import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import type { GameInfo, GameList } from "@/types/game_data";

export const HomeView = () => {
  const navigate = useNavigate();
  const currentDate = new Date();
  const [year, setYear] = useState(currentDate.getFullYear().toString());
  const [month, setMonth] = useState((currentDate.getMonth() + 1).toString().padStart(2, "0"));
  const [gameList, setGameList] = useState<GameInfo[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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

  return (
    <>
      <h1 className="mb-5 text-center">Select a Game</h1>
      <div className="mb-4 flex justify-center gap-10">
        <select
          value={year}
          onChange={(e) => setYear(e.target.value)}
          className="mr-2 rounded border border-gray-300 p-2"
        >
          {Array.from({ length: 10 }, (_, i) => {
            const y = (currentDate.getFullYear() + 1 - i).toString();
            return (
              <option key={y} value={y}>
                {y}
              </option>
            );
          })}
        </select>
        <select
          value={month}
          onChange={(e) => setMonth(e.target.value)}
          className="mr-2 rounded border border-gray-300 p-2"
        >
          {Array.from({ length: 12 }, (_, i) => {
            const m = (i + 1).toString().padStart(2, "0");
            return (
              <option key={m} value={m}>
                {m}
              </option>
            );
          })}
        </select>
      </div>
      <div className="box-border grid w-full grid-cols-[repeat(auto-fit,minmax(300px,1fr))] gap-4 justify-self-center p-5">
        {isLoading && <p>Loading...</p>}
        {error && <p className="text-red-500">{error}</p>}
        {!isLoading && !error && gameList.length === 0 && <p>No games found for the selected month.</p>}
        {!isLoading &&
          !error &&
          gameList.map((game, index) => {
            const gameYear = game.gameDate.slice(0, 4);
            const gameMonth = game.gameDate.slice(4, 6);
            const gameDay = game.gameDate.slice(6, 8);
            const gameHour = game.gameStart.slice(0, 2);
            const gameMinute = game.gameStart.slice(2, 4);
            return (
              <div
                key={index}
                className="min-w-[200px] flex-1 cursor-pointer rounded-lg border border-black bg-blue-200 p-4 hover:bg-blue-300"
                onClick={() => navigate(`/game/${game.gameKey}`)}
              >
                <h2>
                  {game.home.name} - {game.away.name}
                </h2>
                {game.isEnded === 1 && (
                  <div className="font-semibold text-green-600">
                    {game.home.score} - {game.away.score} (Finished)
                  </div>
                )}
                {game.isStarted + game.isEnded === 1 && (
                  <div className="font-semibold text-blue-600">
                    {game.home.score} - {game.away.score} (In Progress)
                  </div>
                )}
                {game.isStarted === 0 && <div className="font-semibold text-orange-600">Game Not Started</div>}
                <p>
                  {gameYear}-{gameMonth}-{gameDay} {gameHour}:{gameMinute}
                </p>
              </div>
            );
          })}
      </div>
    </>
  );
};
