import { useEffect } from 'react';
import { Route, Routes, useLocation } from 'react-router-dom';
import { ROUTES } from '../constants/routes';
import { HomeView, SeasonView } from '../pages';
import { Error, Header } from '.';
import data from '../assets/data/game.json'

export const AppRouter: React.FC = () => {
  const location = useLocation();

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [location.pathname]);

  return (
    <>
      <Header />

      <main>
        <Routes>
          <Route path={ROUTES.HOME} element={<HomeView />} />
          <Route path={ROUTES.SEASON} element={<SeasonView game={data} />} />

          <Route path={ROUTES.NOT_FOUND} element={<Error />} />
        </Routes>
      </main>

      <footer>
      </footer>
    </>
  )
}