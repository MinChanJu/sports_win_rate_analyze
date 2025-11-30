from playwright.async_api import async_playwright
import asyncio, json, os


async def crawl_kbl_data(URL, seasonName, full_log):
    """
    KBL 웹사이트에서 문자중계 탭을 클릭한 후 각 쿼터별 데이터를 크롤링하는 함수
    """
    
    gameKey = URL.split("/")[-2]
    date = URL.split("/")[-1]

    SCORE_SELECTOR = "#root > main > div > div > div:nth-child(3) > div.record-summary > div:nth-child(1) > ul > li"
    MANAGER_SELECTOR = "#root > main > div > div > div:nth-child(3) > div.record-summary > div:nth-child(1) > ul > li > ul > li:nth-child(1) > span"

    GAME_TAB_SELECTOR = "#root > main > div.layout.grid-2 > div > ul.tab-style1.sticky > li:nth-child(2) > a"  # 경기 정보 탭
    HOME_SELECTOR = "#root > main > div.layout.grid-2 > div > div:nth-child(5) > div.table-1200 > table > tbody > tr > td:nth-child(2) > p"
    AWAY_SELECTOR = "#root > main > div.layout.grid-2 > div > div:nth-child(6) > div.table-1200 > table > tbody > tr > td:nth-child(2) > p"

    LOG_TAB_SELECTOR = "#root > main > div.layout.grid-2 > div > ul.tab-style1.sticky > li:nth-child(4) > a"  # 문자중계 탭
    TEAM_PREFIX = f"https://api.kbl.or.kr/match/getPreviewData/{date}/{gameKey}"  # 팀 정보 URL 접두사
    TARGET_PREFIX = f"https://api.kbl.or.kr/match/{gameKey}/text-cast?" # 문자중계 API URL 접두사

    # 각 쿼터 정보
    quarters = [
        {"name": "Q1", "radio_id": "radio0" },
        {"name": "Q2", "radio_id": "radio1" },
        {"name": "Q3", "radio_id": "radio2" },
        {"name": "Q4", "radio_id": "radio3" },
        {"name": "연장", "radio_id": "radio4" },
    ]

    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            )
            page.set_default_timeout(10000)

            metainfo = {
                "url": URL,
                "seasonName": seasonName,
                "gameKey": gameKey,
                "date": date,
                "home": {"name": "", "code": 0, "manager": "", "score": 0, "players": []},
                "away": {"name": "", "code": 0, "manager": "", "score": 0, "players": []},
                "winner": "",
            }

            async with page.expect_response(
                lambda r: r.url.startswith(TEAM_PREFIX)
            ) as resp_info:
                await page.goto(URL, wait_until="networkidle")
                await asyncio.sleep(0.1)
                if full_log:
                    print("페이지 로딩 완료")

            try:
                team_response = await resp_info.value
                team_data = await team_response.json()
                arr_data = team_data["arr_game"][0]
                metainfo["home"]["code"] = int(arr_data["HOME_TEAM"])
                metainfo["away"]["code"] = int(arr_data["AWAY_TEAM"])
                
                await page.wait_for_selector(SCORE_SELECTOR, timeout=1000)
                team_elements = await page.query_selector_all(SCORE_SELECTOR)
                for i, team_element in enumerate(team_elements):
                    score_elements = await team_element.query_selector_all("div > p")
                    metainfo["home" if i == 0 else "away"]["name"] = (
                        await score_elements[0].inner_text()
                    )
                    metainfo["home" if i == 0 else "away"]["score"] = int(
                        await score_elements[1].inner_text()
                    )
                metainfo["winner"] = (
                    "home"
                    if metainfo["home"]["score"] > metainfo["away"]["score"]
                    else (
                        "away"
                        if metainfo["home"]["score"] < metainfo["away"]["score"]
                        else "draw"
                    )
                )
                if full_log:
                    print(f"팀 정보 로딩 완료")
            except Exception as e:
                if full_log:
                    print("팀 정보 로딩 실패" + str(e))

            try:
                await page.wait_for_selector(MANAGER_SELECTOR, timeout=1000)
                manager_elements = await page.query_selector_all(MANAGER_SELECTOR)
                metainfo["home"]["manager"] = await manager_elements[0].inner_text()
                metainfo["away"]["manager"] = await manager_elements[1].inner_text()
                if full_log:
                    print(f"감독 정보 로딩 완료")
            except:
                if full_log:
                    print("감독 정보 로딩 실패")

            await page.wait_for_selector(GAME_TAB_SELECTOR, timeout=1000)
            await page.click(GAME_TAB_SELECTOR)
            await asyncio.sleep(0.1)
            if full_log:
                print("경기기록 페이지 이동완료")

            try:
                await page.wait_for_selector(HOME_SELECTOR, timeout=1000)
                home_elements = await page.query_selector_all(HOME_SELECTOR)
                metainfo["home"]["players"] = [
                    await p.inner_text() for p in home_elements
                ]
                if full_log:
                    print(
                        f"홈 팀 선수 정보 로딩 완료 총 {len(metainfo['home']['players'])}명"
                    )
            except:
                if full_log:
                    print("홈 팀 선수 정보 로딩 실패")

            try:
                await page.wait_for_selector(AWAY_SELECTOR, timeout=1000)
                away_elements = await page.query_selector_all(AWAY_SELECTOR)
                metainfo["away"]["players"] = [
                    await p.inner_text() for p in away_elements
                ]
                if full_log:
                    print(
                        f"어웨이 팀 선수 정보 로딩 완료 총 {len(metainfo['away']['players'])}명"
                    )
            except:
                if full_log:
                    print("어웨이 팀 선수 정보 로딩 실패")

            await page.wait_for_selector(LOG_TAB_SELECTOR, timeout=1000)
            await page.click(LOG_TAB_SELECTOR)
            await asyncio.sleep(0.1)
            if full_log:
                print("문자중계 페이지 이동완료")

            all_logs = []

            for quarter in quarters:
                try:
                    label_selector = f"label[for='{quarter['radio_id']}']"

                    async with page.expect_response(
                        lambda r: r.url.startswith(TARGET_PREFIX)
                    ) as resp_info:
                        await page.click(label_selector, timeout=2000)
                        await asyncio.sleep(0.1)
                    
                    res = await resp_info.value
                    data = await res.json()
                    all_logs.extend(data)

                except:
                    if full_log:
                        print(f"{quarter['name']} 처리 오류")

            await browser.close()
            return metainfo, all_logs

        except Exception as e:
            error_msg = str(e).split("\n")[0] if "\n" in str(e) else str(e)
            if full_log:
                print(f"크롤링 오류: {error_msg[:100]}...")
            if "browser" in locals():
                await browser.close()
            return metainfo, []


def save_results_to_file(metainfo, all_logs, file_path, full_log):
    json_data = {
        "metainfo": metainfo,
        "logs": all_logs,
    }

    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

    if full_log:
        print(f"결과를 {file_path}에 저장했습니다.")


async def kbl_game_crawler(URL, file_path, full_log=False):
    """
    메인 실행 함수
    """
    if full_log:
        print("========================================")
        print(f"KBL {'/'.join(URL.split('/')[-2:])} 크롤링 실행중...")

    # 크롤링 실행
    seasonName = file_path.split("/")[-2]
    metainfo, all_logs = await crawl_kbl_data(URL, seasonName, full_log)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    if all_logs:
        if full_log:
            print(f"크롤링 완료: {all_logs[-1]['q']}쿼터")
        save_results_to_file(metainfo, all_logs, file_path, full_log)
        if not full_log:
            print(
                f"KBL {'/'.join(URL.split('/')[-2:])} ({metainfo['home']['name']} vs {metainfo['away']['name']}) 크롤링 완료, last quarter: {all_logs[-1]['q']} => '{file_path}'에 저장됨"
            )
    else:
        print(f"KBL {'/'.join(URL.split('/')[-2:])} 크롤링 실패")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "metainfo": {
                            "url": URL,
                            "seasonName": seasonName,
                            "gameKey": URL.split("/")[-2],
                            "date": URL.split("/")[-1],
                            "home": {"name": "error", "score": 0, "players": []},
                            "away": {"name": "error", "score": 0, "players": []},
                            "winner": "error",
                        }
                    },
                    indent=2,
                    ensure_ascii=False,
                )
            )
    if full_log:
        print("========================================")


if __name__ == "__main__":
    gameKeys = {
        '2022-2023': ['S41G01N171/20230128', 'S41G01N243/20230317'],
    }
    for seasonName in gameKeys.keys():
        for game in gameKeys[seasonName]:
            URL = f"https://kbl.or.kr/match/record/{game}"
            FILE_PATH = f"../kbl_log_data/{seasonName}/{URL.split('/')[-2]}.json"
            asyncio.run(kbl_game_crawler(URL, FILE_PATH, True))
