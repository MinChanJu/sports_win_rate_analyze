interface TeamLogoProps {
  teamLogo: string | null;
  className?: string;
}

const TeamLogo = ({ teamLogo, className = "h-7 w-7" }: TeamLogoProps) => {
  const primary = `https://www.kbl.or.kr/assets/img/ico/logo/ic-${teamLogo}.svg`;
  const secondary = `https://www.kbl.or.kr/assets/img/ico/logo/old/${teamLogo}e.png`;
  const fallback = "https://www.kbl.or.kr/assets/img/logo/logo-header.svg";

  return (
    <img
      src={primary}
      className={`mr-2 ${className} object-contain`}
      alt={`${teamLogo} logo`}
      onError={(e) => {
        const img = e.currentTarget;

        if (!img.dataset.failedCount) {
          img.dataset.failedCount = "1";
          img.src = secondary;
          return;
        }

        if (img.dataset.failedCount === "1") {
          img.dataset.failedCount = "2";
          img.src = fallback;
          return;
        }
      }}
    />
  );
};

export default TeamLogo;
