export const ROUTES = {
  HOME: "/",
  SEASON: "/:seasonId",
  SEASON_ID: (seasonId: number) => `/${seasonId}`,
  GAME: "/:gameKey/:gameDate",

  NOT_FOUND: "*",
};
