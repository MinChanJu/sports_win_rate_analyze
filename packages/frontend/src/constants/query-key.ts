export const QUERY_KEYS = {
  GAME_DETAIL: (gameKey: string) => ["game", gameKey],
  GAME_LIST: (fromDate: string, toDate: string) => ["gameList", fromDate, toDate],
};
