export const ROUTES = {
  HOME: "/",
  SEASON: "/:seasonName",
  SEASON_ID: (seasonName: string) => `/${seasonName}`,
  GAME: "/game/:gameKey",

  NOT_FOUND: "*",
};
