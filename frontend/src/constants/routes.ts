export const ROUTES = {
  HOME: "/",
  SEASON: "/:seasonId",
  SEASON_ID: (seasonId: number) => `/${seasonId}`,
  GAME: "/game/:gameKey",

  NOT_FOUND: "*",
};
