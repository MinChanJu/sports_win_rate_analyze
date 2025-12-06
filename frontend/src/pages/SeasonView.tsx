import styles from "../assets/css/SessionView.module.css";
import { Error } from "../components";
import { type Game } from "../types";

import React from "react";
import { useParams } from "react-router-dom";

type ProjectViewProps = {
  game: Record<string, Game[]>;
};

export const SeasonView: React.FC<ProjectViewProps> = ({ game }) => {
  const { seasonId } = useParams();

  if (!seasonId) return <Error message="Season ID is missing" />;

  console.log("SeasonView 렌더링:", seasonId);
  const seasonGames = game[seasonId] || [];

  return (
    <>
      <h1 className={styles.title}>Season: {seasonId}</h1>
      <div className={styles.sessionContainer}>
        {seasonGames.map((g, index) => (
          <div key={index} className={styles.sessionItem}>
            <h2>
              {g.home} - {g.away}
            </h2>
            <p>Date: {g.date}</p>
            <p>Score: {g.score}</p>
          </div>
        ))}
      </div>
    </>
  );
};
