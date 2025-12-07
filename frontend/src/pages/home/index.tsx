import useHome from "./hooks/use-home";

import GameCardList from "@/components/game-card-list";
import Loading from "@/components/loading";

const Home = () => {
  const { currentDate, year, setYear, month, setMonth, gameList, isLoading, error } = useHome();

  return (
    <>
      <div className="mb-4 flex justify-center gap-10">
        <select
          value={year}
          onChange={(e) => setYear(e.target.value)}
          className="mr-2 rounded border border-gray-300 p-2"
        >
          {Array.from({ length: 10 }, (_, i) => {
            const y = (currentDate.getFullYear() + 1 - i).toString();
            return (
              <option key={y} value={y}>
                {y}
              </option>
            );
          })}
        </select>
        <select
          value={month}
          onChange={(e) => setMonth(e.target.value)}
          className="mr-2 rounded border border-gray-300 p-2"
        >
          {Array.from({ length: 12 }, (_, i) => {
            const m = (i + 1).toString().padStart(2, "0");
            return (
              <option key={m} value={m}>
                {m}
              </option>
            );
          })}
        </select>
      </div>
      {isLoading && <Loading />}
      {error && <p className="text-red-500">{error}</p>}
      {!isLoading && !error && <GameCardList gameList={gameList} />}
    </>
  );
};

export default Home;
