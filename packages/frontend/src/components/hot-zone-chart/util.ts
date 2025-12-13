import { COURT, HOOP, SVG, ShotZone, ZONES } from "./constant";

export const scaleX = (x: number) => x * COURT.SCALE + SVG.PADDING;
export const scaleY = (y: number) => SVG.HEIGHT - y * COURT.SCALE - SVG.PADDING;

const getDistance = (x1: number, y1: number, x2: number, y2: number) =>
  Math.sqrt(Math.pow(x1 - x2, 2) + Math.pow(y1 - y2, 2));

const getAngleDegrees = (x: number, y: number) => {
  const dx = x - HOOP.X;
  const dy = y - HOOP.Y;
  const rad = Math.atan2(dy, dx);
  let deg = (rad * 180) / Math.PI;
  if (deg < -90) deg += 360;
  return deg;
};

export const getPolarPoint = (radius: number, angle: number) => ({
  x: HOOP.X + radius * Math.cos((angle * Math.PI) / 180),
  y: HOOP.Y + radius * Math.sin((angle * Math.PI) / 180),
});

export const intersectTopBoundary = (pt: { x: number; y: number }, angle: number) => {
  if (Math.abs(angle - 90) < 0.01) return { x: pt.x, y: COURT.HEIGHT };
  const rad = (angle * Math.PI) / 180;
  const targetY = COURT.HEIGHT;
  const targetX = pt.x + (targetY - pt.y) / Math.tan(rad);
  return { x: targetX, y: targetY };
};

export const classifyShotZone = (x: number, y: number, breakY: number): (typeof ShotZone)[keyof typeof ShotZone] => {
  const distFromHoop = getDistance(x, y, HOOP.X, HOOP.Y);
  if (distFromHoop <= ZONES.RA_RADIUS) return "RA";

  const isCorner3Width = Math.abs(x - HOOP.X) >= ZONES.THREE_PT_SIDE_DIST;
  const isCorner3 = isCorner3Width && y <= breakY;
  const is3Point = isCorner3 || distFromHoop >= ZONES.THREE_PT_ARC;

  let angle = getAngleDegrees(x, y);
  if (angle < 0) angle += 360;

  if (is3Point) {
    if (isCorner3) return x > HOOP.X ? "3P_RC" : "3P_LC";
    if (angle < 65 || angle > 300) return "3P_R";
    if (angle < 115) return "3P_C";
    return "3P_L";
  }

  if (distFromHoop > ZONES.MID_RANGE_5M) {
    if (angle < 30 || angle > 330) return "LM_RC";
    if (angle < 65) return "LM_R";
    if (angle < 115) return "LM_C";
    if (angle < 150) return "LM_L";
    return "LM_LC";
  }

  if (x > HOOP.X) {
    return angle < 50 || y < HOOP.Y ? "SM_R" : "SM_C";
  }
  return (angle > 130 && angle < 270) || y < HOOP.Y ? "SM_L" : "SM_C";
};

export const getZoneColor = (attempts: number, pct: number) => {
  if (attempts === 0) return "#f5f5f5";

  // RGB 값을 보간하는 헬퍼 함수
  const interpolateColor = (color1: number[], color2: number[], ratio: number) => {
    return color1.map((c1, i) => Math.round(c1 + (color2[i] - c1) * ratio));
  };

  // RGB 배열을 hex 문자열로 변환
  const rgbToHex = (rgb: number[]) => {
    return "#" + rgb.map((c) => c.toString(16).padStart(2, "0")).join("");
  };

  // 색상 포인트 정의 (낮은 성공률: 파랑 -> 높은 성공률: 빨강)
  const colorStops = [
    { pct: 0, rgb: [20, 100, 255] }, // 진한 파랑
    { pct: 30, rgb: [227, 242, 253] }, // 연한 파랑
    { pct: 40, rgb: [255, 150, 120] }, // 연한 빨강
    { pct: 50, rgb: [239, 83, 80] }, // 중간 빨강
    { pct: 100, rgb: [183, 28, 28] }, // 진한 빨강
  ];

  // pct가 어느 구간에 속하는지 찾기
  for (let i = 0; i < colorStops.length - 1; i++) {
    const start = colorStops[i];
    const end = colorStops[i + 1];

    if (pct >= start.pct && pct <= end.pct) {
      const ratio = (pct - start.pct) / (end.pct - start.pct);
      const interpolated = interpolateColor(start.rgb, end.rgb, ratio);
      return rgbToHex(interpolated);
    }
  }

  // 100% 이상인 경우
  return rgbToHex(colorStops[colorStops.length - 1].rgb);
};
