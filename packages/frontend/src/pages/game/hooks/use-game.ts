// src/hooks/useGameData.ts
import { useCallback, useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";

import type { GameData } from "@/types/game";

const fetchGameData = async (gameKey: string): Promise<GameData> => {
  const res = await fetch(`${import.meta.env.VITE_API_URL}/game/${gameKey}`);
  if (!res.ok) {
    throw new Error("Network response was not ok");
  }
  return await res.json();
};

const useGame = () => {
  const { gameKey } = useParams();

  const intervalRef = useRef<number | null>(null);

  const [gameData, setGameData] = useState<GameData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isError, setIsError] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);
  const [isFetching, setIsFetching] = useState<boolean>(false);

  const fetchData = useCallback(async () => {
    if (!gameKey) return;
    setIsFetching(true);
    try {
      const data = await fetchGameData(gameKey);
      setGameData(data);
      setIsError(false);
      setError(null);
    } catch (err) {
      setIsError(true);
      setError(err as Error);
    } finally {
      setIsLoading(false);
      setIsFetching(false);
    }
  }, [gameKey]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  useEffect(() => {
    const isGameInProgress = gameData?.game_info.isStarted && !gameData?.game_info.isEnded;

    // 기존 인터벌 정리
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    if (!isGameInProgress) {
      return;
    }

    // 경기 진행 중일 때만 30초마다 자동 새로고침
    intervalRef.current = window.setInterval(() => {
      fetchData();
    }, 30000);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [gameData?.game_info.isStarted, gameData?.game_info.isEnded, fetchData]);

  const handleReload = () => {
    fetchData();
  };

  return {
    gameData,
    isLoading,
    isError,
    error,
    handleReload,
    isFetching,
  };
};

export default useGame;
