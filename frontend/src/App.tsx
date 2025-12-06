import { AppRouter } from "./AppRouter";
import { PageTitle } from "./components";
import "./styles";

import { BrowserRouter } from "react-router-dom";

const App: React.FC = () => {
  return (
    <BrowserRouter basename="/sports_win_rate_analyze">
      <PageTitle />
      <AppRouter />
    </BrowserRouter>
  );
};

export default App;
