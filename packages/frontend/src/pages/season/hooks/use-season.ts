import { parseSeasonYears } from "../season.util";

import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import type { GameInfo, GameList } from "@/types/game";

const useSeason = () => {
  const { seasonName } = useParams();
  const [seasonGames, setSeasonGames] = useState<GameInfo[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSeasonGames = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const { from, to } = parseSeasonYears(seasonName) || {};
        if (!from || !to) {
          throw new Error("Invalid season format");
        }

        const response = await fetch(`${import.meta.env.VITE_API_URL}/list/${from}0801/${to}0731`);
        if (!response.ok) {
          throw new Error("Failed to fetch season games");
        }

        const data: GameList = await response.json();
        setSeasonGames(data.games);
      } catch (error) {
        if (error instanceof Error) {
          setError(error.message);
        } else {
          setError("Error fetching season games");
        }
      } finally {
        setIsLoading(false);
      }
    };

    fetchSeasonGames();
  }, [seasonName]);

  return {
    seasonName,
    seasonGames,
    isLoading,
    error,
  };
};

export default useSeason;
