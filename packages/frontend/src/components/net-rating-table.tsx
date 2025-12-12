import TeamLogo from "./team-logo";

import type { GameInfo, QuarterNetRatings } from "@/types/game";

interface NetRatingTableProps {
  gameInfo: GameInfo;
  quarterNetRatings: QuarterNetRatings;
}

const NetRatingTable = ({ gameInfo, quarterNetRatings }: NetRatingTableProps) => {
  return (
    <table>
      <colgroup>
        <col className="w-1/5" />
        <col className="w-2/5" />
        <col className="w-2/5" />
      </colgroup>
      <thead>
        <tr className="bg-gray-100 text-center text-sm">
          <th className="px-4 py-2">쿼터</th>
          <th className="px-4 py-2">
            {gameInfo.home.name} <TeamLogo teamLogo={gameInfo.home.logo} className="inline h-5 w-5" />
          </th>
          <th className="px-4 py-2">
            {gameInfo.away.name} <TeamLogo teamLogo={gameInfo.away.logo} className="inline h-5 w-5" />
          </th>
        </tr>
      </thead>
      <tbody>
        {quarterNetRatings.order.map((quarter, index) => {
          const homeRating = quarterNetRatings.home[index];
          const awayRating = quarterNetRatings.away[index];

          return (
            <tr key={quarter} className="border-t border-b border-gray-300 text-center text-sm">
              <td className="bg-gray-300 px-4 py-2">{quarter}</td>
              <td className={`px-4 py-2 ${homeRating > awayRating ? "bg-green-300" : "bg-red-300"}`}>
                {homeRating.toFixed(2)}
              </td>
              <td className={`px-4 py-2 ${awayRating > homeRating ? "bg-green-300" : "bg-red-300"}`}>
                {awayRating.toFixed(2)}
              </td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
};

export default NetRatingTable;
