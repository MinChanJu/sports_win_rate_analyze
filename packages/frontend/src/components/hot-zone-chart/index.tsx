import { type ShotPoint, convertShootingResponse } from "../shooting-chart/util";
import { COURT, HOOP, PAINT, SVG, ShotZone, ZONES, ZONE_CENTERS } from "./constant";
import { classifyShotZone, getPolarPoint, getZoneColor, intersectTopBoundary, scaleX, scaleY } from "./util";

import { useMemo } from "react";

import { COURT_H, COURT_W, FLOOR_H, FLOOR_W } from "@/constants/court";
import type { GameData } from "@/types/game";

interface HotZoneChartProps {
  gameData: GameData;
  team: "Home" | "Away";
  ratio?: number;
}

const HotZoneChart = ({ gameData, team, ratio = 0.7 }: HotZoneChartProps) => {
  const filteredShots: ShotPoint[] = useMemo(() => {
    const allShots = convertShootingResponse(gameData.shooting_records, gameData.game_info.home.code);
    return allShots.filter((shot) => shot.team === team);
  }, [gameData, team]);

  // Calculate zone geometry
  const breakYDelta = Math.sqrt(Math.pow(ZONES.THREE_PT_ARC, 2) - Math.pow(ZONES.THREE_PT_SIDE_DIST, 2));
  const breakY = HOOP.Y + breakYDelta;

  const breakAngleDeg = Math.acos(ZONES.THREE_PT_SIDE_DIST / ZONES.THREE_PT_ARC) * (180 / Math.PI);
  const baseAngle5m = Math.asin(-HOOP.Y / ZONES.MID_RANGE_5M) * (180 / Math.PI);

  // Calculate statistics for each zone
  const zoneStats = useMemo(() => {
    const stats: Record<string, { attempts: number; made: number; pct: number }> = {};
    Object.values(ShotZone).forEach((z) => (stats[z] = { attempts: 0, made: 0, pct: 0 }));

    filteredShots.forEach((log) => {
      let px = log.x;
      let py = log.y;

      // Fold to half court
      if (px > COURT_W / 2) {
        px = COURT_W - px;
        py = COURT_H - py;
      }

      // Convert pixels to meters
      const meterX = (py / COURT_H) * FLOOR_H - COURT.LANE_WIDTH;
      const meterY = (px / COURT_W) * FLOOR_W - COURT.LANE_WIDTH;

      const zoneID = classifyShotZone(meterX, meterY, breakY);
      if (stats[zoneID]) {
        stats[zoneID].attempts += 1;
        if (log.made) stats[zoneID].made += 1;
      }
    });

    Object.keys(stats).forEach((z) => {
      if (stats[z].attempts > 0) {
        stats[z].pct = Math.round((stats[z].made / stats[z].attempts) * 100);
      }
    });
    return stats;
  }, [filteredShots, breakY]);

  // Generate SVG paths for each zone
  const zonePaths = useMemo(() => {
    const paths: Record<string, string> = {};
    const svgM = (pt: { x: number; y: number }) => `M ${scaleX(pt.x)} ${scaleY(pt.y)}`;
    const svgL = (pt: { x: number; y: number }) => `L ${scaleX(pt.x)} ${scaleY(pt.y)}`;
    const svgA = (r: number, pt: { x: number; y: number }, sweep: 0 | 1) =>
      `A ${r * COURT.SCALE} ${r * COURT.SCALE} 0 0 ${sweep} ${scaleX(pt.x)} ${scaleY(pt.y)}`;

    const getArcPoints = (r: number, startAng: number, endAng: number, step = 2) => {
      let path = "";
      const total = Math.abs(endAng - startAng);
      const count = Math.ceil(total / step);
      const angStep = (endAng - startAng) / count;
      for (let i = 0; i <= count; i++) {
        const ang = startAng + i * angStep;
        const p = getPolarPoint(r, ang);
        path += ` L ${scaleX(p.x)} ${scaleY(p.y)}`;
      }
      return path;
    };

    const getDonutPath = (rIn: number, rOut: number, start: number, end: number) => {
      const p1 = getPolarPoint(rIn, start);
      const p2 = getPolarPoint(rOut, start);
      const p3 = getPolarPoint(rOut, end);
      const p4 = getPolarPoint(rIn, end);
      return [svgM(p1), svgL(p2), svgA(rOut, p3, 0), svgL(p4), svgA(rIn, p1, 1), `Z`].join(" ");
    };

    const raBaseDx = Math.sqrt(Math.pow(ZONES.RA_RADIUS, 2) - Math.pow(HOOP.Y, 2));
    const raBaseAngle = Math.asin(-HOOP.Y / ZONES.RA_RADIUS) * (180 / Math.PI);
    const midBaseDx = Math.sqrt(Math.pow(ZONES.MID_RANGE_5M, 2) - Math.pow(HOOP.Y, 2));

    // Restricted Area
    paths["RA"] = [
      svgM({ x: HOOP.X + raBaseDx, y: 0 }),
      getArcPoints(ZONES.RA_RADIUS, raBaseAngle, 180 - raBaseAngle),
      svgL({ x: HOOP.X - raBaseDx, y: 0 }),
      `Z`,
    ].join(" ");

    // Short Mid-Range
    paths["SM_R"] = [
      svgM({ x: HOOP.X + raBaseDx, y: 0 }),
      svgL({ x: HOOP.X + midBaseDx, y: 0 }),
      getArcPoints(ZONES.MID_RANGE_5M, baseAngle5m, 50),
      svgL(getPolarPoint(ZONES.RA_RADIUS, 50)),
      getArcPoints(ZONES.RA_RADIUS, 50, raBaseAngle),
      `Z`,
    ].join(" ");
    paths["SM_C"] = getDonutPath(ZONES.RA_RADIUS, ZONES.MID_RANGE_5M, 50, 130);
    paths["SM_L"] = [
      svgM(getPolarPoint(ZONES.RA_RADIUS, 130)),
      getArcPoints(ZONES.MID_RANGE_5M, 130, 180 - baseAngle5m),
      svgL({ x: HOOP.X - midBaseDx, y: 0 }),
      svgL({ x: HOOP.X - raBaseDx, y: 0 }),
      getArcPoints(ZONES.RA_RADIUS, 180 - raBaseAngle, 130),
      `Z`,
    ].join(" ");

    // Long Mid-Range
    paths["LM_RC"] = [
      svgM({ x: HOOP.X + midBaseDx, y: 0 }),
      svgL({ x: HOOP.X + ZONES.THREE_PT_SIDE_DIST, y: 0 }),
      svgL({ x: HOOP.X + ZONES.THREE_PT_SIDE_DIST, y: breakY }),
      getArcPoints(ZONES.THREE_PT_ARC, breakAngleDeg, 30),
      svgL(getPolarPoint(ZONES.MID_RANGE_5M, 30)),
      getArcPoints(ZONES.MID_RANGE_5M, 30, baseAngle5m),
      `Z`,
    ].join(" ");
    paths["LM_LC"] = [
      svgM(getPolarPoint(ZONES.MID_RANGE_5M, 150)),
      getArcPoints(ZONES.THREE_PT_ARC, 150, 180 - breakAngleDeg),
      svgL({ x: HOOP.X - ZONES.THREE_PT_SIDE_DIST, y: breakY }),
      svgL({ x: HOOP.X - ZONES.THREE_PT_SIDE_DIST, y: 0 }),
      svgL({ x: HOOP.X - midBaseDx, y: 0 }),
      getArcPoints(ZONES.MID_RANGE_5M, 180 - baseAngle5m, 150),
      `Z`,
    ].join(" ");
    paths["LM_R"] = getDonutPath(ZONES.MID_RANGE_5M, ZONES.THREE_PT_ARC, 30, 65);
    paths["LM_C"] = getDonutPath(ZONES.MID_RANGE_5M, ZONES.THREE_PT_ARC, 65, 115);
    paths["LM_L"] = getDonutPath(ZONES.MID_RANGE_5M, ZONES.THREE_PT_ARC, 115, 150);

    // Three-Point
    paths["3P_RC"] = [
      svgM({ x: HOOP.X + ZONES.THREE_PT_SIDE_DIST, y: 0 }),
      svgL({ x: COURT.WIDTH, y: 0 }),
      svgL({ x: COURT.WIDTH, y: breakY }),
      svgL({ x: HOOP.X + ZONES.THREE_PT_SIDE_DIST, y: breakY }),
      `Z`,
    ].join(" ");
    paths["3P_LC"] = [
      svgM({ x: HOOP.X - ZONES.THREE_PT_SIDE_DIST, y: 0 }),
      svgL({ x: 0, y: 0 }),
      svgL({ x: 0, y: breakY }),
      svgL({ x: HOOP.X - ZONES.THREE_PT_SIDE_DIST, y: breakY }),
      `Z`,
    ].join(" ");
    paths["3P_R"] = [
      svgM({ x: HOOP.X + ZONES.THREE_PT_SIDE_DIST, y: breakY }),
      `L ${scaleX(COURT.WIDTH)} ${scaleY(breakY)}`,
      `L ${scaleX(COURT.WIDTH)} ${scaleY(COURT.HEIGHT)}`,
      svgL(intersectTopBoundary(getPolarPoint(ZONES.THREE_PT_ARC, 65), 65)),
      svgL(getPolarPoint(ZONES.THREE_PT_ARC, 65)),
      getArcPoints(ZONES.THREE_PT_ARC, 65, breakAngleDeg),
      `Z`,
    ].join(" ");
    paths["3P_C"] = [
      svgM(getPolarPoint(ZONES.THREE_PT_ARC, 65)),
      svgL(intersectTopBoundary(getPolarPoint(ZONES.THREE_PT_ARC, 65), 65)),
      svgL(intersectTopBoundary(getPolarPoint(ZONES.THREE_PT_ARC, 115), 115)),
      svgL(getPolarPoint(ZONES.THREE_PT_ARC, 115)),
      getArcPoints(ZONES.THREE_PT_ARC, 115, 65),
      `Z`,
    ].join(" ");
    paths["3P_L"] = [
      svgM(getPolarPoint(ZONES.THREE_PT_ARC, 115)),
      svgL(intersectTopBoundary(getPolarPoint(ZONES.THREE_PT_ARC, 115), 115)),
      `L ${scaleX(0)} ${scaleY(COURT.HEIGHT)}`,
      `L ${scaleX(0)} ${scaleY(breakY)}`,
      svgL({ x: HOOP.X - ZONES.THREE_PT_SIDE_DIST, y: breakY }),
      getArcPoints(ZONES.THREE_PT_ARC, 180 - breakAngleDeg, 115),
      `Z`,
    ].join(" ");

    return paths;
  }, [breakY, breakAngleDeg, baseAngle5m]);

  return (
    <div>
      <div className="mb-2 text-center text-lg">Hot Zone Chart - {team} Team</div>
      <svg
        width={SVG.WIDTH * ratio}
        height={SVG.HEIGHT * ratio}
        viewBox={`0 0 ${SVG.WIDTH} ${SVG.HEIGHT}`}
        style={{ backgroundColor: "#f0f0f0" }}
      >
        {Object.entries(zonePaths).map(([zoneID, path]) => {
          const stat = zoneStats[zoneID];
          const color = getZoneColor(stat.attempts, stat.pct);
          return <path key={zoneID} d={path} fill={color} stroke="none" />;
        })}

        <g stroke="black" strokeWidth="2" fill="none" style={{ pointerEvents: "none" }}>
          {Object.values(zonePaths).map((d, i) => (
            <path key={i} d={d} />
          ))}
        </g>

        <g strokeWidth="2" fill="none" style={{ pointerEvents: "none" }}>
          <rect
            stroke="orange"
            strokeWidth="2"
            x={scaleX(HOOP.X - PAINT.WIDTH / 2)}
            y={scaleY(PAINT.HEIGHT)}
            width={scaleX(PAINT.WIDTH) - scaleX(0)}
            height={scaleY(0) - scaleY(PAINT.HEIGHT)}
          />
          <line
            stroke="black"
            strokeWidth="2"
            x1={scaleX(HOOP.X - PAINT.WIDTH)}
            y1={scaleY(0)}
            x2={scaleX(HOOP.X + PAINT.WIDTH)}
            y2={scaleY(0)}
          />
          <path
            stroke="orange"
            strokeWidth="2"
            d={`
              M ${scaleX(HOOP.X - 1.8)} ${scaleY(PAINT.HEIGHT)}
              A ${1.8 * COURT.SCALE} ${1.8 * COURT.SCALE} 0 0 1 ${scaleX(HOOP.X + 1.8)} ${scaleY(PAINT.HEIGHT)}
            `}
          />
        </g>

        <line
          x1={scaleX(HOOP.X - 1)}
          y1={scaleY(HOOP.BACK)}
          x2={scaleX(HOOP.X + 1)}
          y2={scaleY(HOOP.BACK)}
          stroke="black"
          strokeWidth="2"
        />
        <circle
          cx={scaleX(HOOP.X)}
          cy={scaleY(HOOP.Y)}
          r={HOOP.RIM_RADIUS * COURT.SCALE}
          stroke="orange"
          strokeWidth="2"
          fill="none"
        />
        <line
          x1={scaleX(HOOP.X)}
          y1={scaleY(HOOP.BACK)}
          x2={scaleX(HOOP.X)}
          y2={scaleY(HOOP.Y - HOOP.RIM_RADIUS)}
          stroke="black"
          strokeWidth="2"
        />

        {Object.entries(ZONE_CENTERS).map(([zoneID, pos]) => {
          const stat = zoneStats[zoneID];
          return (
            <text
              key={`txt-${zoneID}`}
              x={scaleX(pos.x)}
              y={scaleY(pos.y)}
              textAnchor="middle"
              dominantBaseline="central"
              fontSize="18"
              fontWeight="bold"
              fill="black"
              stroke="white"
              strokeWidth="3"
              paintOrder="stroke"
              style={{ pointerEvents: "none" }}
            >
              {`${stat.pct}%`}
            </text>
          );
        })}
      </svg>
    </div>
  );
};

export default HotZoneChart;
