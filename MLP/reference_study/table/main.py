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

def main():
    with open('../predict/report.json', 'r') as f:
        content = json.load(f)

    with open('report.md', 'w', encoding='utf-8') as f:
        f.write('| <div style=\"text-align: center;\">게임키</div> | <div style=\"text-align: center;\">팀</div> | <div style=\"text-align: center;\">1쿼터</div> | <div style=\"text-align: center;\">2쿼터</div> | <div style=\"text-align: center;\">3쿼터</div> | <div style=\"text-align: center;\">4쿼터</div> | <div style=\"text-align: center;\">연장</div> | <div style=\"text-align: center;\">경기 결과</div> |\n')
        f.write('| --- | --- | --- | --- | --- | --- | --- | --- |\n')
        correct_count = 0
        total_count = 0
        for gameKey, quarters in content.items():
            f.write(f'| {gameKey} ')
            f.write(f'| <pre style=\"border: none; background: none; padding: 0; margin: 0;\">home {quarters.get("metainfo", {}).get("home", "-")}<br>away {quarters.get("metainfo", {}).get("away", "-")}</pre>')
            f.write(f'| {quarter_to_str(quarters.get("Q1", {}))} ')
            f.write(f'| {quarter_to_str(quarters.get("Q2", {}))} ')
            f.write(f'| {quarter_to_str(quarters.get("Q3", {}))} ')
            f.write(f'| {quarter_to_str(quarters.get("Q4", {}))} ')
            f.write(f'| {quarter_to_str(quarters.get("연장", {}))} ')
            f.write(f'| {winner_to_str(quarters.get("metainfo", {}).get("winner", "-"))} |\n')
            last_quarter = quarters.get("연장", quarters.get("Q4", {}))
            prob_winner = "home" if last_quarter.get("home") > last_quarter.get("away") else "away" if last_quarter.get("away") > last_quarter.get("home") else ""
            if prob_winner == quarters.get("metainfo", {}).get("winner"):
                correct_count += 1
            total_count += 1
        accuracy = (correct_count / total_count * 100) if total_count > 0 else 0
        f.write(f'\n정확도: {accuracy:.2f}% ({correct_count}/{total_count})\n')
    print(f"[saved] metadata -> report.md")

if __name__ == "__main__":
    main()