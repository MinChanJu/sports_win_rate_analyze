import useSeason from "./hooks/use-season";

import GameCardList from "@/components/game-card-list";
import Loading from "@/components/loading";

const Season = () => {
  const { seasonName, seasonGames, isLoading, error } = useSeason();

  if (isLoading) {
    return <Loading />;
  }

  if (error) {
    return <p className="text-red-500">{error}</p>;
  }

  return (
    <>
      <h1 className="mb-5 text-center">Season: {seasonName}</h1>
      <GameCardList gameList={seasonGames} />
    </>
  );
};

export default Season;
