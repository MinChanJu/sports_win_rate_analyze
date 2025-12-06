export type ProbLog = {
  home_probability: number;
  away_probability: number;
  total_time_sec: number;
};

export type TeamInfo = {
  code: number;
  name: string;
  score: number;
};

export type GameData = {
  meta_info: {
    gameKey: string;
    gameDate: string;
    home: TeamInfo;
    away: TeamInfo;
    finished: boolean;
  };
  records: ProbLog[];
};

export type ShootLog = {
  q: string;
  x: number;
  y: number;
  o: string;
  d: string;
};

export type PlayerShootingRecord = {
  pcode: string;
  pname: string;
  ename: string;
  tcode: string;
  logs: ShootLog[];
};

export type ShootingResponse = {
  shooting_records: PlayerShootingRecord[];
};
