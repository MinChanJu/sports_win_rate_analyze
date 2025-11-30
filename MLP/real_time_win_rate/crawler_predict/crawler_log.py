import time
import asyncio
from playwright.async_api import async_playwright

_browser = None
_page = None

async def get_page():
    global _browser, _page
    if _page is not None:
        return _page

    p = await async_playwright().start()
    _browser = await p.chromium.launch(headless=True)
    _page = await _browser.new_page(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    )
    _page.set_default_timeout(10000)
    return _page

async def close_browser():
    global _browser, _page
    if _browser is not None:
        await _browser.close()
        _browser = None
        _page = None

async def crawl_meta_data(URL: str) -> dict | None:
    gameKey = URL.split("/")[-2]
    date = URL.split("/")[-1]
    
    SCORE_SELECTOR = "#root > main > div > div > div:nth-child(3) > div.record-summary > div:nth-child(1) > ul > li"
    TEAM_PREFIX = f"https://api.kbl.or.kr/match/getPreviewData/{date}/{gameKey}"  # 팀 정보 URL 접두사

    try:
        page = await get_page()

        async with page.expect_response(
            lambda r: r.url.startswith(TEAM_PREFIX)
        ) as resp_info:
            await page.goto(URL, wait_until="networkidle")
            await asyncio.sleep(0.1)

        meta_data = {"home": {}, "away": {}}
        try:
            team_response = await resp_info.value
            team_data = await team_response.json()
            arr_data = team_data["arr_game"][0]
            h_code = int(arr_data["HOME_TEAM"])
            a_code = int(arr_data["AWAY_TEAM"])
            meta_data["home"]["code"] = h_code
            meta_data["away"]["code"] = a_code
            
            await page.wait_for_selector(SCORE_SELECTOR, timeout=1000)
            team_elements = await page.query_selector_all(SCORE_SELECTOR)
            for i, team_element in enumerate(team_elements):
                score_elements = await team_element.query_selector_all("div > p")
                team_name = await score_elements[0].inner_text()
                meta_data["home" if i == 0 else "away"]["name"] = team_name
                
        except Exception as e:
            print("팀 정보 로딩 실패" + str(e))

        return meta_data

    except Exception as e:
        error_msg = str(e).split("\n")[0] if "\n" in str(e) else str(e)
        print(f"크롤링 오류: {error_msg[:100]}...")
        return None

async def crawl_all_logs(URL: str) -> list | None:
    gameKey = URL.split("/")[-2]

    LOG_TAB_SELECTOR = "#root > main > div.layout.grid-2 > div > ul.tab-style1.sticky > li:nth-child(4) > a"  # 문자중계 탭
    TARGET_PREFIX = f"https://api.kbl.or.kr/match/{gameKey}/text-cast?" # 문자중계 API URL 접두사

    # 각 쿼터 정보
    quarters = [
        {"name": "Q1", "radio_id": "radio0" },
        {"name": "Q2", "radio_id": "radio1" },
        {"name": "Q3", "radio_id": "radio2" },
        {"name": "Q4", "radio_id": "radio3" },
        {"name": "연장", "radio_id": "radio4" },
    ]

    try:
        page = await get_page()
        
        await page.goto(URL, wait_until="networkidle")
        await asyncio.sleep(0.1)

        await page.wait_for_selector(LOG_TAB_SELECTOR, timeout=1000)
        await page.click(LOG_TAB_SELECTOR)
        await asyncio.sleep(0.1)

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
                print(f"{quarter['name']} 처리 오류")

        return all_logs

    except Exception as e:
        error_msg = str(e).split("\n")[0] if "\n" in str(e) else str(e)
        print(f"크롤링 오류: {error_msg[:100]}...")
        return None

async def main():
    URL = "https://kbl.or.kr/match/record/S41G01N171/20230128"
    
    await get_page()  # 전역 page 준비
    meta_data = await crawl_meta_data(URL)

    n = 10
    start_time = time.time()
    for _ in range(n):
        all_logs = await crawl_all_logs(URL)
    end_time = time.time()
    print(f"Crawling took {end_time - start_time} seconds")
    print(f"Average time per crawl: {(end_time - start_time) / n} seconds")

    await close_browser()

    if all_logs:
        print(f"Home Team Code: {meta_data['home']['code']}, Away Team Code: {meta_data['away']['code']}")
        print(f"Home Team Name: {meta_data['home']['name']}, Away Team Name: {meta_data['away']['name']}")
        print(f"Total Logs Crawled: {len(all_logs)}")

if __name__ == "__main__":
    asyncio.run(main())
