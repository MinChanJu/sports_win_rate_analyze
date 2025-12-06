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
      <h1 className="mb-5 text-center">Season: {seasonId}</h1>
      <div className="box-border grid w-full grid-cols-[repeat(auto-fit,minmax(300px,1fr))] gap-4 justify-self-center p-5">
        {seasonGames.map((g, index) => (
          <div key={index} className="min-w-[200px] flex-1 rounded-lg border border-black bg-blue-200 p-4">
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
