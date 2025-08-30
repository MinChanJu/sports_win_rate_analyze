import json, os, re


def analyze_json_files(log_file_path, root_folder, start=1, end=270):
    total_summary = {}
    pattern = re.compile(r"S\d+G\d+N(\d+)\.json$")
    check_log = ""

    for name in sorted(os.listdir(root_folder)):
        print(name)
        sub_path = os.path.join(root_folder, name)
        if os.path.isdir(sub_path):
            check_log += f"======================================== [{name}] file check ========================================\n"
            files = os.listdir(sub_path)
            files.sort(
                key=lambda x: (
                    int(re.search(r"S\d+G\d+N(\d+)\.json$", x).group(1))
                    if re.search(r"S\d+G\d+N(\d+)\.json$", x)
                    else float("inf")
                )
            )
            count = len(files)
            wrong_files = []
            existing_files = set()
            for file in files:
                match = pattern.match(file)
                if match:
                    existing_files.add(int(match.group(1)))
                    file_path = os.path.join(sub_path, file)
                    with open(file_path, "r") as f:
                        content = f.read().strip()
                        json_content = json.loads(content)
                        check_log += f"{file}: {json_content['metainfo']['date']} ({json_content['metainfo']['home']['name']} vs {json_content['metainfo']['away']['name']})"
                        check_log += f" [{', '.join([f'{quarter}({len(json_content[quarter])})' for quarter in json_content['metainfo']['quarters']])}]"
                        if (
                            "Q1" in json_content
                            and "Q2" in json_content
                            and "Q3" in json_content
                            and "Q4" in json_content
                        ):
                            check_log += " ✅\n"
                        else:
                            check_log += " ❌\n"
                            wrong_files.append(
                                "'"
                                + "/".join(
                                    json_content["metainfo"]["url"].split("/")[-2:]
                                )
                                + "'"
                            )

            # 빠진 번호 찾기
            missing_files = [
                f"{files[0][:6]}N{i}"
                for i in range(start, end + 1)
                if i not in existing_files
            ]

            total_summary[name] = {
                "count": count,
                "wrong_files": wrong_files,
                "missing_files": missing_files,
            }

            check_log += f"총 {count}개의 .json 파일\n"
            if wrong_files:
                check_log += (
                    f"❌ 잘못된 파일 ({len(wrong_files)}): {', '.join(wrong_files)}\n"
                )
            else:
                check_log += "✅ 잘못된 파일 없음\n"

            if missing_files:
                check_log += (
                    f"❌ 빠진 번호 ({len(missing_files)}): {', '.join(missing_files)}\n"
                )
            else:
                check_log += "✅ 빠진 번호 없음\n"

    check_log += f"======================================== kbl_data total summary ========================================\n"
    check_log += (
        f"총 합계: {sum(v['count'] for v in total_summary.values())}개의 .json 파일\n"
    )
    for k, v in total_summary.items():
        if v["count"]:
            check_log += f" - {k}: {v['count']}개\n"
    check_log += f"총 잘못된 파일: {sum(len(v['wrong_files']) for v in total_summary.values())}개\n"
    for k, v in total_summary.items():
        if v["wrong_files"]:
            check_log += (
                f" - {k} ({len(v['wrong_files'])}): {', '.join(v['wrong_files'])}\n"
            )
    check_log += f"총 빠진 번호: {sum(len(v['missing_files']) for v in total_summary.values())}개\n"
    for k, v in total_summary.items():
        if v["missing_files"]:
            check_log += (
                f" - {k} ({len(v['missing_files'])}): {', '.join(v['missing_files'])}\n"
            )
    check_log += "================================================= copy =================================================\n"
    for k, v in total_summary.items():
        if v["wrong_files"]:
            check_log += f"'{k}': [{', '.join(v['wrong_files'])}],\n"
    check_log += "========================================================================================================\n"

    with open(log_file_path, "w") as log_file:
        log_file.write(check_log)
        print(f"Log written to '{log_file_path}'")


# 사용 예시
root = "../kbl_data"
analyze_json_files("file_check.log", root)
