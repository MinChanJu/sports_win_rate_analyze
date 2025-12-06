// src/hooks/useGameData.ts
import type { GameData } from "@/types/game_data";
import { useQuery } from "@tanstack/react-query";

const fetchGameData = async (gameKey: string, gameDate: string) => {
  const res = await fetch(`${import.meta.env.VITE_API_URL}/predict/${gameKey}/${gameDate}`);
  if (!res.ok) {
    throw new Error("Network response was not ok");
  }
  return (await res.json()) as GameData;
};

export const useGameData = (gameKey?: string, gameDate?: string) => {
  const query = useQuery<GameData, Error>({
    queryKey: ["game", gameKey, gameDate],
    queryFn: () => fetchGameData(gameKey as string, gameDate as string),
    enabled: !!gameKey && !!gameDate,
    // v5: refetchInterval 콜백 인자는 Query 객체
    refetchInterval: (q) => {
      const data = q.state.data as GameData | undefined;
      if (!data) return false;
      return data.meta_info.finished ? false : 30_000;
    },
    refetchIntervalInBackground: true,
    // 메모리 관리를 위한 설정
    gcTime: 0, // 사용 안 하면 바로 가비지 컬렉션
    staleTime: 0, // 즉시 stale 처리
    refetchOnMount: false, // 마운트 시 리패치 방지
    refetchOnWindowFocus: false, // 윈도우 포커스 시 리패치 방지
  });

  return {
    gameData: query.data,
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error,
    refetch: query.refetch,
    isFetching: query.isFetching,
  };
};
