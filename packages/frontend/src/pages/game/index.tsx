import useGame from "./hooks/use-game";

import ReloadIcon from "@/assets/icons/reload.svg?react";
import DonutChart from "@/components/donut-chart";
import HotZoneChart from "@/components/hot-zone-chart";
import Loading from "@/components/loading";
import NetRatingTable from "@/components/net-rating-table";
import PreviousStatsTable from "@/components/previous-stats-table";
import ShootingChart from "@/components/shooting-chart";
import TeamLogo from "@/components/team-logo";
import WinRateChart from "@/components/win-rate-chart";

const Game = () => {
  const { gameData, isLoading, isError, error, handleReload, isFetching } = useGame();

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
    <div className="flex flex-row justify-center gap-5 p-5">
      <div className="flex min-w-0 flex-1 flex-col items-center">
        <DonutChart gameData={gameData} field="PP" title="득점" />
        <DonutChart gameData={gameData} field="PRB" title="리바운드" />
        <DonutChart gameData={gameData} field="AST" title="어시스트" />
        <DonutChart gameData={gameData} field="STL" title="스틸" />
        <DonutChart gameData={gameData} field="BLK" title="블록" />
      </div>
      <div className="flex min-w-0 flex-2 flex-col items-center gap-5">
        <div className="game-detail flex w-full flex-col gap-5 rounded-lg bg-gray-100 p-5">
          <div className="flex flex-row gap-10">
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
          <div className="flex justify-center">
            <div className="rounded-2xl border border-gray-300 bg-black p-3 text-center text-white">
              <table className="table-auto border-collapse">
                <thead>
                  <tr className="text-gray-300">
                    <th className="px-2 py-1"></th>
                    <th className="px-2 py-1">Q1</th>
                    <th className="px-2 py-1">Q2</th>
                    <th className="px-2 py-1">Q3</th>
                    <th className="px-2 py-1">Q4</th>
                    {gameData.team_score_record.home.scoreeq.map((_, idx) => (
                      <th key={idx} className="px-2 py-1">
                        ET{idx + 1}
                      </th>
                    ))}
                    {gameData.team_score_record.home.scoreeq.length === 0 && <th className="px-2 py-1">ET</th>}
                    <th className="px-2 py-1 text-amber-500">합계</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td className="px-2 py-1 font-bold">
                      <TeamLogo teamLogo={gameInfo.home.logo} className="h-7 w-7" />
                    </td>
                    <td className="px-2 py-1">{gameData.team_score_record.home.scoreq1}</td>
                    <td className="px-2 py-1">{gameData.team_score_record.home.scoreq2}</td>
                    <td className="px-2 py-1">{gameData.team_score_record.home.scoreq3}</td>
                    <td className="px-2 py-1">{gameData.team_score_record.home.scoreq4}</td>
                    {gameData.team_score_record.home.scoreeq.map((score, idx) => (
                      <td key={idx} className="px-2 py-1">
                        {score}
                      </td>
                    ))}
                    {gameData.team_score_record.home.scoreeq.length === 0 && <td className="px-2 py-1">-</td>}
                    <td className="px-2 py-1 text-amber-500">{gameData.game_info.home.score}</td>
                  </tr>
                  <tr>
                    <td className="px-2 py-1 font-bold">
                      <TeamLogo teamLogo={gameInfo.away.logo} className="h-7 w-7" />
                    </td>
                    <td className="px-2 py-1">{gameData.team_score_record.away.scoreq1}</td>
                    <td className="px-2 py-1">{gameData.team_score_record.away.scoreq2}</td>
                    <td className="px-2 py-1">{gameData.team_score_record.away.scoreq3}</td>
                    <td className="px-2 py-1">{gameData.team_score_record.away.scoreq4}</td>
                    {gameData.team_score_record.away.scoreeq.map((score, idx) => (
                      <td key={idx} className="px-2 py-1">
                        {score}
                      </td>
                    ))}
                    {gameData.team_score_record.away.scoreeq.length === 0 && <td className="px-2 py-1">-</td>}
                    <td className="px-2 py-1 text-amber-500">{gameData.game_info.away.score}</td>
                  </tr>
                </tbody>
              </table>
            </div>
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
                <div className="text-sm text-blue-600">경기 중 (30초마다 자동 새로고침)</div>
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
        <div className="flex w-full flex-row justify-center gap-10">
          <HotZoneChart gameData={gameData} team="Home" />
          <HotZoneChart gameData={gameData} team="Away" />
        </div>
      </div>
      <div className="flex min-w-0 flex-1 flex-col items-center gap-10">
        <PreviousStatsTable previousStats={gameData.previous_stats} />
        <NetRatingTable gameInfo={gameInfo} quarterNetRatings={gameData.quarter_net_ratings} />
      </div>
    </div>
  );
};

export default Game;
