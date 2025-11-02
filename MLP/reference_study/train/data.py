from collections import Counter, defaultdict
from config import get_args
from pathlib import Path
import pandas as pd
import numpy as np
import random
import json

DEFAULT_DROP_COLS = ["gameKey", "seasonName", "date", "quarter", "split"]
team_code_path = Path(__file__).parent / "teamcode.json"

def _prepare_xy(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    if team_code_path.exists(): data = json.loads(team_code_path.read_text())
    else: data = {"team_code": {}, "idx": 0}

    team_code = data.get("team_code", {})
    next_idx = data.get("idx", 0)

    teams_in_df = pd.concat([df["H_TEAM"], df["A_TEAM"]]).unique()
    for team in teams_in_df:
        if team not in team_code:
            team_code[team] = next_idx
            next_idx += 1

    data["team_code"] = team_code
    data["idx"] = next_idx
    
    team_code_path.write_text(json.dumps(data, ensure_ascii=False, indent=2))

    drop_cols = [c for c in DEFAULT_DROP_COLS if c in df.columns]
    df = df.drop(columns=drop_cols)
    df["winner"] = df["winner"].map({"home": 0, "away": 1})
    df["H_TEAM"] = df["H_TEAM"].map(team_code)
    df["A_TEAM"] = df["A_TEAM"].map(team_code)
    X = df.drop("winner", axis=1).values.astype(np.float32)
    y = df["winner"].values.astype(np.int64)
    return X, y


def _heuristic_assign_splits(
    games_df: pd.DataFrame,
    test_size: float,
    valid_size: float,
    seed: int,
    ha_gap_target: int = 1,
    iters: int = 20000,          # 반복 횟수 (원하면 증가)
    no_improve_patience: int = 4000,
    verbose: bool = False,
):
    rnd = random.Random(seed)
    G = games_df["gameKey"].tolist()
    teams = sorted(pd.unique(games_df[["H_TEAM","A_TEAM"]].values.ravel()))
    N = len(G)
    N_test  = int(round(N*test_size))
    N_valid = int(round(N*valid_size))
    N_train = N - N_test - N_valid
    sizes = {"train":N_train, "valid":N_valid, "test":N_test}
    SPLITS = ["train","valid","test"]

    # 초기 배정: 랜덤으로 세트 크기 맞춰 분배
    rnd.shuffle(G)
    assign = {}
    for i,g in enumerate(G):
        if i < N_train: assign[g]="train"
        elif i < N_train+N_valid: assign[g]="valid"
        else: assign[g]="test"

    # 빠른 조회
    home_of = {r["gameKey"]: r["H_TEAM"] for _,r in games_df.iterrows()}
    away_of = {r["gameKey"]: r["A_TEAM"] for _,r in games_df.iterrows()}

    # 카운트 테이블
    C = defaultdict(lambda: Counter())       # 팀-세트 총경기
    H = defaultdict(lambda: Counter())       # 팀-세트 홈
    A = defaultdict(lambda: Counter())       # 팀-세트 원정

    for g,s in assign.items():
        ht, at = home_of[g], away_of[g]
        C[ht][s]+=1; C[at][s]+=1
        H[ht][s]+=1; A[at][s]+=1

    # 목표치
    team_total = {t: sum(C[t][s] for s in SPLITS) for t in teams}
    ratio = {"train":N_train/N, "valid":N_valid/N, "test":N_test/N}
    target = {t:{s: ratio[s]*team_total[t] for s in SPLITS} for t in teams}

    def team_penalty(t, s):
        # 총경기수 편차 + 홈/원정 차이(ha_gap_target 넘어가면 큰 페널티)
        alpha, beta, gamma = 1.0, 0.25, 3.0
        p1 = abs(C[t][s] - target[t][s])
        p2 = abs(H[t][s] - A[t][s])
        p3 = max(0, p2 - ha_gap_target)  # 초과분에 페널티
        return alpha*p1 + beta*p2 + gamma*p3

    def total_cost():
        return sum(team_penalty(t,s) for t in teams for s in SPLITS)

    def apply_move(g, s_from, s_to):
        if s_from == s_to: return
        ht, at = home_of[g], away_of[g]
        # remove
        C[ht][s_from]-=1; C[at][s_from]-=1
        H[ht][s_from]-=1; A[at][s_from]-=1
        # add
        C[ht][s_to]+=1; C[at][s_to]+=1
        H[ht][s_to]+=1; A[at][s_to]+=1
        assign[g]=s_to

    # 힐클라임: (1) 같은 두 세트 간 swap, (2) 보정 이동
    best_cost = total_cost()
    no_improve = 0
    if verbose: print(f"[HEU] init cost={best_cost:.2f}")

    for it in range(iters):
        if no_improve > no_improve_patience: break

        # 50%: swap (세트 크기 유지), 50%: move(+보정)
        if rnd.random() < 0.5:
            # swap
            g1, g2 = rnd.sample(G, 2)
            s1, s2 = assign[g1], assign[g2]
            if s1 == s2: 
                no_improve += 1
                continue

            # delta 계산 (간단히 재계산)
            prev = best_cost
            # 적용
            apply_move(g1, s1, s2)
            apply_move(g2, s2, s1)
            new_cost = total_cost()
            if new_cost <= prev:
                best_cost = new_cost
                no_improve = 0
            else:
                # rollback
                apply_move(g1, s2, s1)
                apply_move(g2, s1, s2)
                no_improve += 1
        else:
            # move: s_from -> s_to, 대신 s_to에서 하나 끌어와 균형 유지
            g1 = rnd.choice(G)
            s_from = assign[g1]
            s_to = rnd.choice([s for s in SPLITS if s!=s_from])

            # s_to에서 아무거나 하나 골라 역방향 이동해 세트 크기 유지
            cand = [g for g in G if assign[g]==s_to]
            if not cand:
                no_improve += 1
                continue
            g2 = rnd.choice(cand)

            prev = best_cost
            apply_move(g1, s_from, s_to)
            apply_move(g2, s_to, s_from)
            new_cost = total_cost()
            if new_cost <= prev:
                best_cost = new_cost
                no_improve = 0
            else:
                # rollback
                apply_move(g1, s_to, s_from)
                apply_move(g2, s_from, s_to)
                no_improve += 1

    if verbose: print(f"[HEU] final cost={best_cost:.2f}")
    return assign


def load_single_csv(path: str | Path, seed: int = None) -> dict[str, dict[str, np.ndarray]]:
    args = get_args()
    test_size = args.test_size
    valid_size = args.valid_size
    seed = args.split_seed if seed is None else seed

    df = pd.read_csv(path)

    # ── game 단위 테이블 (쿼터 중복 제거) ─────────────────────────
    games = (df.drop_duplicates("gameKey")
               [["gameKey", "H_TEAM", "A_TEAM"]]
               .reset_index(drop=True))

    # ── 1) 휴리스틱으로 배정 ─────────────────────────────────────────
    key2split = _heuristic_assign_splits(
        games_df=games,
        test_size=test_size,
        valid_size=valid_size,
        seed=seed,
        ha_gap_target=1,
        iters=20000,
        no_improve_patience=4000,
    )

    # ── 원본 df에 split 조인 ────────────────────────────────────
    df = df.merge(
        pd.DataFrame({"gameKey": list(key2split.keys()),
                      "split":   list(key2split.values())}),
        on="gameKey", how="left"
    )

    # ── 세트별 분할 후 X,y 준비 ─────────────────────────────────
    train_df = df[df["split"] == "train"]
    valid_df = df[df["split"] == "valid"]
    test_df  = df[df["split"] == "test"]

    X_train, y_train = _prepare_xy(train_df)
    X_valid, y_valid = _prepare_xy(valid_df)
    X_test,  y_test  = _prepare_xy(test_df)

    return {
        "train": {"X": X_train, "y": y_train},
        "valid": {"X": X_valid, "y": y_valid},
        "test": {"X": X_test, "y": y_test},
    }

def load_multi_csv(paths: list[str | Path]) -> dict[str, dict[str, np.ndarray]]:
    args = get_args()
    seed = args.split_seed
    
    X_train = y_train = X_valid = y_valid = X_test = y_test = None

    for i, path in enumerate(paths):
        if not Path(path).exists():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {path}")

        data_path = load_single_csv(path, seed + i)  # 시드 변경하여 데이터 분할 다르게

        X_train = np.vstack([X_train, data_path["train"]["X"]]) if X_train is not None else data_path["train"]["X"]
        y_train = np.hstack([y_train, data_path["train"]["y"]]) if y_train is not None else data_path["train"]["y"]
        X_valid = np.vstack([X_valid, data_path["valid"]["X"]]) if X_valid is not None else data_path["valid"]["X"]
        y_valid = np.hstack([y_valid, data_path["valid"]["y"]]) if y_valid is not None else data_path["valid"]["y"]
        X_test  = np.vstack([X_test, data_path["test"]["X"]]) if X_test is not None else data_path["test"]["X"]
        y_test  = np.hstack([y_test, data_path["test"]["y"]]) if y_test is not None else data_path["test"]["y"]

    return {
        "train": {"X": X_train, "y": y_train},
        "valid": {"X": X_valid, "y": y_valid},
        "test": {"X": X_test, "y": y_test},
    }
    
if __name__ == "__main__":
    data = load_multi_csv([
        "../kbl_data_quarter_csv/2021-2022.csv",
        "../kbl_data_quarter_csv/2022-2023.csv",
        "../kbl_data_quarter_csv/2023-2024.csv",
        "../kbl_data_quarter_csv/2024-2025.csv",
    ])
    for split in ["train", "valid", "test"]:
        print(f"{split}: X={data[split]['X'].shape}, y={data[split]['y'].shape}")