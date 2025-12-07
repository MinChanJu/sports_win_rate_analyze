import useGame from "./hooks/use-game";

import ReloadIcon from "@/assets/icons/reload.svg?react";
import Loading from "@/components/loading";
import ShootingChart from "@/components/shooting-chart";
import TeamLogo from "@/components/team-logo";
import WinRateChart from "@/components/win-rate-chart";

const Game = () => {
  const { gameData, isLoading, isError, error, handleReload, isFetching, countSeconds } = useGame();

  if (isLoading && !gameData) {
    return <Loading />;
  }

  if (isError || !gameData) {
    return (
      <div className="flex flex-col items-center gap-5">
        <div>Error: {(error as Error).message}</div>
        <button
          onClick={handleReload}
          className="cursor-pointer rounded-xl bg-blue-500 p-2 text-sm text-white hover:bg-blue-700 disabled:opacity-50"
          disabled={isFetching}
        >
          다시 시도
        </button>
      </div>
    );
  }

  const gameInfo = gameData.game_info;
  const gameYear = gameInfo.gameDate.slice(0, 4);
  const gameMonth = gameInfo.gameDate.slice(4, 6);
  const gameDay = gameInfo.gameDate.slice(6, 8);
  const gameHour = gameInfo.gameStart.slice(0, 2);
  const gameMinute = gameInfo.gameStart.slice(2, 4);

  return (
    <div className="m-10 flex flex-col items-center gap-5">
      <div className="game-detail flex w-full max-w-2xl flex-col gap-5 rounded-lg bg-gray-100 p-5">
        <div className="flex w-full flex-row gap-10">
          <div className="home-team flex flex-1 flex-row items-center justify-end gap-10">
            <div className="flex w-50 flex-col items-center">
              <TeamLogo teamLogo={gameInfo.home.logo} className="h-15 w-15" />
              <div className="text-base font-medium">{gameInfo.home.name}</div>
            </div>
            <div className="text-2xl font-semibold">{gameInfo.home.score}</div>
          </div>
          <div className="away-team flex flex-1 flex-row items-center justify-start gap-10">
            <div className="text-2xl font-semibold">{gameInfo.away.score}</div>
            <div className="flex w-50 flex-col items-center">
              <TeamLogo teamLogo={gameInfo.away.logo} className="h-15 w-15" />
              <div className="text-base font-medium">{gameInfo.away.name}</div>
            </div>
          </div>
        </div>
        <div className="text-center">
          <div>
            {gameYear}-{gameMonth}-{gameDay} {gameInfo.weekDay} {gameHour}:{gameMinute}
          </div>
          <div className="text-sm text-gray-600">{gameInfo.stadiumName}</div>
        </div>
        <div className="flex flex-row justify-between">
          <a
            href={`https://kbl.or.kr/match/record/${gameInfo.gameKey}/${gameInfo.gameDate}`}
            className="rounded-lg bg-gray-300 px-2 py-1 text-sm hover:bg-gray-500"
            target="_blank"
            rel="noopener noreferrer"
          >
            <img src="https://www.kbl.or.kr/assets/img/favicon.svg" alt="KBL Logo" className="inline w-8" />
          </a>

          <div className="flex flex-row items-center gap-3">
            {gameInfo.isEnded === 0 && gameInfo.isStarted === 0 && (
              <div className="text-sm text-orange-600">경기 전</div>
            )}
            {gameInfo.isEnded === 0 && gameInfo.isStarted === 1 && (
              <>
                <div className="text-sm text-blue-600">경기 중</div>
                <div className="rounded-md bg-gray-400 px-1 py-0.5 text-sm text-white">00:{countSeconds}</div>
              </>
            )}
            {gameInfo.isEnded === 1 && <div className="text-sm text-green-600">경기 종료</div>}
            <button
              onClick={handleReload}
              className="cursor-pointer rounded-4xl bg-blue-500 p-2 text-sm text-white hover:bg-blue-700 disabled:opacity-50"
              disabled={isFetching}
            >
              <ReloadIcon className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>

      <WinRateChart gameData={gameData} />
      <ShootingChart gameData={gameData} />
    </div>
  );
};

export default Game;
