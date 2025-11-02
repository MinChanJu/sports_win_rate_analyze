from pathlib import Path
from collections import Counter, defaultdict
import random
import pandas as pd
import torch

def load_state(ckpt_path: Path):
    ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    if isinstance(ckpt, dict) and "state_dict" in ckpt:
        return ckpt["state_dict"], {k: v for k, v in ckpt.items() if k != "state_dict"}
    return ckpt, {}

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

def load_csv_path(csv_path: Path, team_code: dict, config: dict = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.read_csv(csv_path)
    if config is not None:
        test_size  = config.get("test_size", 0.2)
        valid_size = config.get("valid_size", 0.1)
        seed       = config.get("split_seed", 42)
        games = (df.drop_duplicates("gameKey")
               [["gameKey", "H_TEAM", "A_TEAM"]]
               .reset_index(drop=True))
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
        
        df  = df[df["split"] == "test"]
        df.drop(columns=["split"], inplace=True)
        
        print(f"Loaded {len(df)} rows from {csv_path} for prediction (seed={seed})")
    else:
        print(f"Loaded {len(df)} rows from {csv_path} for prediction (no split)")
    
    drop_df = df.drop(columns=["gameKey", "seasonName", "date", "quarter", "winner"])
    drop_df["H_TEAM"] = drop_df["H_TEAM"].map(team_code)
    drop_df["A_TEAM"] = drop_df["A_TEAM"].map(team_code)
    
    return df, drop_df

def load_csv_paths(csv_path_list: list[Path], team_code: dict, seed: int = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    df_list = [load_csv_path(csv_path, team_code, seed) for csv_path in csv_path_list]
    df = pd.concat([d[0] for d in df_list], ignore_index=True)
    drop_df = pd.concat([d[1] for d in df_list], ignore_index=True)
    return df, drop_df