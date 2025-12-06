import data from "./assets/data/game.json";
import { Error, Header } from "./components";
import { ROUTES } from "./constants/routes";
import { HomeView, SeasonView } from "./pages";
import GameView from "./pages/GameView";

import { useEffect } from "react";
import { Route, Routes, useLocation } from "react-router-dom";

export const AppRouter: React.FC = () => {
  const location = useLocation();

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [location.pathname]);

  return (
    <>
      <Header />

      <main className="h-full w-full">
        <Routes>
          <Route path={ROUTES.HOME} element={<HomeView />} />
          <Route path={ROUTES.SEASON} element={<SeasonView game={data} />} />
          <Route path={ROUTES.GAME} element={<GameView />} />

          <Route path={ROUTES.NOT_FOUND} element={<Error />} />
        </Routes>
      </main>

      <footer></footer>
    </>
  );
};
