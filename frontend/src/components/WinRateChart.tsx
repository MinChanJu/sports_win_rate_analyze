import {
  Area,
  CartesianGrid,
  ComposedChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { NameType, ValueType } from "recharts/types/component/DefaultTooltipContent";
import type { ContentType } from "recharts/types/component/Tooltip";

import type { ProbLog } from "@/types";

interface WinRateChartProps {
  width?: number;
  height?: number;
  probLogs: ProbLog[];
}

const WinRateChart = ({ width = 600, height = 300, probLogs }: WinRateChartProps) => {
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

  return (
    <div className="relative" style={{ width, height }}>
      <ResponsiveContainer width={width} height={height}>
        <ComposedChart data={chartData}>
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
          <Tooltip content={createContent(chartData)} />
        </ComposedChart>
      </ResponsiveContainer>
      <div
        style={{
          position: "absolute",
          right: -40,
          top: 0,
          color: "red",
          fontSize: 14,
          fontWeight: 600,
          pointerEvents: "none",
        }}
      >
        Away
      </div>

      <div
        style={{
          position: "absolute",
          right: -40,
          bottom: 35,
          color: "blue",
          fontSize: 14,
          fontWeight: 600,
          pointerEvents: "none",
        }}
      >
        Home
      </div>
    </div>
  );
};

const createContent: (chartData: ProbLog[]) => ContentType<ValueType, NameType> =
  (chartData) =>
  ({ active, payload, label }) => {
    if (!active || !payload || payload.length === 0) return null;

    const data = chartData.find((d) => d.total_time_sec === label);
    if (!data || typeof label !== "number") return `오류 발생 시간: ${label}`;

    let quarter = null;
    let quarter_time = null;
    if (label < 2400) {
      quarter = `${Math.floor(label / 600) + 1}쿼터`;
      quarter_time = label % 600;
    } else {
      quarter = `연장전 ${Math.floor((label - 2400) / 300) + 1}`;
      quarter_time = label % 300;
    }

    const minutes = Math.floor(quarter_time / 60);
    const seconds = quarter_time % 60;

    const time = `${minutes}:${seconds.toString().padStart(2, "0")}`;

    return (
      <div className="rounded-lg border border-gray-300 bg-white p-2.5">
        <div>{`${quarter} ${time}`}</div>
        <div>홈팀 승률: {data.home_probability}%</div>
        <div>원정팀 승률: {data.away_probability}%</div>
      </div>
    );
  };

export default WinRateChart;
