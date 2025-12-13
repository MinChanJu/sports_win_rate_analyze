import { type ShotPoint, type TeamLabel, convertShootingResponse } from "./util";

import { useEffect, useMemo, useState } from "react";

import { COURT_H, COURT_W } from "@/constants/court";
import type { GameData } from "@/types/game";

interface ShootingChartProps {
  gameData: GameData;
  ratio?: number;
  width?: number;
  height?: number;
}

const ShootingChart = ({ gameData, ratio = 1.3 }: ShootingChartProps) => {
  const { name: home_name } = gameData.game_info.home;
  const { name: away_name } = gameData.game_info.away;
  const shootingLogs = gameData.shooting_records;

  const shots: ShotPoint[] = useMemo(() => {
    if (!shootingLogs) return [];
    return convertShootingResponse(shootingLogs, gameData.game_info.home.code);
  }, [shootingLogs, gameData.game_info.home.code]);

  const allQuarters = useMemo(() => Array.from(new Set(shots.map((s) => s.quarter))).sort(), [shots]);

  const [activeQuarters, setActiveQuarters] = useState<string[]>([]);
  const [showHome, setShowHome] = useState(true);
  const [showAway, setShowAway] = useState(true);
  const [showMade, setShowMade] = useState(true);
  const [showMiss, setShowMiss] = useState(true);

  useEffect(() => {
    setActiveQuarters(allQuarters);
  }, [allQuarters]);

  const filteredShots = useMemo(
    () =>
      shots.filter((s) => {
        if (!activeQuarters.includes(s.quarter)) return false;
        if (s.team === "Home" && !showHome) return false;
        if (s.team === "Away" && !showAway) return false;
        if (s.made && !showMade) return false;
        if (!s.made && !showMiss) return false;
        return true;
      }),
    [shots, activeQuarters, showHome, showAway, showMade, showMiss],
  );

  const calcStat = (team: TeamLabel) => {
    const teamShots = filteredShots.filter((s) => s.team === team);
    if (teamShots.length === 0) return "0.0% (0/0)";
    const made = teamShots.filter((s) => s.made).length;
    const pct = (made / teamShots.length) * 100;
    return `${pct.toFixed(1)}% (${made}/${teamShots.length})`;
  };

  const toggleQuarter = (q: string) => {
    setActiveQuarters((prev) => (prev.includes(q) ? prev.filter((v) => v !== q) : [...prev, q]));
  };

  return (
    <>
      <div className="mt-8 text-center text-xl font-bold">Shooting Chart</div>
      <div className="flex gap-4">
        {/* 왼쪽: 필터 패널 */}
        <div className="flex flex-col gap-3 text-xs sm:text-sm">
          <div>
            <div className="mb-1 font-bold">쿼터</div>
            {allQuarters.map((q) => (
              <label key={q} className="flex items-center gap-1">
                <input type="checkbox" checked={activeQuarters.includes(q)} onChange={() => toggleQuarter(q)} />
                {q}
              </label>
            ))}
          </div>

          <div>
            <div className="mb-1 font-bold">팀</div>
            <label className="flex items-center gap-1">
              <input type="checkbox" checked={showHome} onChange={() => setShowHome((v) => !v)} />
              {home_name}
            </label>
            <label className="flex items-center gap-1">
              <input type="checkbox" checked={showAway} onChange={() => setShowAway((v) => !v)} />
              {away_name}
            </label>
          </div>
        </div>

        {/* 중앙: 코트 + 슛 */}
        <div>
          <svg viewBox={`0 0 ${COURT_W} ${COURT_H}`} width={350 * ratio} height={200 * ratio}>
            <image
              href="https://kbl.or.kr/assets/img/game/court.png"
              x={0}
              y={0}
              width={COURT_W}
              height={COURT_H}
              style={{ objectFit: "fill" }}
            />

            {filteredShots.map((s, idx) =>
              s.made ? (
                <circle
                  key={idx}
                  cx={s.x}
                  cy={s.y}
                  r={7}
                  fill="none"
                  stroke={s.team === "Home" ? "blue" : "green"}
                  strokeWidth={1.5}
                />
              ) : (
                <g key={idx} stroke="red">
                  <line x1={s.x - 7} y1={s.y - 7} x2={s.x + 7} y2={s.y + 7} />
                  <line x1={s.x - 7} y1={s.y + 7} x2={s.x + 7} y2={s.y - 7} />
                </g>
              ),
            )}
          </svg>
        </div>

        {/* 오른쪽: 필터 패널 */}
        <div className="flex flex-col gap-3 text-xs sm:text-sm">
          <div>
            <div className="mb-1 font-bold">결과</div>
            <label className="flex items-center gap-1">
              <input type="checkbox" checked={showMade} onChange={() => setShowMade((v) => !v)} />
              성공 (O)
            </label>
            <label className="flex items-center gap-1">
              <input type="checkbox" checked={showMiss} onChange={() => setShowMiss((v) => !v)} />
              실패 (X)
            </label>
          </div>

          <div className="mt-2 text-xs text-gray-700">
            <div className="mb-1 font-bold">슈팅 통계 (필터 적용 후)</div>
            <div>
              <b>HOME</b> {calcStat("Home")}
            </div>
            <div>
              <b>AWAY</b> {calcStat("Away")}
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default ShootingChart;
