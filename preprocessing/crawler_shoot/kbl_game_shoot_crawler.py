import asyncio
import json
import os
from playwright.async_api import async_playwright

async def crawl_kbl_match_chart(URL, seasonName, full_log):
    """
    KBL 웹사이트에서 '매치차트' 탭을 클릭한 후 슛 차트 데이터를 크롤링하는 함수
    """
    
    # URL에서 게임키와 날짜 추출 (예: S41G01N171, 20230128)
    gameKey = URL.split("/")[-2]
    date = URL.split("/")[-1]

    # --- Selectors (KBL 웹사이트 구조 반영) ---
    SCORE_SELECTOR = "#root > main > div > div > div:nth-child(3) > div.record-summary > div:nth-child(1) > ul > li"
    
    # 매치차트 탭은 보통 3번째에 위치합니다. (1:경기요약, 2:기록비교, 3:매치차트, 4:문자중계)
    # 만약 클릭이 안 된다면 nth-child 숫자를 확인해야 합니다.
    CHART_TAB_SELECTOR = "#root > main > div.layout.grid-2 > div > ul.tab-style1.sticky > li:nth-child(3) > a"
    
    HOME_SELECTOR = "#root > main > div.layout.grid-2 > div > div:nth-child(5) > div.table-1200 > table > tbody > tr > td:nth-child(2) > p"
    AWAY_SELECTOR = "#root > main > div.layout.grid-2 > div > div:nth-child(6) > div.table-1200 > table > tbody > tr > td:nth-child(2) > p"

    # 우리가 가로채야 할 API의 핵심 키워드
    TARGET_API_KEYWORD = "match-chart" 

    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=True) # 디버깅 시 False로 변경하여 브라우저 화면 확인 가능
            page = await browser.new_page(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page.set_default_timeout(10000)

            # 메타 정보 초기화
            metainfo = {
                "url": URL,
                "seasonName": seasonName,
                "gameKey": gameKey,
                "date": date,
                "home": {"name": "", "code": "", "score": 0, "players": []},
                "away": {"name": "", "code": "", "score": 0, "players": []}
            }

            # 1. 페이지 접속
            if full_log:
                print(f"페이지 접속 중... {URL}")
                

            # 페이지 로딩 대기
            await page.goto(URL, wait_until="networkidle")
            await asyncio.sleep(1) # 안전장치

            # 2. 기본 경기 정보 (점수, 팀명) 파싱 - 기존 코드 재사용
            try:
                await page.wait_for_selector(SCORE_SELECTOR, timeout=3000)
                team_elements = await page.query_selector_all(SCORE_SELECTOR)
                for i, team_element in enumerate(team_elements):
                    score_elements = await team_element.query_selector_all("div > p")
                    team_key = "home" if i == 0 else "away"
                    metainfo[team_key]["name"] = await score_elements[0].inner_text()
                    metainfo[team_key]["score"] = int(await score_elements[1].inner_text())
                
                if full_log:
                    print(f"기본 정보 로딩 완료: {metainfo['home']['name']} vs {metainfo['away']['name']}")
            except Exception as e:
                print(f"점수 정보 로딩 실패: {e}")

            # 3. 매치차트 탭 클릭 및 API 데이터 가로채기 (핵심 로직)
            chart_data = None
            
            try:
                # 탭이 있는지 확인
                await page.wait_for_selector(CHART_TAB_SELECTOR, timeout=3000)
                
                # 클릭과 동시에 발생하는 네트워크 요청 중 'match-chart'가 포함된 것을 잡습니다.
                async with page.expect_response(lambda response: TARGET_API_KEYWORD in response.url and response.status == 200, timeout=5000) as response_info:
                    if full_log:
                        print("매치차트 탭 클릭 시도...")
                    await page.click(CHART_TAB_SELECTOR)
                
                # 가로챈 응답을 JSON으로 변환
                api_response = await response_info.value
                json_data = await api_response.json()
                
                # match-chart API는 보통 {"data": {...}} 또는 바로 데이터가 오는 경우가 있음
                # 질문주신 구조(shootLog)를 찾아서 저장
                if "shootLog" in json_data:
                    chart_data = json_data["shootLog"]
                elif "data" in json_data and "shootLog" in json_data["data"]:
                    chart_data = json_data["data"]["shootLog"]
                else:
                    chart_data = json_data # 구조를 모를 땐 통째로 저장
                
                if full_log:
                    print("API 데이터 가로채기 성공!")

            except Exception as e:
                print(f"매치차트 API 로딩 실패 (탭 클릭 문제 또는 타임아웃): {e}")

            await browser.close()
            return metainfo, chart_data

        except Exception as e:
            print(f"크롤링 치명적 오류: {e}")
            if 'browser' in locals():
                await browser.close()
            return metainfo, None

# 파일 저장 함수 (기존 코드 유지)
def save_results_to_file(metainfo, chart_data, file_path, full_log):
    json_data = {
        "metainfo": metainfo,
        "shootLog": chart_data if chart_data else []
    }
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

    if full_log:
        print(f"결과를 {file_path}에 저장했습니다.")

# 메인 래퍼 함수
async def kbl_chart_crawler(URL, file_path, full_log=False):
    seasonName = file_path.split("/")[-2]
    
    # 디렉토리 생성
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    metainfo, chart_data = await crawl_kbl_match_chart(URL, seasonName, full_log)
    
    if chart_data:
        save_results_to_file(metainfo, chart_data, file_path, full_log)
        if not full_log:
            print(f"완료: {metainfo['home']['name']} vs {metainfo['away']['name']} -> {file_path}")
    else:
        print(f"실패 (데이터 없음): {URL}")

# 실행부
if __name__ == "__main__":
    # 테스트용 게임 키 (질문주신 URL의 게임키 S47G01N49 사용)
    # 실제로는 리스트로 돌리시면 됩니다.
    gameKeys = {
        '2024-2025': ['S47G01N49/20241029'], 
    }
    
    for seasonName in gameKeys.keys():
        for game in gameKeys[seasonName]:
            URL = f"https://kbl.or.kr/match/record/{game}"
            # 파일명에 _chart를 붙여서 구분
            FILE_PATH = f"./kbl_chart_data/{seasonName}/{game.split('/')[0]}_chart.json"
            
            asyncio.run(kbl_chart_crawler(URL, FILE_PATH, True))