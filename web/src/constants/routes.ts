export const ROUTES = {
  HOME: '/',
  SEASON: '/:seasonId',
  SEASON_ID: (seasonId: number) => `/${seasonId}`,

  NOT_FOUND: '*',
};
