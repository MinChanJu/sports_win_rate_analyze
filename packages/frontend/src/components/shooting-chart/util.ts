import type { PlayerShootingRecord } from "@/types/game";

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

export const convertShootingResponse = (data: PlayerShootingRecord[], h_code: number): ShotPoint[] => {
  const shots: ShotPoint[] = [];

  for (const player of data) {
    let teamLabel: TeamLabel;

    if (Number(player.tcode) === h_code) {
      teamLabel = "Home";
    } else {
      teamLabel = "Away";
    }

    for (const log of player.logs) {
      const x = Number(log.x ?? 0);
      const y = Number(log.y ?? 0);
      const d = String(log.d ?? "1");
      const made = log.o === "O";
      const q = String(log.q ?? "");

      const flip = (x: number, y: number) => ({ x: COURT_W - x, y: COURT_H - y });

      let fx = x,
        fy = y;

      if (teamLabel === "Home") {
        if (d === "1") ({ x: fx, y: fy } = flip(x, y));
      } else {
        if (d !== "1") ({ x: fx, y: fy } = flip(x, y));
      }

      shots.push({
        x: fx,
        y: fy,
        made,
        team: teamLabel,
        quarter: q,
      });
    }
  }

  return shots;
};
