import json
import os
import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
from bs4 import BeautifulSoup

async def crawl_kbl_data():
    """
    KBL 웹사이트에서 문자중계 탭을 클릭한 후 각 쿼터별 데이터를 크롤링하는 함수
    """
    URL = "https://www.kbl.or.kr/match/record/S45G04N1/20250505"
    TAB_SELECTOR = "#root > main > div > div > ul.tab-style1.sticky > li:nth-child(4) > a"  # 문자중계 탭
    TEAM_SELECTOR = "#root > main > div > div > div > div.record-summary.md > div:nth-child(1) > ul > li > div > div > p" # 팀 정보
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
            
            print("페이지 로딩중...")
            await page.goto(URL, wait_until="networkidle")
            
            print("문자중계 탭 클릭중...")
            await page.wait_for_selector(TAB_SELECTOR, timeout=15000)
            await page.click(TAB_SELECTOR)
            print("문자중계 페이지 이동완료")
            
            all_results = []
            
            try:
                await page.wait_for_selector(TEAM_SELECTOR, timeout=5000)
                team_elements = await page.query_selector_all(TEAM_SELECTOR)
                if len(team_elements) >= 2:
                    home_text = await team_elements[0].inner_text()
                    away_text = await team_elements[1].inner_text()
                    all_results.append({
                        "home": home_text,
                        "away": away_text
                    })
                else:
                    print(f"팀 정보 부족")
            except:
                print(f"팀 정보 로딩 실패")

            for quarter in quarters:
                try:
                    print(f"{quarter['name']} 수집중...")
                    
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
                            
                            all_results.append(result)
                            print(f"{quarter['name']} 완료: {len(row_data)}개 행")
                        else:
                            print(f"{quarter['name']} 테이블 없음")
                    except:
                        print(f"{quarter['name']} 테이블 수집 실패")
                        
                except:
                    print(f"{quarter['name']} 처리 오류")
            
            await browser.close()
            return all_results
            
        except Exception as e:
            print(f"크롤링 오류: {e}")
            if 'browser' in locals():
                await browser.close()
            return []

def save_results_to_file(results, filename="kbl_quarters_results.html"):
    json_data = {
        "metainfo": {
            "home": results[0]["home"],
            "away": results[0]["away"],
            "quarters": [result["quarter"] for result in results[1:]]
        },
    }
    for result in results[1:]:
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
    
    with open("kbl_quarters_data.json", "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)

async def main():
    """
    메인 실행 함수
    """
    print("KBL 크롤링 실행중...")
    
    # 크롤링 실행
    results = await crawl_kbl_data()
    
    if results:
        print(f"크롤링 완료: {len(results) - 1}개 쿼터")
        save_results_to_file(results)
    else:
        print("크롤링 실패")

if __name__ == "__main__":
    asyncio.run(main())
