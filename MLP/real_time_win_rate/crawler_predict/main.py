from data import load_state, transform_stats_to_array
from crawler_log import crawl_all_logs, crawl_meta_data, close_browser
from win_rate_graph import draw_win_rate_graph
from kbl_decoder import kbl_log_decoder
from predict import predict_one
from device import get_device
from config import get_args
from pathlib import Path
from model import MLP
import asyncio
import signal
import json
import sys


async def main(URL: str):
    args = get_args()

    model_path = Path(args.model_dir) / f"{args.model_type}" / "best_model.pt"
    if not model_path.exists():
        print(f"체크포인트 파일이 없습니다: {model_path}")
        sys.exit(1)

    model_info_path = Path(args.model_dir) / f"{args.model_type}" / "best_model.json"
    if not model_info_path.exists():
        print(f"모델 정보 파일이 없습니다: {model_info_path}")
        sys.exit(1)

    device = get_device()
    in_dim = 88
    model = MLP(in_dim).to(device)
    state_dict, _ = load_state(model_path)
    model.load_state_dict(state_dict)
    model.eval()

    record = []

    def signal_handler(sig, frame):
        print("종료 신호를 받아 예측 기록을 저장합니다.")
        with open("predict_log.json", "w", encoding="utf-8") as f:
            json.dump(record, f, ensure_ascii=False, indent=4)
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    meta_data = await crawl_meta_data(URL)
    if meta_data is None:
        print("메타데이터 크롤링에 실패하여 예측을 종료합니다.")
        await close_browser()
        sys.exit(1)

    h_code = meta_data["home"]["code"]
    a_code = meta_data["away"]["code"]

    h_name = meta_data["home"]["name"]
    a_name = meta_data["away"]["name"]

    print("실시간 승률 예측 시작")
    print(f"경기 URL: {URL}")
    print("경기 정보:")
    print(f"    - 팀 정보: 팀 이름 (팀 코드)")
    print(f"    - home: {h_name} ({h_code})")
    print(f"    - away: {a_name} ({a_code})")
    print("종료하려면 Ctrl+C를 누르세요.\n")

    print(
        f"{'Quarter':<8} {'Time':<6} {'score':<10} {'Home Win%':<12} {'Away Win%':<12} {'log count':<10} {'total sec':<10}"
    )

    all_logs = []
    backup_logs = None
    log_idx = 0
    while True:
        # crawl_logs = await crawl_all_logs(URL)

        # if crawl_logs is None:
        #     print("크롤링에 실패하여 예측을 종료합니다.")
        #     await close_browser()
        #     sys.exit(1)

        # if len(crawl_logs) <= len(all_logs):
        #     continue  # 이전보다 로그가 적으면 무시

        if backup_logs is None:
            backup_logs = await crawl_all_logs(URL)

        if backup_logs is None:
            await asyncio.sleep(10)
            continue

        if len(backup_logs) > log_idx:
            log_idx += 1
            crawl_logs = backup_logs[:log_idx]
        else:
            await close_browser()
            continue

        all_logs = crawl_logs
        game_stats = kbl_log_decoder(all_logs, h_code, a_code)

        x_row = transform_stats_to_array(game_stats)
        home_prob, away_prob = predict_one(model, x_row, device)

        last_log = all_logs[-1]
        last_min = int(last_log["m"])
        last_sec = int(last_log["s"])
        last_time = f"{last_min:02}:{last_sec:02}"
        last_quarter = last_log["q"]
        last_time_sec = (
            600 - (last_min * 60 + last_sec)
            if last_quarter.startswith("Q")
            else 300 - (last_min * 60 + last_sec)
        )

        total_time_sec = (
            ((int(last_quarter[1]) - 1) * 10 * 60 + last_time_sec)
            if last_quarter.startswith("Q")
            else (
                2400 + (int(last_quarter[1]) - 1) * 5 * 60 + last_time_sec
                if last_quarter.startswith("X")
                else None
            )
        )

        if total_time_sec is None:
            print(f"알 수 없는 쿼터 정보입니다: {last_quarter}")
            await close_browser()
            sys.exit(1)

        gam = f"{game_stats['home']['PP']} - {game_stats['away']['PP']}"
        print(
            f"{last_quarter:<8} {last_time:<6} {gam:<10} {home_prob*100:<12.2f} {away_prob*100:<12.2f} {len(all_logs):<10} {total_time_sec:<10}"
        )

        if record and record[-1]["total_time_sec"] == total_time_sec:
            record[-1] = {
                "home_code": h_code,
                "away_code": a_code,
                "home_win_rate": home_prob,
                "away_win_rate": away_prob,
                "quarter": last_quarter,
                "time": last_time,
                "total_time_sec": total_time_sec,
            }
        else:
            record.append(
                {
                    "home_code": h_code,
                    "away_code": a_code,
                    "home_win_rate": home_prob,
                    "away_win_rate": away_prob,
                    "quarter": last_quarter,
                    "time": last_time,
                    "total_time_sec": total_time_sec,
                }
            )

        draw_win_rate_graph(record, URL)

        # await asyncio.sleep(10)  # 10초 대기


if __name__ == "__main__":
    # URL = "https://kbl.or.kr/match/record/S48G01N18/20251202"
    # URL = "https://kbl.or.kr/match/record/S47G01N84/20251204"  # 12월 5일 경기 예시
    URL = "https://kbl.or.kr/match/record/S47G01N86/20251205"  # 12월 5일 경기 예시

    asyncio.run(main(URL))
