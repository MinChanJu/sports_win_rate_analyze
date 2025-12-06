import { useGameData } from "./hooks/use-game-data";

import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import HotZoneChart from "@/components/HotZoneChart";
import WinRateChart from "@/components/WinRateChart";
import { ShootingChart } from "@/components/shooting-chart";

const dummyData = [
  { zone: "rim", percentage: 57.4 }, // 골밑
  { zone: "paint_upper", percentage: 8.3 }, // 페인트존 상단
  { zone: "mid_left_low", percentage: 35.7 }, // 미드레인지 좌하
  { zone: "mid_right_low", percentage: 40.0 }, // 미드레인지 우하
  { zone: "mid_left_high", percentage: 16.7 }, // 미드레인지 좌상 (이미지 16.7% 반영)
  { zone: "mid_right_high", percentage: 100.0 }, // 미드레인지 우상
  { zone: "three_left_corner", percentage: 14.3 }, // 3점 좌측 코너 (이미지 14.3% 반영)
  { zone: "three_right_corner", percentage: 20.0 }, // 3점 우측 코너
  { zone: "three_left_wing_low", percentage: 0.0 }, // 3점 좌측 윙 하단 (이미지 0.0% 반영)
  { zone: "three_right_wing_low", percentage: 62.5 }, // 3점 우측 윙 하단
  { zone: "three_left_top", percentage: 0.0 }, // 3점 좌측 탑 (이미지 0.0% 반영)
  { zone: "three_right_top", percentage: 25.8 }, // 3점 우측 탑
  { zone: "three_center_left", percentage: 0.0 }, // 3점 중앙 탑 좌측
  { zone: "three_center_right", percentage: 43.2 }, // 3점 중앙 탑 우측
];

const GameView = () => {
  const { gameKey, gameDate } = useParams();
  const [countSeconds, setCountSeconds] = useState(30);

  const { gameData, isLoading, isError, error, refetch, isFetching } = useGameData(gameKey, gameDate);

  const hasGame = !!gameData;
  const finished = gameData?.meta_info.finished ?? false;

  // 🔁 카운트다운 (경기 진행 중일 때만)
  useEffect(() => {
    if (!hasGame || finished) return;

    setCountSeconds(30);

    const id = window.setInterval(() => {
      setCountSeconds((prev) => (prev <= 1 ? 30 : prev - 1));
    }, 1000);

    return () => clearInterval(id);
  }, [hasGame, finished]);

  // 🔄 리로드 버튼 클릭 시 수동 리패치 + 카운트 리셋
  const handleReload = () => {
    setCountSeconds(30);
    refetch();
  };

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
    <div className="flex flex-col items-center gap-5">
      <h1 className="text-2xl font-bold">
        {gameData.meta_info.home.name} vs {gameData.meta_info.away.name}
      </h1>

      <div className="text-lg">
        {gameData.meta_info.home.score} - {gameData.meta_info.away.score}
      </div>

      <div className="text-sm text-gray-500">Date: {gameData.meta_info.gameDate}</div>

      {!finished && <div className="text-sm text-gray-500">Next auto update in: {countSeconds} seconds</div>}

      <div className="flex items-center gap-3">
        <button
          onClick={handleReload}
          className="cursor-pointer rounded bg-blue-500 px-4 py-2 text-white disabled:opacity-50"
          disabled={isFetching}
        >
          {isFetching ? "Loading..." : "Reload Now"}
        </button>
      </div>

      {finished ? (
        <div className="font-semibold text-green-600">Game Finished</div>
      ) : (
        <div className="font-semibold text-orange-600">Game In Progress</div>
      )}

      <WinRateChart probLogs={gameData.records} />
      <ShootingChart
        h_code={gameData.meta_info.home.code}
        a_code={gameData.meta_info.away.code}
        homeName={gameData.meta_info.home.name}
        awayName={gameData.meta_info.away.name}
      />
      <HotZoneChart
        data={dummyData} // 준비한 데이터 전달
        width={600} // 기준 너비 설정 (반응형을 위해 컨테이너 크기에 맞춤)
      />
    </div>
  );
};

export default GameView;
