from pathlib import Path
from config import get_args
import numpy as np
import pandas as pd
import random
import torch

def load_state(ckpt_path: Path):
    ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    if isinstance(ckpt, dict) and "state_dict" in ckpt:
        return ckpt["state_dict"], {k: v for k, v in ckpt.items() if k != "state_dict"}
    return ckpt, {}

DEFAULT_DROP_COLS = ["gameKey", "seasonName", "date", "winner", "n"]

def load_single_csv(csv_path: str | Path) -> tuple[np.ndarray, np.ndarray]:
    df = pd.read_csv(csv_path)
    drop_df = df.drop(columns=DEFAULT_DROP_COLS)
    return df, drop_df
    
def load_multi_csv(csv_folder_list: list[Path], test_game_keys: list[str] | None) -> tuple[pd.DataFrame, pd.DataFrame, str] | None:
    total_csv_paths: list[Path] = []
    for folder in csv_folder_list:
        csv_paths = list(folder.glob("*.csv"))
        total_csv_paths.extend(csv_paths)
    
    args = get_args()
    
    if test_game_keys is not None:
        total_csv_paths = [path for path in total_csv_paths if path.stem in test_game_keys]
        if not total_csv_paths:
            print("테스트용 CSV 파일이 없습니다.")
            return None
    
    random.seed(args.seed)
    specific_csv_path = random.choice(total_csv_paths)
    gameKey = specific_csv_path.stem
    print(f"선택된 CSV 파일: {specific_csv_path}")
    
    df, drop_df = load_single_csv(csv_path=specific_csv_path)

    return df, drop_df, gameKey

if __name__ == "__main__":
    csv_folder_list = [
        Path("../kbl_real_time_csv/2021-2022"),
        Path("../kbl_real_time_csv/2022-2023"),
        Path("../kbl_real_time_csv/2023-2024"),
        Path("../kbl_real_time_csv/2024-2025"),
    ]
    
    test_game_keys = [
        "S45G01N115",
        "S43G01N105",
        "S45G01N40",
        "S41G01N184",
        "S41G01N22",
        "S43G01N234",
        "S43G01N166",
        "S45G01N53",
        "S43G01N81",
        "S45G01N257",
        "S45G01N133",
        "S39G01N229",
        "S39G01N267",
        "S41G01N114",
        "S41G01N149",
        "S41G01N4",
        "S43G01N232",
        "S43G01N192",
        "S45G01N150",
        "S43G01N100",
        "S41G01N175",
        "S39G01N54",
        "S45G01N91",
        "S43G01N168",
        "S43G01N28",
        "S43G01N39",
        "S45G01N206",
        "S41G01N240",
        "S39G01N240",
        "S39G01N156",
        "S39G01N3",
        "S41G01N77",
        "S39G01N23",
        "S43G01N216",
        "S43G01N175",
        "S43G01N4",
        "S41G01N93",
        "S45G01N107",
        "S43G01N264",
        "S43G01N33",
        "S41G01N249",
        "S39G01N221",
        "S43G01N145",
        "S43G01N2",
        "S39G01N170",
        "S45G01N258",
        "S39G01N234",
        "S45G01N96",
        "S43G01N238",
        "S41G01N260",
        "S43G01N91",
        "S43G01N154",
        "S39G01N18",
        "S41G01N123",
        "S39G01N181",
        "S43G01N221",
        "S43G01N5",
        "S45G01N7",
        "S43G01N99",
        "S39G01N82",
        "S43G01N218",
        "S41G01N266",
        "S39G01N114",
        "S43G01N53",
        "S45G01N158",
        "S45G01N229",
        "S45G01N13",
        "S39G01N141",
        "S41G01N67",
        "S43G01N7",
        "S41G01N2",
        "S43G01N114",
        "S45G01N160",
        "S43G01N82",
        "S45G01N20",
        "S39G01N45",
        "S41G01N194",
        "S43G01N253",
        "S41G01N238",
        "S39G01N125",
        "S43G01N156",
        "S43G01N84",
        "S45G01N154",
        "S39G01N13",
        "S45G01N134",
        "S39G01N200",
        "S39G01N46",
        "S41G01N219",
        "S39G01N73",
        "S41G01N109",
        "S39G01N196",
        "S45G01N125",
        "S39G01N126",
        "S41G01N261",
        "S45G01N45",
        "S45G01N175",
        "S43G01N167",
        "S45G01N245",
        "S43G01N49",
        "S39G01N233",
        "S39G01N92",
        "S41G01N218",
        "S39G01N239",
        "S39G01N182",
        "S45G01N140",
        "S45G01N139",
        "S41G01N171",
        "S43G01N190",
        "S45G01N262",
        "S41G01N153",
        "S45G01N195",
        "S43G01N16",
        "S43G01N111",
        "S41G01N51",
        "S41G01N3",
        "S39G01N231",
        "S41G01N42",
        "S43G01N263",
        "S45G01N249",
        "S41G01N255",
        "S41G01N213",
        "S39G01N115",
        "S45G01N161",
        "S41G01N151",
        "S43G01N164",
        "S41G01N211",
        "S39G01N138",
        "S41G01N221",
        "S43G01N256",
        "S41G01N127",
        "S39G01N243",
        "S41G01N69",
        "S43G01N55",
        "S45G01N264",
        "S39G01N94",
        "S39G01N36",
        "S41G01N94",
        "S45G01N110",
        "S41G01N150",
        "S41G01N98",
        "S43G01N268",
        "S41G01N91",
        "S39G01N129",
        "S43G01N209",
        "S41G01N11",
        "S41G01N59",
        "S45G01N165",
        "S39G01N91",
        "S41G01N124",
        "S45G01N66",
        "S43G01N243",
        "S45G01N4",
        "S45G01N61",
        "S45G01N180",
        "S41G01N83",
        "S39G01N147",
        "S43G01N194",
        "S39G01N203",
        "S41G01N267",
        "S39G01N64",
        "S45G01N29",
        "S43G01N43",
        "S39G01N187",
        "S45G01N255",
        "S39G01N48",
        "S43G01N196",
        "S43G01N169",
        "S43G01N25",
        "S43G01N182",
        "S39G01N144",
        "S39G01N31",
        "S45G01N156",
        "S43G01N137",
        "S45G01N22",
        "S45G01N152",
        "S39G01N143",
        "S39G01N168",
        "S43G01N128",
        "S45G01N132",
        "S39G01N202",
        "S41G01N97",
        "S39G01N62",
        "S45G01N82",
        "S41G01N45",
        "S43G01N132",
        "S45G01N89",
        "S39G01N123",
        "S45G01N203",
        "S39G01N237",
        "S41G01N189",
        "S45G01N63",
        "S41G01N270",
        "S45G01N88",
        "S45G01N192",
        "S41G01N196",
        "S41G01N99",
        "S41G01N167",
        "S39G01N119",
        "S43G01N224",
        "S41G01N90",
        "S45G01N37",
        "S43G01N152",
        "S39G01N87",
        "S39G01N247",
        "S39G01N113",
        "S39G01N140",
        "S43G01N149",
        "S39G01N188",
        "S39G01N103",
        "S43G01N176",
        "S41G01N16",
        "S41G01N38",
        "S45G01N41",
        "S41G01N71",
        "S41G01N121",
        "S39G01N206"
    ]
    
    df, drop_df, gameKey = load_multi_csv(csv_folder_list, test_game_keys)
    
    print("데이터 로드 완료.")
    print(f"총 데이터 개수: {df.shape[0]}")
    print(f"특징 개수: {len(df['gameKey'].values)}")
    print(f"선택된 게임 키: {gameKey}")
    print(drop_df.shape)