import styles from "../assets/css/Header.module.css";

import { useNavigate } from "react-router-dom";

export const Header: React.FC = () => {
  const navigate = useNavigate();
  return (
    <header className={styles.header}>
      <button className={styles.title} onClick={() => navigate("/")}>
        Sports Win Rate Analyze
      </button>
      <div className={styles.menu}>
        <button onClick={() => navigate("/2021-2022")}>2021-2022</button>
        <button onClick={() => navigate("/2022-2023")}>2022-2023</button>
        <button onClick={() => navigate("/2023-2024")}>2023-2024</button>
        <button onClick={() => navigate("/2024-2025")}>2024-2025</button>
        <button onClick={() => navigate("/2025-2026")}>2025-2026</button>
      </div>
    </header>
  );
};
