import json

def main():
  with open('report.json', 'r') as f:
    data = json.load(f)

  total = len(data)
  correct = 0
  for gameKey, item in data.items():
    last_quarter = item["metainfo"]["quarters"][-1]
    last_prob = item[last_quarter]
    predicted_winner = "home" if last_prob["home"] > last_prob["away"] else "away"
    actual_winner = item["metainfo"]["winner"]
    if predicted_winner == actual_winner:
      correct += 1
  
  accuracy = correct / total * 100
  print(f"Total games: {total}")
  print(f"Correct predictions: {correct}")
  print(f"Accuracy: {accuracy:.2f}%")
  
if __name__ == "__main__":
  main()