import TeamLogo from "./team-logo";

import { useNavigate } from "react-router-dom";

import type { GameInfo } from "@/types/game";

interface GameCardProps {
  game: GameInfo;
}

const GameCard = ({ game }: GameCardProps) => {
  const navigate = useNavigate();

  const gameYear = game.gameDate.slice(0, 4);
  const gameMonth = game.gameDate.slice(4, 6);
  const gameDay = game.gameDate.slice(6, 8);
  const gameHour = game.gameStart.slice(0, 2);
  const gameMinute = game.gameStart.slice(2, 4);

  return (
    <div
      className="flex cursor-pointer flex-col gap-2 rounded-lg bg-gray-100 p-4 hover:bg-gray-300"
      onClick={() => navigate(`/game/${game.gameKey}`)}
    >
      <div className="overflow-hidden text-sm whitespace-nowrap">
        {gameYear}-{gameMonth}-{gameDay} {game.weekDay} {gameHour}:{gameMinute} {game.stadiumName}
      </div>
      {[game.home, game.away].map((team, index) => (
        <div key={index} className="flex items-center">
          <TeamLogo teamLogo={team.logo} className="h-7 w-7" />
          <span className="flex-1 text-lg font-semibold">{team.name}</span>
          <span className="text-xl font-bold">{team.score !== null ? team.score : "-"}</span>
        </div>
      ))}
      {game.isEnded === 0 && game.isStarted === 0 && <div className="text-sm text-orange-600">경기 전</div>}
      {game.isEnded === 0 && game.isStarted === 1 && <div className="text-sm text-blue-600">경기 중</div>}
      {game.isEnded === 1 && <div className="text-sm text-green-600">경기 종료</div>}
    </div>
  );
};

export default GameCard;
