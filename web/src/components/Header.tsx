import styles from '../assets/css/Header.module.css';

export const Header: React.FC = () => {
  return (
    <header className={styles.header}>
      <a className={styles.title} href='/sports_win_rate_analyze/'>Sports Win Rate Analyze</a>
      <div className={styles.menu}>
        <a href="/sports_win_rate_analyze/2021-2022">2021-2022</a>
        <a href="/sports_win_rate_analyze/2022-2023">2022-2023</a>
        <a href="/sports_win_rate_analyze/2023-2024">2023-2024</a>
        <a href="/sports_win_rate_analyze/2024-2025">2024-2025</a>
        <a href="/sports_win_rate_analyze/2025-2026">2025-2026</a>
      </div>
    </header>
  )
}