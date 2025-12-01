import asyncio
import json
import os
from playwright.async_api import async_playwright

async def crawl_kbl_match_chart(URL, file_path):
    # 1. URL 파싱
    try:
        parts = URL.split("/")
        gameKey = parts[-2]
        date = parts[-1]
    except:
        gameKey = "Unknown"
        date = "Unknown"

    # --- Selectors ---
    SCORE_SELECTOR = "#root > main > div > div > div:nth-child(3) > div.record-summary > div:nth-child(1) > ul > li"
    CHART_TAB_SELECTOR = "#root > main > div.layout.grid-2 > div > ul.tab-style1.sticky > li:nth-child(3) > a"
    
    # --- 가로챌 API 키워드 정의 ---
    TEAM_INFO_KEYWORD = "getPreviewData"  # 팀 코드 정보가 담긴 API
    CHART_API_KEYWORD = "match-chart"     # 슛 차트 데이터 API

    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page.set_default_timeout(10000)

            # 2. metainfo 초기화
            metainfo = {
                "url": URL,
                "gameKey": gameKey,
                "date": date,
                "home": {"name": "", "code": "", "score": 0},
                "away": {"name": "", "code": "", "score": 0},
            }

            # =================================================================
            # [수정 1] 페이지 접속 시 팀 정보(getPreviewData) 가로채기
            # =================================================================
            try:
                # page.goto 실행 중에 발생하는 네트워크 요청을 기다림
                async with page.expect_response(lambda response: TEAM_INFO_KEYWORD in response.url and response.status == 200, timeout=10000) as team_resp_info:
                    await page.goto(URL, wait_until="networkidle")
                
                # ★★★ [수정됨] await를 두 단계로 나누어야 합니다 ★★★
                team_response = await team_resp_info.value  # 1. 응답 객체(Response)를 먼저 받음
                team_json = await team_response.json()      # 2. 그 객체에서 json()을 호출
                
                # API 응답에서 HOME_TEAM, AWAY_TEAM 코드 추출
                if "arr_game" in team_json and len(team_json["arr_game"]) > 0:
                    game_info = team_json["arr_game"][0]
                    metainfo["home"]["code"] = str(game_info.get("HOME_TEAM", "")).strip()
                    metainfo["away"]["code"] = str(game_info.get("AWAY_TEAM", "")).strip()
            
            except Exception as e:
                print(f"   [Warning] 팀 코드 추출 실패 (기본값 진행): {e}")
                if page.url != URL: 
                    await page.goto(URL, wait_until="networkidle")

            # =================================================================
            # 3. 점수 및 팀 이름 파싱 (기존 유지)
            # =================================================================
            try:
                await page.wait_for_selector(SCORE_SELECTOR, timeout=3000)
                team_elements = await page.query_selector_all(SCORE_SELECTOR)
                for i, team_element in enumerate(team_elements):
                    score_elements = await team_element.query_selector_all("div > p")
                    team_key = "home" if i == 0 else "away"
                    metainfo[team_key]["name"] = await score_elements[0].inner_text()
                    metainfo[team_key]["score"] = int(await score_elements[1].inner_text())
            except Exception as e:
                print(f"   [Error] 점수 파싱 실패: {e}")

            # =================================================================
            # 4. 매치차트 탭 클릭 및 슛 데이터 가로채기
            # =================================================================
            chart_data = None
            try:
                await page.wait_for_selector(CHART_TAB_SELECTOR, timeout=3000)
                
                async with page.expect_response(lambda response: CHART_API_KEYWORD in response.url and response.status == 200, timeout=5000) as chart_resp_info:
                    await page.click(CHART_TAB_SELECTOR)
                
                # ★★★ [수정됨] 여기도 동일하게 await 분리 ★★★
                chart_response = await chart_resp_info.value # 1. 응답 객체 받기
                json_data = await chart_response.json()      # 2. json 변환
                
                # 데이터 구조 확인
                if "shootLog" in json_data:
                    chart_data = json_data["shootLog"]
                elif "data" in json_data and "shootLog" in json_data["data"]:
                    chart_data = json_data["data"]["shootLog"]
                else:
                    chart_data = json_data 

            except Exception as e:
                print(f"   [Error] 매치차트 로딩 실패: {e}")

            await browser.close()
            return metainfo, chart_data

        except Exception as e:
            print(f"   [Critical] 브라우저 에러: {e}")
            if 'browser' in locals():
                await browser.close()
            return metainfo, None

def save_results_to_file(metainfo, chart_data, file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    json_data = {
        "metainfo": metainfo,
        "shootLog": chart_data if chart_data else []
    }
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

# 메인에서 호출되는 함수
async def kbl_chart_crawler(URL, file_path):
    metainfo, chart_data = await crawl_kbl_match_chart(URL, file_path)
    if chart_data:
        save_results_to_file(metainfo, chart_data, file_path)