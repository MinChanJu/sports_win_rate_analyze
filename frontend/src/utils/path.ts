export const getLastPathParam = (path: string): string => {
  const segments = path.split('/').filter(Boolean);  // '/' 기준으로 나누기
  return segments.pop() || '';       // 마지막 요소 가져오기 (없으면 빈 문자열)
};