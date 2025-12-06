import type { PlayerShootingRecord } from "@/types/game_data";

// constants.ts 같은 데 빼도 됨
const COURT_W = 726;
const COURT_H = 412;

export type TeamLabel = "Home" | "Away";

export type ShotPoint = {
  x: number;
  y: number;
  made: boolean;
  team: TeamLabel;
  quarter: string;
};

export const convertShootingResponse = (data: PlayerShootingRecord[], h_code: string, a_code: string): ShotPoint[] => {
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
      // 혹시 코드가 안 맞는 기록은 일단 Away 취급
      targetSide = "Right";
      teamLabel = "Away";
    }

    for (const log of player.logs) {
      const x = Number(log.x ?? 0);
      const y = Number(log.y ?? 0);
      const d = String(log.d ?? "1");
      const made = log.o === "O";
      const q = String(log.q ?? "");

      // Python 코드:
      // if d == '1': norm_x = COURT_W - x; norm_y = COURT_H - y
      // else: norm_x = x; norm_y = y
      let norm_x: number;
      let norm_y: number;
      if (d === "1") {
        norm_x = COURT_W - x;
        norm_y = COURT_H - y;
      } else {
        norm_x = x;
        norm_y = y;
      }

      // if target_side == "Left": final_x, final_y = norm_x, norm_y
      // else: final_x, final_y = COURT_W - norm_x, COURT_H - norm_y
      let final_x: number;
      let final_y: number;
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
