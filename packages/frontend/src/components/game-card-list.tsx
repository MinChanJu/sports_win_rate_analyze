import GameCard from "./game-card";

import type { GameInfo } from "@/types/game";

interface GameCardListProps {
  gameList: GameInfo[];
}

const GameCardList = ({ gameList }: GameCardListProps) => {
  if (gameList.length === 0) {
    return <div className="text-center text-gray-500">경기 정보가 없습니다.</div>;
  }

  return (
    <>
      <h3 className="text-center font-bold">Game List</h3>
      <h4 className="text-center">총 {gameList.length}경기</h4>
      <div className="grid w-full grid-cols-[repeat(auto-fit,minmax(300px,1fr))] gap-5 p-5">
        {gameList.map((game, index) => (
          <GameCard key={index} game={game} />
        ))}
      </div>
    </>
  );
};

export default GameCardList;
