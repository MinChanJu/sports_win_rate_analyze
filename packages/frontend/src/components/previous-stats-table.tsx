import TeamLogo from "./team-logo";

import type { TotalPreviousStats } from "@/types/game";

interface PreviousStatsTableProps {
  previousStats: TotalPreviousStats;
}

const cellStyles = "px-4 py-2 ";
const headerCellStyles = "bg-gray-100";
const rowStyles = "border-t border-b border-gray-300 text-center text-sm";

const PreviousStatsTable = ({ previousStats }: PreviousStatsTableProps) => {
  return (
    <div className="w-full">
      <div className="flex w-full flex-row items-center justify-around">
        <TeamLogo teamLogo={previousStats.home.logo} className="h-15 w-15" />
        <div className="text-lg font-bold">VS</div>
        <TeamLogo teamLogo={previousStats.away.logo} className="h-15 w-15" />
      </div>
      <table className="w-full">
        <colgroup>
          <col className="w-2/7" />
          <col className="w-3/7" />
          <col className="w-2/7" />
        </colgroup>
        <tbody>
          <tr className={rowStyles + " border-t-gray-800"}>
            <td className={cellStyles}>
              {previousStats.home.thisSeasonWin}승 {previousStats.home.thisSeasonLose}패
            </td>
            <td className={headerCellStyles + " " + cellStyles}>이번시즌 성적</td>
            <td className={cellStyles}>
              {previousStats.away.thisSeasonWin}승 {previousStats.away.thisSeasonLose}패
            </td>
          </tr>
          <tr className={rowStyles}>
            <td className={cellStyles}>
              {previousStats.home.headToHeadWin}승 {previousStats.home.headToHeadLose}패
            </td>
            <td className={headerCellStyles + " " + cellStyles}>이번시즌 상대 전적</td>
            <td className={cellStyles}>
              {previousStats.away.headToHeadWin}승 {previousStats.away.headToHeadLose}패
            </td>
          </tr>
          <tr className={rowStyles}>
            <td className={cellStyles}>
              {previousStats.home.last5gamesWin}승 {previousStats.home.last5gamesLose}패
            </td>
            <td className={headerCellStyles + " " + cellStyles}>최근 5경기</td>
            <td className={cellStyles}>
              {previousStats.away.last5gamesWin}승 {previousStats.away.last5gamesLose}패
            </td>
          </tr>
          <tr className={rowStyles + " border-b-gray-800"}>
            <td className={cellStyles}>
              {previousStats.home.allTimeHeadToHeadWin}승 {previousStats.home.allTimeHeadToHeadLose}패
            </td>
            <td className={headerCellStyles + " " + cellStyles}>역대 전적</td>
            <td className={cellStyles}>
              {previousStats.away.allTimeHeadToHeadWin}승 {previousStats.away.allTimeHeadToHeadLose}패
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  );
};

export default PreviousStatsTable;
