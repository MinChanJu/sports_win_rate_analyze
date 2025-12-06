import { useEffect } from "react";
import { useLocation, matchPath } from "react-router-dom";
import { ROUTES } from "../constants/routes";
import { getLastPathParam } from "../utils/path";

export const PageTitle: React.FC = () => {
  const location = useLocation();

  useEffect(() => {
    const path = location.pathname;
    const param = getLastPathParam(path);

    // 페이지별 제목 매핑
    const titleMap: { [key: string]: string } = {
      [ROUTES.HOME] : "홈",
    };

    let title = titleMap[path] || "오류";

    if (matchPath(ROUTES.SEASON, path)) {
      title = param + " 시즌";
    }

    document.title = title + " | Sports Win Rate Analyze";
  }, [location.pathname]);

  return null;
};