// src/hooks/useGameData.ts
import { useEffect, useState } from "react";

import type { GameData } from "@/types/game_data";
import { useQuery } from "@tanstack/react-query";

const fetchGameData = async (gameKey: string) => {
  const res = await fetch(`${import.meta.env.VITE_API_URL}/game/${gameKey}`);
  if (!res.ok) {
    throw new Error("Network response was not ok");
  }
  return (await res.json()) as GameData;
};

export const useGameData = (gameKey?: string) => {
  const [countSeconds, setCountSeconds] = useState(30);
  const query = useQuery<GameData, Error>({
    queryKey: ["game", gameKey],
    queryFn: () => fetchGameData(gameKey as string),
    enabled: !!gameKey,
    refetchInterval: (q) => {
      const data = q.state.data;
      if (!data) return false;
      return data.game_info.isStarted && !data.game_info.isEnded ? 30_000 : false;
    },
    refetchIntervalInBackground: true,
    // 메모리 관리를 위한 설정
    gcTime: 0, // 사용 안 하면 바로 가비지 컬렉션
    staleTime: 0, // 즉시 stale 처리
    refetchOnMount: false, // 마운트 시 리패치 방지
    refetchOnWindowFocus: false, // 윈도우 포커스 시 리패치 방지
  });

  useEffect(() => {
    const hasGame = !!query.data;
    const finished = query.data?.game_info.isStarted && !query.data?.game_info.isEnded;
    if (!hasGame || !finished) return;

    setCountSeconds(30);

    const id = window.setInterval(() => {
      setCountSeconds((prev) => (prev <= 1 ? 30 : prev - 1));
    }, 1000);

    return () => clearInterval(id);
  }, [query.data]);

  const handleReload = () => {
    setCountSeconds(30);
    query.refetch();
  };

  return {
    gameData: query.data,
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error,
    countSeconds,
    handleReload,
    refetch: query.refetch,
    isFetching: query.isFetching,
  };
};
