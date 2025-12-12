import { useNavigate } from "react-router-dom";

const Header: React.FC = () => {
  const navigate = useNavigate();
  return (
    <header className="mt-5 mb-5 flex items-center justify-center gap-2.5">
      <button className="cursor-pointer text-2xl font-bold" onClick={() => navigate("/")}>
        Sports Win Rate Analyze
      </button>
      <div className="flex border-t border-b border-l">
        {["2021-2022", "2022-2023", "2023-2024", "2024-2025", "2025-2026"].map((season) => (
          <button
            key={season}
            className="cursor-pointer border-r px-4 py-2 break-all"
            onClick={() => navigate(`/${season}`)}
          >
            {season}
          </button>
        ))}
      </div>
    </header>
  );
};

export default Header;
