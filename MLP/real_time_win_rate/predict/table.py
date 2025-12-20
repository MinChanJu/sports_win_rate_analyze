from pathlib import Path
import json

def quarter_to_str(quarter: dict) -> str:
    if 'home' not in quarter or 'away' not in quarter:
        return '<pre style=\"border: none; background: none; padding: 0; margin: 0;\">-<br>-</pre>'
    return f"<pre style=\"border: none; background: none; padding: 0; margin: 0;\">{quarter['home_score']:3d}  {quarter['home']*100:4.1f}<br>{quarter['away_score']:3d}  {quarter['away']*100:4.1f}</pre>"

def winner_to_str(winner: str) -> str:
    if winner == 'home':
        return '<pre style=\"border: none; background: none; padding: 0; margin: 0;\">Win<br>Lose</pre>'
    elif winner == 'away':
        return '<pre style=\"border: none; background: none; padding: 0; margin: 0;\">Lose<br>Win</pre>'
    else:
        return '<pre style=\"border: none; background: none; padding: 0; margin: 0;\">-</pre>'

def main(report_path: Path):
    table_report_path = report_path.with_name("table_report.md")

    with open(report_path, 'r') as f:
        content = json.load(f)

    with open(table_report_path, 'w', encoding='utf-8') as f:
        f.write('| <div style=\"text-align: center;\">게임키</div> | <div style=\"text-align: center;\">팀</div> | <div style=\"text-align: center;\">1쿼터</div> | <div style=\"text-align: center;\">2쿼터</div> | <div style=\"text-align: center;\">3쿼터</div> | <div style=\"text-align: center;\">4쿼터</div> | <div style=\"text-align: center;\">연장</div> | <div style=\"text-align: center;\">경기 결과</div> |\n')
        f.write('| --- | --- | --- | --- | --- | --- | --- | --- |\n')
        correct_count = 0
        total_count = 0
        for gameKey, gameData in content.items():
            max_n = gameData.get("metainfo", {}).get("max_n", -1)
            last_log = gameData.get(f"{max_n}", {})
            prob_winner = "home" if last_log.get("home") > last_log.get("away") else "away" if last_log.get("away") > last_log.get("home") else ""
            answer = prob_winner == gameData.get("metainfo", {}).get("winner")
            
            quarters = []
            for n, quarter in gameData.items():
              if n.isdigit() and quarter.get("total_sec", -1) in [600, 1200, 1800, 2400, 2700, 3000, 3300, 3600, 3900]:
                quarters.append((int(n), quarter))
            quarters.sort(key=lambda x: x[0])
            quarters_dict = {}
            for n, quarter in quarters:
              if quarter.get("total_sec", -1) ==600:
                quarters_dict["Q1"] = quarter
              elif quarter.get("total_sec", -1) ==1200:
                quarters_dict["Q2"] = quarter
              elif quarter.get("total_sec", -1) ==1800:
                quarters_dict["Q3"] = quarter
              elif quarter.get("total_sec", -1) ==2400:
                quarters_dict["Q4"] = quarter
              elif quarter.get("total_sec", -1) in [2700, 3000, 3300, 3600, 3900]:
                quarters_dict["연장"] = quarter
            
            f.write(f'| {gameKey} {answer and "✅" or "❌"}')
            f.write(f'| <pre style=\"border: none; background: none; padding: 0; margin: 0;\">home {gameData.get("metainfo", {}).get("home", "-")}<br>away {gameData.get("metainfo", {}).get("away", "-")}</pre>')
            f.write(f'| {quarter_to_str(quarters_dict.get("Q1", {}))} ')
            f.write(f'| {quarter_to_str(quarters_dict.get("Q2", {}))} ')
            f.write(f'| {quarter_to_str(quarters_dict.get("Q3", {}))} ')
            f.write(f'| {quarter_to_str(quarters_dict.get("Q4", {}))} ')
            f.write(f'| {quarter_to_str(quarters_dict.get("연장", {}))} ')
            f.write(f'| {winner_to_str(gameData.get("metainfo", {}).get("winner", "-"))} |\n')
            
            if answer: correct_count += 1
            total_count += 1
        accuracy = (correct_count / total_count * 100) if total_count > 0 else 0
        f.write(f'\n정확도: {accuracy:.2f}% ({correct_count}/{total_count})\n')
    print(f"[saved] table report -> {table_report_path}")

if __name__ == "__main__":
    report_path = Path("../models/03/combined/predict_report.json")
    main(report_path)