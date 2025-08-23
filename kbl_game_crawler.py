from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import asyncio, json, os

async def crawl_kbl_data(URL):
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
            page.set_default_timeout(30000)
            
            metainfo = {
                "date": URL.split("/")[-1],
                "home": {"name": "", "score": 0, "players": []},
                "away": {"name": "", "score": 0, "players": []},
                "winner": "",
                "quarters": []
            }
            
            await page.goto(URL, wait_until="networkidle")
            print("페이지 로딩 완료")
            
            try:
                await page.wait_for_selector(SCORE_SELECTOR, timeout=5000)
                team_elements = await page.query_selector_all(SCORE_SELECTOR)
                for i, team_element in enumerate(team_elements):
                    score_elements = await team_element.query_selector_all("div > p")
                    metainfo["home" if i == 0 else "away"]["name"] = await score_elements[0].inner_text()
                    metainfo["home" if i == 0 else "away"]["score"] = int(await score_elements[1].inner_text())
                metainfo["winner"] = "home" if metainfo["home"]["score"] > metainfo["away"]["score"] else "away" if metainfo["home"]["score"] < metainfo["away"]["score"] else "draw"
                print(f"팀 정보 로딩 완료")
            except:
                print("팀 정보 로딩 실패")

            await page.wait_for_selector(GAME_TAB_SELECTOR, timeout=15000)
            await page.click(GAME_TAB_SELECTOR)
            print("경기기록 페이지 이동완료")
            
            try:
                await page.wait_for_selector(HOME_SELECTOR, timeout=5000)
                home_elements = await page.query_selector_all(HOME_SELECTOR)
                metainfo["home"]["players"] = [await p.inner_text() for p in home_elements]
                print(f"홈 팀 선수 정보 로딩 완료 총 {len(metainfo['home']['players'])}명")
            except:
                print("홈 팀 선수 정보 로딩 실패")

            try:
                await page.wait_for_selector(AWAY_SELECTOR, timeout=5000)
                away_elements = await page.query_selector_all(AWAY_SELECTOR)
                metainfo["away"]["players"] = [await p.inner_text() for p in away_elements]
                print(f"어웨이 팀 선수 정보 로딩 완료 총 {len(metainfo['away']['players'])}명")
            except:
                print("어웨이 팀 선수 정보 로딩 실패")

            await page.wait_for_selector(LOG_TAB_SELECTOR, timeout=15000)
            await page.click(LOG_TAB_SELECTOR)
            print("문자중계 페이지 이동완료")
            
            all_results = []

            for quarter in quarters:
                try:
                    # 라디오 버튼 상태 확인 (연장전인 경우 특별 처리)
                    radio_selector = f"#{quarter['radio_id']}"
                    radio_element = await page.query_selector(radio_selector)
                    
                    if radio_element:
                        # disabled 상태 확인
                        is_disabled = await radio_element.get_attribute("disabled")
                        is_checked = await radio_element.get_attribute("checked")
                        
                        # 연장전인 경우 상태에 따라 처리
                        if quarter['name'] == "연장":
                            if is_disabled is not None:  # disabled 속성이 존재하면
                                print(f"{quarter['name']} 경기 없음 (disabled)")
                                continue
                            elif is_checked is None:  # checked 속성이 없으면 연장전이 진행되지 않음
                                print(f"{quarter['name']} 경기 없음 (not checked)")
                                continue
                            else:
                                print(f"{quarter['name']} 경기 진행됨 (checked)")
                    
                    # 라벨 클릭
                    label_selector = f"label[for='{quarter['radio_id']}']"
                    
                    try:
                        # 라벨 클릭 시도
                        await page.click(label_selector)
                    except:
                        # 비활성화된 경우 건너뛰기
                        print(f"{quarter['name']} 클릭 실패")
                        continue

                    # 테이블 데이터 수집
                    try:
                        await page.wait_for_selector(TABLE_SELECTOR, timeout=5000)
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
                            print(f"{quarter['name']} 완료: {len(row_data)}개 행")
                        else:
                            print(f"{quarter['name']} 테이블 없음")
                    except:
                        print(f"{quarter['name']} 테이블 수집 실패")
                        
                except:
                    print(f"{quarter['name']} 처리 오류")
            
            await browser.close()
            all_results.append(metainfo)
            return all_results
            
        except Exception as e:
            print(f"크롤링 오류: {e}")
            if 'browser' in locals():
                await browser.close()
            return []

def save_results_to_file(results, file_path):
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

async def kbl_crawler(URL, file_path):
    """
    메인 실행 함수
    """
    print("========================================")
    print(f"KBL {'/'.join(URL.split('/')[-2:])} 크롤링 실행중...")

    # 크롤링 실행
    results = await crawl_kbl_data(URL)

    if results:
        print(f"크롤링 완료: {len(results) - 1}개 쿼터")
        save_results_to_file(results, file_path)
    else:
        print("크롤링 실패")
    print("========================================")

if __name__ == "__main__":
    URL = "https://kbl.or.kr/match/record/S45G01N130/20250108"
    FILE_PATH = "kbl_data/S45/S45G01N130_results.json"
    asyncio.run(kbl_crawler(URL, FILE_PATH))