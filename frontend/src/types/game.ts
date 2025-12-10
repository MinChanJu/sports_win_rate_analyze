export type ProbabilityRecord = {
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

export type TeamStats = {
  TEAM: number;
  AST: number;
  BLK: number;
  DREB: number;
  OREB: number;
  PRB: number;
  TRB: number;
  "2PA": number;
  "2PM": number;
  "3PA": number;
  "3PM": number;
  DKA: number;
  DKM: number;
  FTA: number;
  FTM: number;
  SWA: number;
  SWM: number;
  FGA: number;
  FGM: number;
  TPF: number;
  PF: number;
  PP: number;
  PA: number;
  STL: number;
  TTO: number;
  PTO: number;
  MIN: number;
  UF: number;
  TF: number;
  EJ: number;
  TO: number;
  NR: number;
  "TS%": number;
  "eFG%": number;
  EFF: number;
  "TOV%": number;
  "OREB%": number;
  "FT%": number;
  "AST%": number;
  "AST/TO%": number;
  CR: number;
  LC: number;
  LLP: number;
  PACE: number;
};

export type GameStats = {
  home: TeamStats;
  away: TeamStats;
};

export type ScoreBoard = {
  scoreq1: number;
  scoreq2: number;
  scoreq3: number;
  scoreq4: number;
  scoreeq: number[];
};

export type TeamScoreRecord = {
  home: ScoreBoard;
  away: ScoreBoard;
};

export type GameData = {
  game_info: GameInfo;
  team_score_record: TeamScoreRecord;
  prediction_records: ProbabilityRecord[];
  shooting_records: PlayerShootingRecord[];
  last_game_stats: GameStats;
};

export type GameList = {
  games: GameInfo[];
};
