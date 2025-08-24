from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import asyncio, json, os


async def crawl_kbl_data(URL, seasonName, full_log):
    """
    KBL 웹사이트에서 문자중계 탭을 클릭한 후 각 쿼터별 데이터를 크롤링하는 함수
    """

    SCORE_SELECTOR = "#root > main > div > div > div:nth-child(3) > div.record-summary > div:nth-child(1) > ul > li"

    GAME_TAB_SELECTOR = "#root > main > div.layout.grid-2 > div > ul.tab-style1.sticky > li:nth-child(2) > a"  # 경기 정보 탭
    HOME_SELECTOR = "#root > main > div.layout.grid-2 > div > div:nth-child(5) > div.table-1200 > table > tbody > tr > td:nth-child(2) > p"
    AWAY_SELECTOR = "#root > main > div.layout.grid-2 > div > div:nth-child(6) > div.table-1200 > table > tbody > tr > td:nth-child(2) > p"
    
    LOG_TAB_SELECTOR = "#root > main > div.layout.grid-2 > div > ul.tab-style1.sticky > li:nth-child(4) > a"  # 문자중계 탭
    TABLE_SELECTOR = "#root > main > div > div > div > div.sms-broadcast-table > table > tbody"  # 테이블 데이터
    
    # 각 쿼터 정보
    quarters = [
        {"name": "Q1", "radio_id": "radio0", "data_key": "Q1"},
        {"name": "Q2", "radio_id": "radio1", "data_key": "Q2"},
        {"name": "Q3", "radio_id": "radio2", "data_key": "Q3"},
        {"name": "Q4", "radio_id": "radio3", "data_key": "Q4"},
        {"name": "연장", "radio_id": "radio4", "data_key": "X1,X2,X3,X4,X5"}
    ]
    
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
            page.set_default_timeout(10000)
            
            metainfo = {
                "url": URL,
                "seasonName": seasonName,
                "gameKey": URL.split('/')[-2],
                "date": URL.split("/")[-1],
                "home": {"name": "", "score": 0, "players": []},
                "away": {"name": "", "score": 0, "players": []},
                "winner": "",
                "quarters": []
            }
            
            await page.goto(URL, wait_until="networkidle")
            if full_log: print("페이지 로딩 완료")

            try:
                await page.wait_for_selector(SCORE_SELECTOR, timeout=1000)
                team_elements = await page.query_selector_all(SCORE_SELECTOR)
                for i, team_element in enumerate(team_elements):
                    score_elements = await team_element.query_selector_all("div > p")
                    metainfo["home" if i == 0 else "away"]["name"] = await score_elements[0].inner_text()
                    metainfo["home" if i == 0 else "away"]["score"] = int(await score_elements[1].inner_text())
                metainfo["winner"] = "home" if metainfo["home"]["score"] > metainfo["away"]["score"] else "away" if metainfo["home"]["score"] < metainfo["away"]["score"] else "draw"
                if full_log: print(f"팀 정보 로딩 완료")
            except:
                if full_log: print("팀 정보 로딩 실패")

            await page.wait_for_selector(GAME_TAB_SELECTOR, timeout=1000)
            await page.click(GAME_TAB_SELECTOR)
            if full_log: print("경기기록 페이지 이동완료")

            try:
                await page.wait_for_selector(HOME_SELECTOR, timeout=1000)
                home_elements = await page.query_selector_all(HOME_SELECTOR)
                metainfo["home"]["players"] = [await p.inner_text() for p in home_elements]
                if full_log: print(f"홈 팀 선수 정보 로딩 완료 총 {len(metainfo['home']['players'])}명")
            except:
                if full_log: print("홈 팀 선수 정보 로딩 실패")

            try:
                await page.wait_for_selector(AWAY_SELECTOR, timeout=1000)
                away_elements = await page.query_selector_all(AWAY_SELECTOR)
                metainfo["away"]["players"] = [await p.inner_text() for p in away_elements]
                if full_log: print(f"어웨이 팀 선수 정보 로딩 완료 총 {len(metainfo['away']['players'])}명")
            except:
                if full_log: print("어웨이 팀 선수 정보 로딩 실패")

            await page.wait_for_selector(LOG_TAB_SELECTOR, timeout=1000)
            await page.click(LOG_TAB_SELECTOR)
            if full_log: print("문자중계 페이지 이동완료")

            all_results = []

            for quarter in quarters:
                try:
                    label_selector = f"label[for='{quarter['radio_id']}']"
                    try:
                        await page.click(label_selector, timeout=1000)
                    except Exception:
                        if full_log: print(f"{quarter['name']} 스킵 (비활성화됨)")
                        continue

                    try:
                        await page.wait_for_selector(TABLE_SELECTOR, timeout=1000)
                        table_element = await page.query_selector(TABLE_SELECTOR)
                        
                        if table_element:
                            table_html = await table_element.inner_html()
                            table_text = await table_element.inner_text()
                            
                            rows = await table_element.query_selector_all("tr")
                            row_data = []
                            for i, row in enumerate(rows):
                                row_html = await row.inner_html()
                                row_text = await row.inner_text()
                                if row_text.strip():
                                    row_data.append({
                                        'row_index': i + 1,
                                        'html': row_html,
                                        'text': row_text.strip()
                                    })
                            
                            result = {
                                'quarter': quarter['name'],
                                'quarter_data_key': quarter['data_key'],
                                'table_html': table_html,
                                'table_text': table_text.strip(),
                                'row_count': len(row_data),
                                'rows': row_data
                            }
                            
                            metainfo['quarters'].append(quarter['name'])
                            all_results.append(result)
                            if full_log: print(f"{quarter['name']} 완료: {len(row_data)}개 행")
                        else:
                            if full_log: print(f"{quarter['name']} 테이블 없음")
                    except:
                        if full_log: print(f"{quarter['name']} 테이블 수집 실패")

                except:
                    if full_log: print(f"{quarter['name']} 처리 오류")

            await browser.close()
            all_results.append(metainfo)
            return all_results
            
        except Exception as e:
            error_msg = str(e).split('\n')[0] if '\n' in str(e) else str(e)
            if full_log: print(f"크롤링 오류: {error_msg[:100]}...")
            if 'browser' in locals(): await browser.close()
            return []

def save_results_to_file(results, file_path, full_log):
    json_data = {
        "metainfo": results[-1]
    }
    for result in results[:-1]:
        quarter_data = []
        for row in result["rows"]:
            soup = BeautifulSoup(row["html"], "html.parser")
            tds = soup.find_all("td")
            th = soup.find("th")
            
            row_data = {}
            for i, td in enumerate(tds):
                text = td.find("p").get_text(strip=True)
                row_data[f"{'home' if i == 0 else 'away'}"] = text
            row_data["time"] = th.get_text(strip=True) if th else ""
            
            quarter_data.append(row_data)
        json_data[result["quarter"]] = quarter_data
    
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)

    if full_log:
        print(f"결과를 {file_path}에 저장했습니다.")

async def kbl_crawler(URL, file_path, full_log=False):
    """
    메인 실행 함수
    """
    if full_log:
        print("========================================")
        print(f"KBL {'/'.join(URL.split('/')[-2:])} 크롤링 실행중...")

    # 크롤링 실행
    seasonName = file_path.split('/')[-2]
    results = await crawl_kbl_data(URL, seasonName, full_log)

    if results:
        if full_log:
            print(f"크롤링 완료: {len(results) - 1}개 쿼터")
        save_results_to_file(results, file_path, full_log)
        if not full_log:
            print(f"KBL {'/'.join(URL.split('/')[-2:])} ({results[-1]['home']['name']} vs {results[-1]['away']['name']}) 크롤링 완료, quarters :[{', '.join(results[-1]['quarters'])}] => '{file_path}'에 저장됨")
    else:
        print(f"KBL {'/'.join(URL.split('/')[-2:])} 크롤링 실패")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(json.dumps({"metainfo": {
                "url": URL,
                "seasonName": seasonName,
                "gameKey": URL.split('/')[-2],
                "date": URL.split("/")[-1],
                "home": {"name": "error", "score": 0, "players": []},
                "away": {"name": "error", "score": 0, "players": []},
                "winner": "error",
                "quarters": []
            }}))
    if full_log:
        print("========================================")

if __name__ == "__main__":
    gameKeys = {
        '2022-2023': ['S41G01N72/20221127', 'S41G01N99/20221213', 'S41G01N173/20230128', 'S41G01N209/20230218'],
        '2023-2024': ['S43G01N218/20240302', 'S43G01N220/20240302', 'S43G01N235/20240313'],
        '2024-2025': ['S45G01N33/20241104', 'S45G01N73/20241208', 'S45G01N168/20250201']
    }
    for seasonName in gameKeys.keys():
        for game in gameKeys[seasonName]:
            URL = f"https://kbl.or.kr/match/record/{game}"
            FILE_PATH = f"kbl_data/{seasonName}/{URL.split('/')[-2]}.json"
            asyncio.run(kbl_crawler(URL, FILE_PATH, True))