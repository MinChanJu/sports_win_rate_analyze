export type ProbLog = {
  home_probability: number;
  away_probability: number;
  total_time_sec: number;
};

export type TeamInfo = {
  code: number;
  name: string;
  score: number | null;
  logo: string | null;
};

export type GameInfo = {
  gameKey: string;
  gameDate: string;
  weekDay: string;
  gameStart: string;
  isStarted: number;
  isEnded: number;
  seasonName: string;
  stadiumName: string;
  home: TeamInfo;
  away: TeamInfo;
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

export type GameData = {
  game_info: GameInfo;
  prediction_records: ProbLog[];
  shooting_records: PlayerShootingRecord[];
};

export type GameList = {
  games: GameInfo[];
};
