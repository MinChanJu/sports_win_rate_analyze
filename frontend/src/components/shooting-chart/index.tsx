import { type ShotPoint, type TeamLabel, convertShootingResponse } from "./util";

import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";

import type { ShootingResponse } from "@/types/game_data";

const COURT_W = 726;
const COURT_H = 412;

interface ShootingChartProps {
  h_code: number;
  a_code: number;
  homeName: string;
  awayName: string;
  width?: number;
  height?: number;
}

const ShootingChart = ({ h_code, a_code, homeName, awayName, width = 528, height = 300 }: ShootingChartProps) => {
  const { gameKey, gameDate } = useParams();
  const [shootingData, setShootingData] = useState<ShootingResponse | null>(null);

  useEffect(() => {
    if (!gameKey || !gameDate) return;

    const fetchShootingData = async () => {
      try {
        const res = await fetch(`${import.meta.env.VITE_API_URL}/shoot/${gameKey}/${gameDate}`);
        if (!res.ok) {
          throw new Error("Failed to fetch shooting data");
        }
        const data: ShootingResponse = await res.json();
        setShootingData(data);
      } catch (error) {
        console.error("Error fetching shooting data:", error);
      }
    };

    fetchShootingData();
  }, [gameKey, gameDate]);

  const shots: ShotPoint[] = useMemo(() => {
    if (!shootingData) return [];
    return convertShootingResponse(shootingData, String(h_code), String(a_code));
  }, [shootingData, h_code, a_code]);

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

  if (!shootingData) {
    return <div>Loading...</div>;
  }

  return (
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
            {homeName} (Home)
          </label>
          <label className="flex items-center gap-1">
            <input type="checkbox" checked={showAway} onChange={() => setShowAway((v) => !v)} />
            {awayName} (Away)
          </label>
        </div>
      </div>

      {/* 중앙: 코트 + 슛 */}
      <div>
        <svg viewBox={`0 0 ${COURT_W} ${COURT_H}`} width={width} height={height}>
          <image href="https://kbl.or.kr/assets/img/game/court.png" x={0} y={0} width={COURT_W} height={COURT_H} />

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
  );
};

export { ShootingChart };
