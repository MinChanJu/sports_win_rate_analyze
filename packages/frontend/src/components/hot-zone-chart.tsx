import type { ShotPoint, TeamLabel } from "./shooting-chart/util";

import React, { useEffect, useMemo, useState } from "react";

import type { GameData, PlayerShootingRecord } from "@/types/game";

// ---------------------------------------------------------
// [2] 데이터 변환 로직 (제공해주신 convertShootingResponse)
// ---------------------------------------------------------
const COURT_W = 726; // Full Court Width (Pixel)
const COURT_H = 412; // Full Court Height (Pixel)

const convertShootingResponse = (data: PlayerShootingRecord[], h_code: string, a_code: string): ShotPoint[] => {
  const shots: ShotPoint[] = [];

  for (const player of data) {
    const tcode = player.tcode.trim();
    let targetSide: "Left" | "Right";
    let teamLabel: TeamLabel;

    if (tcode === h_code.trim()) {
      targetSide = "Left";
      teamLabel = "Home";
    } else if (tcode === a_code.trim()) {
      targetSide = "Right";
      teamLabel = "Away";
    } else {
      targetSide = "Right";
      teamLabel = "Away";
    }

    for (const log of player.logs) {
      const x = Number(log.x ?? 0);
      const y = Number(log.y ?? 0);
      const d = String(log.d ?? "1");
      const made = log.o === "O" || String(log.o).includes("성공") || String(log.o) === "1";
      const q = String(log.q ?? "");

      let norm_x: number, norm_y: number;
      if (d === "1") {
        norm_x = COURT_W - x;
        norm_y = COURT_H - y;
      } else {
        norm_x = x;
        norm_y = y;
      }

      let final_x: number, final_y: number;
      if (targetSide === "Left") {
        final_x = norm_x;
        final_y = norm_y;
      } else {
        final_x = COURT_W - norm_x;
        final_y = COURT_H - norm_y;
      }

      shots.push({
        x: final_x,
        y: final_y,
        made,
        team: teamLabel,
        quarter: q,
      });
    }
  }
  return shots;
};

// ---------------------------------------------------------
// [3] 핫존 설정값 (상수)
// ---------------------------------------------------------
// HotZone Coordinate System: X(Width: 15m), Y(Length: 14m)
const C_WIDTH = 15;
const C_HEIGHT = 14;
const SCALE = 45;
const PAD = 20;

const SVG_W = C_WIDTH * SCALE + PAD * 2;
const SVG_H = C_HEIGHT * SCALE + PAD * 2;

const HOOP_X = 7.5;
const HOOP_Y = 1.575;
const R_RIM = 0.225;

const W_PAINT = 4.9;
const H_PAINT = 5.5;

const RA_RADIUS = 2.9;
const R_MID_5M = 5.0;
const R_3PT_ARC = 6.75;
const R_3PT_SIDE_DIST = 6.6;

// ---------------------------------------------------------
// [4] 헬퍼 함수 (좌표 변환 및 기하학)
// ---------------------------------------------------------
const sX = (x: number) => x * SCALE + PAD;
const sY = (y: number) => SVG_H - y * SCALE - PAD;

const getDist = (x1: number, y1: number, x2: number, y2: number) =>
  Math.sqrt(Math.pow(x1 - x2, 2) + Math.pow(y1 - y2, 2));

const getAngleDeg = (x: number, y: number) => {
  const dx = x - HOOP_X;
  const dy = y - HOOP_Y;
  const rad = Math.atan2(dy, dx);
  let deg = (rad * 180) / Math.PI;
  if (deg < -90) deg += 360;
  return deg;
};

const getPt = (r: number, ang: number) => ({
  x: HOOP_X + r * Math.cos((ang * Math.PI) / 180),
  y: HOOP_Y + r * Math.sin((ang * Math.PI) / 180),
});

const intersectTop = (pt: { x: number; y: number }, ang: number) => {
  if (Math.abs(ang - 90) < 0.01) return { x: pt.x, y: C_HEIGHT };
  const rad = (ang * Math.PI) / 180;
  const targetY = C_HEIGHT;
  const targetX = pt.x + (targetY - pt.y) / Math.tan(rad);
  return { x: targetX, y: targetY };
};

// ---------------------------------------------------------
// [5] 구역 분류 로직
// ---------------------------------------------------------
const classifyShotZone = (x: number, y: number, breakY: number): string => {
  const distFromHoop = getDist(x, y, HOOP_X, HOOP_Y);
  if (distFromHoop <= RA_RADIUS) return "RA";

  const isCorner3Width = Math.abs(x - HOOP_X) >= R_3PT_SIDE_DIST;
  let is3Point = false;
  let isCorner3 = false;

  if (isCorner3Width && y <= breakY) {
    is3Point = true;
    isCorner3 = true;
  } else if (distFromHoop >= R_3PT_ARC) {
    is3Point = true;
  }

  let angle = getAngleDeg(x, y);
  if (angle < 0) angle += 360;

  if (is3Point) {
    if (isCorner3) return x > HOOP_X ? "3P_RC" : "3P_LC";
    if (angle < 65 || angle > 300) return "3P_R";
    if (angle < 115) return "3P_C";
    return "3P_L";
  }

  if (distFromHoop > R_MID_5M) {
    if (angle < 30 || angle > 330) return "LM_RC";
    if (angle < 65) return "LM_R";
    if (angle < 115) return "LM_C";
    if (angle < 150) return "LM_L";
    return "LM_LC";
  } else {
    if (x > HOOP_X) {
      if (angle < 50 || y < HOOP_Y) return "SM_R";
      return "SM_C";
    } else {
      if ((angle > 130 && angle < 270) || y < HOOP_Y) return "SM_L";
      return "SM_C";
    }
  }
};

const getZoneColor = (attempts: number, pct: number) => {
  if (attempts === 0) return "#f5f5f5";
  if (pct < 20) return "#90caf9";
  if (pct < 35) return "#e3f2fd";
  if (pct < 45) return "#ffccbc";
  if (pct < 60) return "#ef5350";
  return "#b71c1c";
};

// ---------------------------------------------------------
// [6] 메인 컴포넌트
// ---------------------------------------------------------
interface Props {
  gameData: GameData;
}

const HotZoneChart: React.FC<Props> = ({ gameData }) => {
  // 1. 데이터 추출 및 필터 상태 관리
  const { code: h_code, name: home_name } = gameData.game_info.home;
  const { code: a_code, name: away_name } = gameData.game_info.away;
  const shootingLogs = gameData.shooting_records;

  // 1-1. 전체 샷 데이터 변환 (convertShootingResponse 사용)
  const allShots: ShotPoint[] = useMemo(() => {
    if (!shootingLogs) return [];
    return convertShootingResponse(shootingLogs, String(h_code), String(a_code));
  }, [shootingLogs, h_code, a_code]);

  // 1-2. 필터 상태
  const allQuarters = useMemo(() => Array.from(new Set(allShots.map((s) => s.quarter))).sort(), [allShots]);
  const [activeQuarters, setActiveQuarters] = useState<string[]>([]);
  const [showHome, setShowHome] = useState(true);
  const [showAway, setShowAway] = useState(true);
  const [showMade, setShowMade] = useState(true);
  const [showMiss, setShowMiss] = useState(true);

  useEffect(() => {
    setActiveQuarters(allQuarters);
  }, [allQuarters]); // 쿼터 목록 변경 시 전체 선택

  // 1-3. 필터링된 샷
  const filteredShots = useMemo(
    () =>
      allShots.filter((s) => {
        if (!activeQuarters.includes(s.quarter)) return false;
        if (s.team === "Home" && !showHome) return false;
        if (s.team === "Away" && !showAway) return false;
        if (s.made && !showMade) return false;
        if (!s.made && !showMiss) return false;
        return true;
      }),
    [allShots, activeQuarters, showHome, showAway, showMade, showMiss],
  );

  // 2. 핫존 계산 로직
  const breakYDelta = Math.sqrt(Math.pow(R_3PT_ARC, 2) - Math.pow(R_3PT_SIDE_DIST, 2));
  const breakY = HOOP_Y + breakYDelta;
  const breakAngleDeg = Math.acos(R_3PT_SIDE_DIST / R_3PT_ARC) * (180 / Math.PI);
  const baseAngle5m = Math.asin(-HOOP_Y / R_MID_5M) * (180 / Math.PI);

  const zoneStats = useMemo(() => {
    const stats: Record<string, { attempts: number; made: number; pct: number }> = {};
    const allZones = [
      "RA",
      "SM_R",
      "SM_C",
      "SM_L",
      "LM_RC",
      "LM_R",
      "LM_C",
      "LM_L",
      "LM_LC",
      "3P_RC",
      "3P_R",
      "3P_C",
      "3P_L",
      "3P_LC",
    ];
    allZones.forEach((z) => (stats[z] = { attempts: 0, made: 0, pct: 0 }));

    filteredShots.forEach((log) => {
      // ★ 좌표 변환 (Full Court Pixels -> Half Court Meters)
      // 1. Full Court Pixel 좌표
      let px = log.x;
      let py = log.y;

      // 2. 반코트로 접기 (Folding)
      // KBL Full Court: 726px wide. Middle is 363.
      // If x > 363 (Right Side), we assume it's the other team's offense or second half.
      // We mirror it to the Left side to overlay all stats on one hoop.
      if (px > COURT_W / 2) {
        px = COURT_W - px;
        py = COURT_H - py;
      }

      // 3. Pixel to Meter Scaling
      // KBL Data: x is Length (Baseline to Center), y is Width (Sideline to Sideline).
      // HotZone: x is Width (0-15), y is Length (0-14).
      // Mapping:
      // Input Y (0~412) -> HotZone X (0~15)
      // Input X (0~363) -> HotZone Y (0~14)

      // Y축 뒤집기 고려 (svg 좌표계 vs 데이터 좌표계 확인 필요)
      // 보통 데이터의 (0,0)은 코트 모서리.
      // 핫존의 X (Width)는 데이터의 Y (412)에 해당.
      const meterX = (py / COURT_H) * 15; // 0 ~ 15
      const meterY = (px / (COURT_W / 2)) * 14; // 0 ~ 14

      // 4. 구역 분류
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

  // -------------------------------------------------------
  // [Path 생성 (SVG)] - 이전 코드와 동일
  // -------------------------------------------------------
  const svgM = (pt: { x: number; y: number }) => `M ${sX(pt.x)} ${sY(pt.y)}`;
  const svgL = (pt: { x: number; y: number }) => `L ${sX(pt.x)} ${sY(pt.y)}`;
  const svgA = (r: number, pt: { x: number; y: number }, sweep: 0 | 1) =>
    `A ${r * SCALE} ${r * SCALE} 0 0 ${sweep} ${sX(pt.x)} ${sY(pt.y)}`;

  const getArcPoints = (r: number, startAng: number, endAng: number, step = 2) => {
    let path = "";
    const total = Math.abs(endAng - startAng);
    const count = Math.ceil(total / step);
    const angStep = (endAng - startAng) / count;
    for (let i = 0; i <= count; i++) {
      const ang = startAng + i * angStep;
      const p = getPt(r, ang);
      path += ` L ${sX(p.x)} ${sY(p.y)}`;
    }
    return path;
  };

  const zonePaths: Record<string, string> = {};
  const raBaseDx = Math.sqrt(Math.pow(RA_RADIUS, 2) - Math.pow(HOOP_Y, 2));
  zonePaths["RA"] = [
    svgM({ x: HOOP_X + raBaseDx, y: 0 }),
    getArcPoints(
      RA_RADIUS,
      Math.asin(-HOOP_Y / RA_RADIUS) * (180 / Math.PI),
      180 - Math.asin(-HOOP_Y / RA_RADIUS) * (180 / Math.PI),
    ),
    svgL({ x: HOOP_X - raBaseDx, y: 0 }),
    `Z`,
  ].join(" ");

  const getDonutPath = (rIn: number, rOut: number, start: number, end: number) => {
    const p1 = getPt(rIn, start);
    const p2 = getPt(rOut, start);
    const p3 = getPt(rOut, end);
    const p4 = getPt(rIn, end);
    return [svgM(p1), svgL(p2), svgA(rOut, p3, 0), svgL(p4), svgA(rIn, p1, 1), `Z`].join(" ");
  };
  const midBaseDx = Math.sqrt(Math.pow(R_MID_5M, 2) - Math.pow(HOOP_Y, 2));
  const midBaseRightX = HOOP_X + midBaseDx;
  const midBaseLeftX = HOOP_X - midBaseDx;

  zonePaths["SM_R"] = [
    svgM({ x: HOOP_X + raBaseDx, y: 0 }),
    svgL({ x: midBaseRightX, y: 0 }),
    getArcPoints(R_MID_5M, baseAngle5m, 50),
    svgL(getPt(RA_RADIUS, 50)),
    getArcPoints(RA_RADIUS, 50, Math.asin(-HOOP_Y / RA_RADIUS) * (180 / Math.PI)),
    `Z`,
  ].join(" ");
  zonePaths["SM_C"] = getDonutPath(RA_RADIUS, R_MID_5M, 50, 130);
  zonePaths["SM_L"] = [
    svgM(getPt(RA_RADIUS, 130)),
    getArcPoints(R_MID_5M, 130, 180 - baseAngle5m),
    svgL({ x: midBaseLeftX, y: 0 }),
    svgL({ x: HOOP_X - raBaseDx, y: 0 }),
    getArcPoints(RA_RADIUS, 180 - Math.asin(-HOOP_Y / RA_RADIUS) * (180 / Math.PI), 130),
    `Z`,
  ].join(" ");

  zonePaths["LM_RC"] = [
    svgM({ x: midBaseRightX, y: 0 }),
    svgL({ x: HOOP_X + R_3PT_SIDE_DIST, y: 0 }),
    svgL({ x: HOOP_X + R_3PT_SIDE_DIST, y: breakY }),
    getArcPoints(R_3PT_ARC, breakAngleDeg, 30),
    svgL(getPt(R_MID_5M, 30)),
    getArcPoints(R_MID_5M, 30, baseAngle5m),
    `Z`,
  ].join(" ");
  zonePaths["LM_LC"] = [
    svgM(getPt(R_MID_5M, 150)),
    getArcPoints(R_3PT_ARC, 150, 180 - breakAngleDeg),
    svgL({ x: HOOP_X - R_3PT_SIDE_DIST, y: breakY }),
    svgL({ x: HOOP_X - R_3PT_SIDE_DIST, y: 0 }),
    svgL({ x: midBaseLeftX, y: 0 }),
    getArcPoints(R_MID_5M, 180 - baseAngle5m, 150),
    `Z`,
  ].join(" ");
  zonePaths["LM_R"] = getDonutPath(R_MID_5M, R_3PT_ARC, 30, 65);
  zonePaths["LM_C"] = getDonutPath(R_MID_5M, R_3PT_ARC, 65, 115);
  zonePaths["LM_L"] = getDonutPath(R_MID_5M, R_3PT_ARC, 115, 150);

  zonePaths["3P_RC"] = [
    svgM({ x: HOOP_X + R_3PT_SIDE_DIST, y: 0 }),
    svgL({ x: 15, y: 0 }),
    svgL({ x: 15, y: breakY }),
    svgL({ x: HOOP_X + R_3PT_SIDE_DIST, y: breakY }),
    `Z`,
  ].join(" ");
  zonePaths["3P_LC"] = [
    svgM({ x: HOOP_X - R_3PT_SIDE_DIST, y: 0 }),
    svgL({ x: 0, y: 0 }),
    svgL({ x: 0, y: breakY }),
    svgL({ x: HOOP_X - R_3PT_SIDE_DIST, y: breakY }),
    `Z`,
  ].join(" ");

  const p3PR_Start = { x: HOOP_X + R_3PT_SIDE_DIST, y: breakY };
  const p3PR_End = getPt(R_3PT_ARC, 65);
  const p3PR_OutEnd = intersectTop(p3PR_End, 65);
  zonePaths["3P_R"] = [
    svgM(p3PR_Start),
    `L ${sX(15)} ${sY(breakY)}`,
    `L ${sX(15)} ${sY(C_HEIGHT)}`,
    svgL(p3PR_OutEnd),
    svgL(p3PR_End),
    getArcPoints(R_3PT_ARC, 65, breakAngleDeg),
    `Z`,
  ].join(" ");
  zonePaths["3P_C"] = [
    svgM(getPt(R_3PT_ARC, 65)),
    svgL(intersectTop(getPt(R_3PT_ARC, 65), 65)),
    svgL(intersectTop(getPt(R_3PT_ARC, 115), 115)),
    svgL(getPt(R_3PT_ARC, 115)),
    getArcPoints(R_3PT_ARC, 115, 65),
    `Z`,
  ].join(" ");

  const p3PL_Start = getPt(R_3PT_ARC, 115);
  const p3PL_OutStart = intersectTop(p3PL_Start, 115);
  const p3PL_End = { x: HOOP_X - R_3PT_SIDE_DIST, y: breakY };
  zonePaths["3P_L"] = [
    svgM(p3PL_Start),
    svgL(p3PL_OutStart),
    `L ${sX(0)} ${sY(C_HEIGHT)}`,
    `L ${sX(0)} ${sY(breakY)}`,
    svgL(p3PL_End),
    getArcPoints(R_3PT_ARC, 180 - breakAngleDeg, 115),
    `Z`,
  ].join(" ");

  const ZONE_CENTERS: Record<string, { x: number; y: number }> = {
    RA: { x: 7.5, y: 1.2 },
    SM_R: { x: 10.5, y: 2.5 },
    SM_C: { x: 7.5, y: 4.2 },
    SM_L: { x: 4.5, y: 2.5 },
    LM_RC: { x: 12.5, y: 2.0 },
    LM_R: { x: 11.0, y: 6.0 },
    LM_C: { x: 7.5, y: 6.8 },
    LM_L: { x: 4.0, y: 6.0 },
    LM_LC: { x: 2.5, y: 2.0 },
    "3P_RC": { x: 14.2, y: 1.0 },
    "3P_R": { x: 12.0, y: 9.0 },
    "3P_C": { x: 7.5, y: 9.5 },
    "3P_L": { x: 3.0, y: 9.0 },
    "3P_LC": { x: 0.8, y: 1.0 },
  };

  const toggleQuarter = (q: string) => {
    setActiveQuarters((prev) => (prev.includes(q) ? prev.filter((v) => v !== q) : [...prev, q]));
  };

  return (
    <div className="flex flex-col items-center">
      {/* ---------------- 컨트롤 패널 (필터) ---------------- */}
      <div className="mb-4 flex w-full justify-center gap-6 rounded-lg bg-gray-50 p-4 text-sm">
        {/* 쿼터 필터 */}
        <div className="flex flex-col">
          <span className="mb-1 font-bold">Quarter</span>
          <div className="flex gap-2">
            {allQuarters.map((q) => (
              <label key={q} className="flex cursor-pointer items-center">
                <input
                  type="checkbox"
                  className="mr-1"
                  checked={activeQuarters.includes(q)}
                  onChange={() => toggleQuarter(q)}
                />
                {q}
              </label>
            ))}
          </div>
        </div>

        {/* 팀 필터 */}
        <div className="flex flex-col">
          <span className="mb-1 font-bold">Team</span>
          <div className="flex gap-3">
            <label className="flex cursor-pointer items-center">
              <input type="checkbox" className="mr-1" checked={showHome} onChange={() => setShowHome(!showHome)} />
              Home ({home_name})
            </label>
            <label className="flex cursor-pointer items-center">
              <input type="checkbox" className="mr-1" checked={showAway} onChange={() => setShowAway(!showAway)} />
              Away ({away_name})
            </label>
          </div>
        </div>

        {/* 결과 필터 */}
        <div className="flex flex-col">
          <span className="mb-1 font-bold">Result</span>
          <div className="flex gap-3">
            <label className="flex cursor-pointer items-center">
              <input type="checkbox" className="mr-1" checked={showMade} onChange={() => setShowMade(!showMade)} />
              Made
            </label>
            <label className="flex cursor-pointer items-center">
              <input type="checkbox" className="mr-1" checked={showMiss} onChange={() => setShowMiss(!showMiss)} />
              Missed
            </label>
          </div>
        </div>
      </div>

      {/* ---------------- SVG 차트 ---------------- */}
      <svg
        width={SVG_W}
        height={SVG_H}
        viewBox={`0 0 ${SVG_W} ${SVG_H}`}
        style={{ backgroundColor: "white", border: "1px solid #ddd" }}
      >
        {/* Zones Fill */}
        {Object.keys(zonePaths).map((zoneID) => {
          const stat = zoneStats[zoneID];
          const color = getZoneColor(stat.attempts, stat.pct);
          return <path key={zoneID} d={zonePaths[zoneID]} fill={color} stroke="none" />;
        })}

        {/* Lines */}
        <g stroke="black" strokeWidth="2" fill="none" style={{ pointerEvents: "none" }}>
          <rect x={sX(0)} y={sY(C_HEIGHT)} width={sX(C_WIDTH) - sX(0)} height={sY(C_HEIGHT) - sY(0)} strokeWidth="3" />
          {Object.values(zonePaths).map((d, i) => (
            <path key={i} d={d} />
          ))}
        </g>

        {/* White Design Lines */}
        <g stroke="white" strokeWidth="6" fill="none" style={{ pointerEvents: "none" }}>
          <path
            d={`M ${sX(HOOP_X + R_3PT_SIDE_DIST)} ${sY(0)} L ${sX(HOOP_X + R_3PT_SIDE_DIST)} ${sY(breakY)} A ${R_3PT_ARC * SCALE} ${R_3PT_ARC * SCALE} 0 0 0 ${sX(HOOP_X - R_3PT_SIDE_DIST)} ${sY(breakY)} L ${sX(HOOP_X - R_3PT_SIDE_DIST)} ${sY(0)}`}
          />
          <rect x={sX(HOOP_X - W_PAINT / 2)} y={sY(H_PAINT)} width={sX(W_PAINT) - sX(0)} height={sY(0) - sY(H_PAINT)} />
          <circle cx={sX(HOOP_X)} cy={sY(H_PAINT)} r={sX(W_PAINT / 2) - sX(0)} />
        </g>

        {/* Hoop */}
        <line x1={sX(HOOP_X - 0.9)} y1={sY(1.2)} x2={sX(HOOP_X + 0.9)} y2={sY(1.2)} stroke="black" strokeWidth="4" />
        <circle cx={sX(HOOP_X)} cy={sY(HOOP_Y)} r={R_RIM * SCALE * 2} stroke="orange" strokeWidth="3" fill="none" />
        <line x1={sX(HOOP_X)} y1={sY(1.2)} x2={sX(HOOP_X)} y2={sY(HOOP_Y - R_RIM)} stroke="orange" strokeWidth="3" />

        {/* Text Stats */}
        {Object.entries(ZONE_CENTERS).map(([zoneID, pos]) => {
          const stat = zoneStats[zoneID];
          return (
            <text
              key={`txt-${zoneID}`}
              x={sX(pos.x)}
              y={sY(pos.y)}
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
              {stat.attempts > 0 ? `${stat.pct}%` : ""}
            </text>
          );
        })}
      </svg>
    </div>
  );
};

export default HotZoneChart;
