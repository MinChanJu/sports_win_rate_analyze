import { useMemo } from "react";

import type { GameData } from "@/types/game";

// ---------------------------------------------------------
// [Type Definitions]
// ---------------------------------------------------------

type VisualizationShot = {
  id: string;
  x: number;
  y: number;
  isMade: boolean;
  pname: string;
  desc: string;
};

// ---------------------------------------------------------
// [Configuration]
// ---------------------------------------------------------
const C_WIDTH = 15;
const C_HEIGHT = 14;
const SCALE = 45;
const PAD = 50;

const COURT_W = C_WIDTH * SCALE;
const COURT_H = C_HEIGHT * SCALE;
const SVG_W = COURT_W + PAD * 2;
const SVG_H = COURT_H + PAD * 2;

const HOOP_X = 7.5;
const HOOP_Y = 1.575;
const R_3PT = 6.75;
const R_RIM = 0.225;

// ---------------------------------------------------------
// [Helper Functions]
// ---------------------------------------------------------
const sX = (x: number) => x * SCALE + PAD;
const sY = (y: number) => COURT_H - y * SCALE + PAD;

const getPt = (r: number, angDeg: number) => {
  const rad = (angDeg * Math.PI) / 180;
  return {
    x: HOOP_X + r * Math.cos(rad),
    y: HOOP_Y + r * Math.sin(rad),
  };
};

const BasketballHotZone = ({ data }: { data: GameData }) => {
  const correction = { scaleX: 1, scaleY: 1, offsetX: 0, offsetY: 0, flipX: false };

  const shots: VisualizationShot[] = useMemo(() => {
    const processed: VisualizationShot[] = [];
    if (!data.shooting_records) return [];
    data.shooting_records.forEach((record) => {
      record.logs.forEach((log, idx) => {
        const isMade = ["SUCCESS", "Made", "In", "1", "성공", "득점"].some((k) => log.o && log.o.includes(k));
        let rawX = log.x * correction.scaleX;
        const rawY = log.y * correction.scaleY;
        if (correction.flipX) rawX = C_WIDTH - rawX;
        processed.push({
          id: `${record.pcode}-${idx}`,
          x: rawX + correction.offsetX,
          y: rawY + correction.offsetY,
          isMade,
          pname: record.pname,
          desc: log.d,
        });
      });
    });
    return processed;
  }, [
    correction.flipX,
    correction.offsetX,
    correction.offsetY,
    correction.scaleX,
    correction.scaleY,
    data.shooting_records,
  ]);

  // [Geometry: 3점 라인 패스]
  const arcStartX = sX(HOOP_X + R_3PT);
  const arcStartY = sY(HOOP_Y);
  const arcEndX = sX(HOOP_X - R_3PT);
  const arcEndY = sY(HOOP_Y);
  const radiusPx = R_3PT * SCALE;
  const threePointPath = [
    `M ${arcStartX} ${sY(0)} L ${arcStartX} ${arcStartY}`,
    `A ${radiusPx} ${radiusPx} 0 0 0 ${arcEndX} ${arcEndY}`,
    `L ${arcEndX} ${sY(0)}`,
  ].join(" ");

  // [Geometry: STEP 1. 코너 구분선]
  const angleRad = (12 * Math.PI) / 180;
  const cornerLineY_m = HOOP_Y + R_3PT * Math.sin(angleRad);
  const cornerLineX_Right_m = HOOP_X + R_3PT * Math.cos(angleRad);
  const cornerLineX_Left_m = HOOP_X - R_3PT * Math.cos(angleRad);

  // [Geometry: STEP 2. 3점 라인 바깥쪽 구분선]
  const p_start_65 = getPt(R_3PT, 65);
  const p_end_65 = getPt(20, 65); // 20m까지 뻗지만 clipPath에 의해 잘림
  const p_start_115 = getPt(R_3PT, 115);
  const p_end_115 = getPt(20, 115);

  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", padding: "20px" }}>
      <h3>Step 2: Top/Wing Separators (Clipped)</h3>

      <svg
        width={SVG_W}
        height={SVG_H}
        viewBox={`0 0 ${SVG_W} ${SVG_H}`}
        style={{ backgroundColor: "white", border: "1px solid #ccc" }}
      >
        {/* ★ [핵심] 클리핑 마스크 정의: 이 사각형 안쪽만 그리겠다는 선언 */}
        <defs>
          <clipPath id="court-clip">
            <rect
              x={sX(0)}
              y={sY(C_HEIGHT)} // SVG 상에서는 y값이 작은 쪽이 위쪽 (여기선 Top Line)
              width={COURT_W}
              height={COURT_H}
            />
          </clipPath>
        </defs>

        {/* 1. 배경 및 코트 바닥 (여기는 안 잘려도 되므로 밖으로 뺌) */}
        <rect x={sX(0)} y={sY(C_HEIGHT)} width={COURT_W} height={COURT_H} fill="#f9f9f9" />

        {/* 2. 라인 그룹: clipPath 적용 (이 그룹 안의 모든 요소는 코트 밖으로 못 나감) */}
        <g clipPath="url(#court-clip)">
          {/* 기본 외곽선 */}
          <line x1={sX(0)} y1={sY(0)} x2={sX(C_WIDTH)} y2={sY(0)} stroke="black" strokeWidth="3" />
          <rect
            x={sX(HOOP_X - 2.45)}
            y={sY(5.8)}
            width={sX(HOOP_X + 2.45) - sX(HOOP_X - 2.45)}
            height={sY(0) - sY(5.8)}
            fill="none"
            stroke="black"
            strokeWidth="3"
          />

          {/* 3점 라인 */}
          <path d={threePointPath} fill="none" stroke="black" strokeWidth="3" />

          {/* 자유투 라인 */}
          <path
            d={`M ${sX(HOOP_X + 2.45)} ${sY(5.8)} A ${2.45 * SCALE} ${2.45 * SCALE} 0 0 0 ${sX(HOOP_X - 2.45)} ${sY(5.8)}`}
            fill="none"
            stroke="black"
            strokeWidth="2"
            strokeDasharray="5,5"
          />
          <path
            d={`M ${sX(HOOP_X - 2.45)} ${sY(5.8)} A ${2.45 * SCALE} ${2.45 * SCALE} 0 0 0 ${sX(HOOP_X + 2.45)} ${sY(5.8)}`}
            fill="none"
            stroke="black"
            strokeWidth="2"
          />

          {/* [STEP 1. 코너 구분선] */}
          <line
            x1={sX(cornerLineX_Right_m)}
            y1={sY(cornerLineY_m)}
            x2={sX(15)}
            y2={sY(cornerLineY_m)}
            stroke="black"
            strokeWidth="2"
          />
          <line
            x1={sX(cornerLineX_Left_m)}
            y1={sY(cornerLineY_m)}
            x2={sX(0)}
            y2={sY(cornerLineY_m)}
            stroke="black"
            strokeWidth="2"
          />

          {/* [STEP 2. 3점 라인 바깥쪽 구분선] - 이제 20m까지 뻗어도 코트 끝에서 잘림 */}
          <line
            x1={sX(p_start_65.x)}
            y1={sY(p_start_65.y)}
            x2={sX(p_end_65.x)}
            y2={sY(p_end_65.y)}
            stroke="black"
            strokeWidth="2"
          />
          <line
            x1={sX(p_start_115.x)}
            y1={sY(p_start_115.y)}
            x2={sX(p_end_115.x)}
            y2={sY(p_end_115.y)}
            stroke="black"
            strokeWidth="2"
          />
        </g>

        {/* 3. 림 & 백보드 (가장 위에 그려야 하므로 clipPath 밖으로 빼거나 순서 유지) */}
        {/* 보통 백보드는 라인 위에 오므로 여기 배치 */}
        <line x1={sX(HOOP_X - 0.9)} y1={sY(1.2)} x2={sX(HOOP_X + 0.9)} y2={sY(1.2)} stroke="black" strokeWidth="4" />
        <circle cx={sX(HOOP_X)} cy={sY(HOOP_Y)} r={R_RIM * SCALE * 2} stroke="orange" strokeWidth="3" fill="none" />
        <line x1={sX(HOOP_X)} y1={sY(1.2)} x2={sX(HOOP_X)} y2={sY(HOOP_Y - R_RIM)} stroke="orange" strokeWidth="3" />

        {/* 4. 슛 데이터 점 */}
        {shots.map((shot) => (
          <circle
            key={shot.id}
            cx={sX(shot.x)}
            cy={sY(shot.y)}
            r={5}
            fill={shot.isMade ? "rgba(46, 204, 113, 0.7)" : "rgba(231, 76, 60, 0.7)"}
            stroke="#fff"
            strokeWidth={1}
          />
        ))}
      </svg>
    </div>
  );
};

export default BasketballHotZone;
