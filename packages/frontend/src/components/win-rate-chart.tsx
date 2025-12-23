import { Area, CartesianGrid, ComposedChart, ReferenceLine, Tooltip, XAxis, YAxis } from "recharts";

import type { GameData } from "@/types/game";
import { formatTime } from "@/utils/time";

interface WinRateChartProps {
  width?: number;
  height?: number;
  gameData: GameData;
}

const WinRateChart = ({ width = 600, height = 400, gameData }: WinRateChartProps) => {
  const probLogs = gameData.prediction_records;
  if (probLogs.length === 0) {
    probLogs.push({ home_probability: 50, away_probability: 50, total_time_sec: 0 });
  }

  const chartData = probLogs.map((p) => ({
    ...p,
    upper_bound: 100, // 위쪽 경계
  }));

  const totalTimeSec = probLogs[probLogs.length - 1].total_time_sec;
  const maxTime = Math.max(2400, totalTimeSec + (totalTimeSec % 300 === 0 ? 0 : 300 - (totalTimeSec % 300)));

  const xTicks: number[] = [];
  for (let t = 0; t < maxTime + 300; t += 300) {
    xTicks.push(t);
  }
  const yTicks = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100];

  const clutchTimeMin = 3;
  const last5MinLog =
    gameData.game_info.isStarted + gameData.game_info.isEnded === 2
      ? probLogs.find((p) => p.total_time_sec >= totalTimeSec - clutchTimeMin * 60)
      : null;

  return (
    <>
      <h3 className="mt-8 text-center text-xl font-bold">Win Rate Chart</h3>
      {last5MinLog && (
        <div className="flex flex-row justify-center gap-3">
          <div>경기 종료 {clutchTimeMin}분 전 승률:</div>
          <div className="font-semibold text-blue-600">
            {gameData.game_info.home.name}: {last5MinLog.home_probability}%
          </div>
          <div className="font-semibold text-red-600">
            {gameData.game_info.away.name}: {last5MinLog.away_probability}%
          </div>
          <div>
            {(() => {
              const winner =
                gameData.game_info.home.score! > gameData.game_info.away.score!
                  ? "home"
                  : gameData.game_info.home.score! < gameData.game_info.away.score!
                    ? "away"
                    : "draw";
              const probWinner =
                last5MinLog.home_probability > last5MinLog.away_probability
                  ? "home"
                  : last5MinLog.home_probability < last5MinLog.away_probability
                    ? "away"
                    : "draw";
              if (winner === "draw" || probWinner === "draw") {
                return "무승부로 예측과 결과 일치 여부 없음";
              }
              if (winner === probWinner) {
                return "예측 성공 ✅";
              }
              return "예측 실패 ❌";
            })()}
          </div>
        </div>
      )}
      <div className="flex justify-center">
        <ComposedChart width={width} height={height} data={chartData}>
          <defs>
            <linearGradient id="colorBlue" x1="0" y1="1" x2="0" y2="0">
              <stop offset="0%" stopColor="rgba(0, 100, 255, 0.7)" />
              <stop offset="100%" stopColor="rgba(0, 100, 255, 0.2)" />
            </linearGradient>
            <linearGradient id="colorRed" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="rgba(255, 0, 0, 0.7)" />
              <stop offset="100%" stopColor="rgba(255, 0, 0, 0.2)" />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" />
          <Area
            type="monotone"
            dataKey="upper_bound"
            fill="url(#colorRed)"
            strokeWidth={0}
            activeDot={false}
            pointerEvents="none"
          />

          <Area
            type="monotone"
            dataKey="home_probability"
            fill="#ffffff"
            strokeWidth={0}
            fillOpacity={1}
            activeDot={false}
            pointerEvents="none"
          />
          <Area
            type="monotone"
            dataKey="home_probability"
            fill="url(#colorBlue)"
            fillOpacity={1}
            activeDot={true}
            pointerEvents="none"
          />

          <XAxis
            dataKey="total_time_sec"
            type="number"
            ticks={xTicks}
            tickFormatter={(value) => `${Math.floor(value / 60)}`}
            domain={[0, maxTime]}
            pointerEvents="none"
          />
          <YAxis
            type="number"
            ticks={yTicks}
            tickFormatter={(value) => `${value}%`}
            domain={["dataMin", "dataMax"]}
            pointerEvents="none"
          />
          {[0, 600, 1200, 1800, 2400].map((time) => (
            <ReferenceLine key={time} x={time} stroke="#000" strokeDasharray="3 3" />
          ))}
          {[0, 50, 100].map((percent) => (
            <ReferenceLine key={percent} y={percent} stroke="#000" strokeDasharray="3 3" />
          ))}
          <Tooltip
            content={({ active, payload, label }) => {
              if (!active || !payload || payload.length === 0) return null;

              const data = gameData.prediction_records.find((d) => d.total_time_sec === label);
              if (!data) return `오류 발생 시간: ${label}`;

              const time = formatTime(data.total_time_sec, {
                home: gameData.game_info.home.score,
                away: gameData.game_info.away.score,
              });

              return (
                <div className="rounded-lg border border-gray-300 bg-white p-2.5">
                  <div>{time}</div>
                  <div>홈팀 승률: {data.home_probability}%</div>
                  <div>원정팀 승률: {data.away_probability}%</div>
                </div>
              );
            }}
          />
        </ComposedChart>
      </div>
      <div className="flex justify-center gap-4 text-sm font-semibold">
        <div className="text-blue-600">home: {gameData.game_info.home.name}</div>
        <div className="text-red-600">away: {gameData.game_info.away.name}</div>
      </div>
    </>
  );
};

export default WinRateChart;
