export const COURT = {
  WIDTH: 15, // meters
  HEIGHT: 14, // meters
  SCALE: 45, // pixels per meter
  LANE_WIDTH: 2, // meters (padding on each side)
} as const;

export const SVG = {
  WIDTH: (COURT.WIDTH + COURT.LANE_WIDTH * 2) * COURT.SCALE,
  HEIGHT: (COURT.HEIGHT + COURT.LANE_WIDTH * 2) * COURT.SCALE,
  PADDING: COURT.LANE_WIDTH * COURT.SCALE,
} as const;

export const HOOP = {
  X: 7.5,
  Y: 1.575,
  RIM_RADIUS: 0.225,
} as const;

export const PAINT = {
  WIDTH: 4.9,
  HEIGHT: 5,
} as const;

export const ZONES = {
  RA_RADIUS: 2.9, // Restricted Area
  MID_RANGE_5M: 5.0,
  THREE_PT_ARC: 6.75,
  THREE_PT_SIDE_DIST: 6.6,
} as const;

export const ShotZone = {
  RA: "RA",
  SM_R: "SM_R",
  SM_C: "SM_C",
  SM_L: "SM_L",
  LM_RC: "LM_RC",
  LM_R: "LM_R",
  LM_C: "LM_C",
  LM_L: "LM_L",
  LM_LC: "LM_LC",
  THREE_P_RC: "3P_RC",
  THREE_P_R: "3P_R",
  THREE_P_C: "3P_C",
  THREE_P_L: "3P_L",
  THREE_P_LC: "3P_LC",
};

export const ZONE_CENTERS: Record<string, { x: number; y: number }> = {
  RA: { x: 7.5, y: 2 },
  SM_R: { x: 11.3, y: 2.5 },
  SM_C: { x: 7.5, y: 5.5 },
  SM_L: { x: 3.8, y: 2.5 },
  LM_RC: { x: 13.3, y: 2.0 },
  LM_R: { x: 11.5, y: 6.0 },
  LM_C: { x: 7.5, y: 7.4 },
  LM_L: { x: 3.5, y: 6.0 },
  LM_LC: { x: 1.8, y: 2.0 },
  "3P_RC": { x: 14.6, y: 1.5 },
  "3P_R": { x: 13.3, y: 9.0 },
  "3P_C": { x: 7.5, y: 11 },
  "3P_L": { x: 1.7, y: 9.0 },
  "3P_LC": { x: 0.4, y: 1.5 },
};
