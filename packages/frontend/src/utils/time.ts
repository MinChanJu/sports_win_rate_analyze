export const formatTime = (totalSeconds: number, score: { home: number | null; away: number | null }): string => {
  let quarter = null;
  let quarter_time = null;

  if (totalSeconds < 2400) {
    quarter = `${Math.floor(totalSeconds / 600) + 1}쿼터`;
    quarter_time = totalSeconds % 600;
  } else if (totalSeconds === 2400 && score.home !== score.away) {
    quarter = "4쿼터";
    quarter_time = 600;
  } else {
    quarter = `연장전 ${Math.floor((totalSeconds - 2400) / 300) + 1}`;
    quarter_time = totalSeconds % 300;
  }

  const minutes = Math.floor(quarter_time / 60);
  const seconds = quarter_time % 60;

  const time = `${minutes}:${seconds.toString().padStart(2, "0")}`;
  return `${quarter} ${time}`;
};
