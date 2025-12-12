import Error from "./components/error";
import Header from "./components/header";
import PageTitle from "./components/page-title";
import { ROUTES } from "./constants/routes";
import GamePage from "./pages/game";
import HomePage from "./pages/home";
import SeasonPage from "./pages/season";

import { BrowserRouter, Route, Routes } from "react-router-dom";

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <PageTitle />
      <Header />

      <main>
        <Routes>
          <Route path={ROUTES.HOME} element={<HomePage />} />
          <Route path={ROUTES.SEASON} element={<SeasonPage />} />
          <Route path={ROUTES.GAME} element={<GamePage />} />
          <Route path={ROUTES.NOT_FOUND} element={<Error />} />
        </Routes>
      </main>

      <footer></footer>
    </BrowserRouter>
  );
};

export default App;
