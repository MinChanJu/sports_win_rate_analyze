import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";

import type { GameInfo, GameList } from "@/types/game";

const useHome = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const currentDate = new Date();

  const [year, setYear] = useState(searchParams.get("year") || currentDate.getFullYear().toString());
  const [month, setMonth] = useState(
    searchParams.get("month") || (currentDate.getMonth() + 1).toString().padStart(2, "0"),
  );
  const [gameList, setGameList] = useState<GameInfo[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setSearchParams({ year, month }, { replace: true });
  }, [year, month, setSearchParams]);

  useEffect(() => {
    const fetchGameList = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/list/${year}${month}01/${year}${month}40`);
        if (!response.ok) {
          throw new Error("Failed to fetch game list");
        }
        const data: GameList = await response.json();
        setGameList(data.games);
      } catch (error) {
        console.error("Error fetching game list:", error);
        setError("Failed to fetch game list");
      } finally {
        setIsLoading(false);
      }
    };

    fetchGameList();
  }, [year, month]);

  return { currentDate, year, setYear, month, setMonth, gameList, isLoading, error };
};

export default useHome;
