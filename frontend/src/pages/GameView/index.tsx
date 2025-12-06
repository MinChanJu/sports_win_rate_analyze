import { useGameData } from "./hooks/use-game-data";

import { useParams } from "react-router-dom";

import WinRateChart from "@/components/WinRateChart";
import { ShootingChart } from "@/components/shooting-chart";

const GameView = () => {
  const { gameKey } = useParams();

  const { gameData, isLoading, isError, error, handleReload, isFetching, countSeconds } = useGameData(gameKey);

  if (isLoading && !gameData) {
    return (
      <div className="flex flex-col items-center gap-5">
        <div>Loading...</div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex flex-col items-center gap-5">
        <div>Error: {(error as Error).message}</div>
        <button
          onClick={handleReload}
          className="rounded bg-blue-500 px-4 py-2 text-white disabled:opacity-50"
          disabled={isFetching}
        >
          다시 시도
        </button>
      </div>
    );
  }

  if (!gameData) return null;

  return (
    <div className="mb-10 flex flex-col items-center gap-5">
      <h1 className="text-2xl font-bold">
        {gameData.game_info.home.name} vs {gameData.game_info.away.name}
      </h1>
      <div className="text-lg">
        {gameData.game_info.home.score} - {gameData.game_info.away.score}
      </div>
      <a
        href={`https://kbl.or.kr/match/record/${gameData.game_info.gameKey}/${gameData.game_info.gameDate}`}
        className="rounded-lg bg-gray-200 p-2 hover:bg-gray-300"
        target="_blank"
        rel="noopener noreferrer"
      >
        View on KBL
      </a>

      <button
        onClick={handleReload}
        className="cursor-pointer rounded bg-blue-500 px-4 py-2 text-white disabled:opacity-50"
        disabled={isFetching}
      >
        {gameData.game_info.isStarted && !gameData.game_info.isEnded ? `Reload (${countSeconds}s)` : `Reload`}
      </button>

      {gameData.game_info.isStarted + gameData.game_info.isEnded === 1 && (
        <div className="font-semibold text-orange-600">Game In Progress</div>
      )}
      {gameData.game_info.isStarted === 0 && <div className="font-semibold text-gray-600">Game Not Started</div>}

      <h3 className="mt-8 text-xl font-bold">Win Rate Chart</h3>
      <WinRateChart probLogs={gameData.prediction_records} />
      <h3 className="mt-8 text-xl font-bold">Shooting Chart</h3>
      <ShootingChart
        h_code={gameData.game_info.home.code}
        a_code={gameData.game_info.away.code}
        homeName={gameData.game_info.home.name}
        awayName={gameData.game_info.away.name}
        shootingLogs={gameData.shooting_records}
      />
    </div>
  );
};

export default GameView;
