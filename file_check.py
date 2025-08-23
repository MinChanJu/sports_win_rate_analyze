import os
import re

def analyze_json_files(root_folder, start=1, end=270):
    result = {}
    total = 0
    pattern = re.compile(r"S\d+G\d+N(\d+)_results\.json$")

    for name in os.listdir(root_folder):
        sub_path = os.path.join(root_folder, name)
        if os.path.isdir(sub_path):
            files = [f for f in os.listdir(sub_path) if f.endswith(".json")]

            # 파일 개수
            count = len(files)
            total += count

            # 존재하는 번호 추출
            existing = set()
            for f in files:
                match = pattern.match(f)
                if match:
                    existing.add(int(match.group(1)))

            # 빠진 번호 찾기
            missing = [i for i in range(start, end + 1) if i not in existing]

            result[name] = {
                "count": count,
                "missing": missing
            }

    return result, total

# 사용 예시
root = "kbl_data"
analysis, total = analyze_json_files(root)

print(f"{root} 폴더 분석 결과")
for folder, info in analysis.items():
    print(f"[{folder}] {info['count']}개의 .json 파일")
    if info["missing"]:
        print("   빠진 번호:", info["missing"])
    else:
        print("   빠진 번호 없음 ✅")

print(f"\n총 합계: {total}개의 .json 파일")