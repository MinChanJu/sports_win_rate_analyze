import { Cell, Legend, Pie, PieChart } from "recharts";

import type { GameData, TeamStats } from "@/types/game";

interface DonutChartProps {
  gameData: GameData;
  field: keyof TeamStats;
  size?: number; // 도넛 지름(px)
}

const DonutChart = ({ gameData, field, size = 220 }: DonutChartProps) => {
  const homeValue = gameData.last_game_stats.home[field];
  const awayValue = gameData.last_game_stats.away[field];
  const total = homeValue + awayValue;
  const homePercent = total === 0 ? 50 : (homeValue / total) * 100;
  const awayPercent = total === 0 ? 50 : (awayValue / total) * 100;

  // 도넛 영역 + 아래 Legend 영역(대략 40px)
  const LEGEND_HEIGHT = 40;
  const totalHeight = size + LEGEND_HEIGHT;

  return (
    <div className="mb-8">
      <PieChart width={size} height={totalHeight} margin={{ top: 8, right: 8, bottom: LEGEND_HEIGHT, left: 8 }}>
        <Pie
          data={[
            { name: gameData.game_info.home.name, value: homeValue },
            { name: gameData.game_info.away.name, value: awayValue },
          ]}
          cx="50%"
          cy="45%" // 위로 조금 올려서 아래 공간 확보
          innerRadius="60%" // 퍼센트 사용 → 컨테이너 안에서 자동 조정
          outerRadius="90%" // 끝에 딱 안 닿게
          paddingAngle={2}
          dataKey="value"
        >
          <text x="50%" y="35%" textAnchor="middle" dominantBaseline="middle" fontSize="20" fontWeight="bold">
            {field}
          </text>
          <Cell key="home" fill="#1217ff" />
          <Cell key="away" fill="#f54242" />
        </Pie>

        <Legend
          verticalAlign="bottom"
          height={LEGEND_HEIGHT}
          formatter={(value) => {
            const percent = value === gameData.game_info.home.name ? homePercent : awayPercent;
            return `${value}: ${percent.toFixed(1)}%`;
          }}
        />
      </PieChart>
    </div>
  );
};

export default DonutChart;
