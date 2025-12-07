export const validateSeason = (seasonName: string): boolean => {
  const seasonParts = seasonName.split("-");
  if (seasonParts.length !== 2) {
    return false;
  }
  if (
    seasonParts.filter((part) => {
      const yearNum = Number(part);
      return isNaN(yearNum) || yearNum < 2000 || yearNum > 2100;
    }).length > 0
  ) {
    return false;
  }

  const from = seasonParts[0];
  const to = seasonParts[1];

  if (Number(to) - Number(from) !== 1) {
    return false;
  }

  return true;
};

export const parseSeasonYears = (seasonName: string | undefined): { from: string; to: string } | null => {
  if (!seasonName || !validateSeason(seasonName)) {
    return null;
  }

  const seasonParts = seasonName.split("-");
  return { from: seasonParts[0], to: seasonParts[1] };
};
