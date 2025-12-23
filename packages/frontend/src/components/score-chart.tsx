import { Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import type { GameData } from "@/types/game";

interface ScoreChartProps {
  gameData: GameData;
}

const QUARTER_ORDER = ["q1", "q2", "q3", "q4", "eq1", "eq2", "eq3", "eq4"] as const;

const labelQuarter = (q: string) => {
  if (q === "q1") return "Q1";
  if (q === "q2") return "Q2";
  if (q === "q3") return "Q3";
  if (q === "q4") return "Q4";
  if (q.startsWith("eq")) return `OT${q.slice(2)}`;
  return q;
};

const ScoreChart = ({ gameData }: ScoreChartProps) => {
  const { home, away } = gameData.score_chart;

  const data = QUARTER_ORDER.flatMap((q) => {
    const hs = home[q] as number[] | undefined;
    const as = away[q] as number[] | undefined;
    if (!Array.isArray(hs) && !Array.isArray(as)) return [];

    const len = Math.max(hs?.length ?? 0, as?.length ?? 0);
    const qLabel = labelQuarter(q);

    return Array.from({ length: len }, (_, i) => ({
      time: `${qLabel}-${i + 1}`, // 같은 쿼터 안에서도 x가 안 겹치게
      quarter: qLabel, // 필요하면 표시용
      home_score: hs?.[i] ?? null,
      away_score: as?.[i] ?? null,
    }));
  });

  return (
    <>
      <div className="text-center">Score Chart</div>
      <div style={{ width: "100%", height: 300 }}>
        <ResponsiveContainer>
          <LineChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <XAxis dataKey="time" tick={false} interval="preserveStartEnd" />
            <YAxis />
            <Tooltip labelFormatter={(label) => label.split("-")[0]} />
            <Legend />
            <Line
              type="monotone"
              dataKey="home_score"
              stroke="#0000f3"
              dot={false}
              name={`${gameData.game_info.home.name} Score`}
            />
            <Line
              type="monotone"
              dataKey="away_score"
              stroke="#fe0000"
              dot={false}
              name={`${gameData.game_info.away.name} Score`}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </>
  );
};

export default ScoreChart;
