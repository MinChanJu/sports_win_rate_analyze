import { useNavigate } from "react-router-dom";

export const Header: React.FC = () => {
  const navigate = useNavigate();
  return (
    <header className="mt-5 mb-5 flex items-center justify-center gap-2.5">
      <button className="cursor-pointer text-2xl font-bold" onClick={() => navigate("/")}>
        Sports Win Rate Analyze
      </button>
      <div className="flex border-t border-b border-l">
        <button className="cursor-pointer border-r px-4 py-2 break-all" onClick={() => navigate("/2021-2022")}>
          2021-2022
        </button>
        <button className="cursor-pointer border-r px-4 py-2 break-all" onClick={() => navigate("/2022-2023")}>
          2022-2023
        </button>
        <button className="cursor-pointer border-r px-4 py-2 break-all" onClick={() => navigate("/2023-2024")}>
          2023-2024
        </button>
        <button className="cursor-pointer border-r px-4 py-2 break-all" onClick={() => navigate("/2024-2025")}>
          2024-2025
        </button>
        <button className="cursor-pointer border-r px-4 py-2 break-all" onClick={() => navigate("/2025-2026")}>
          2025-2026
        </button>
      </div>
    </header>
  );
};
