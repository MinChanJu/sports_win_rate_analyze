from playwright.async_api import async_playwright
from kbl_game_crawler import kbl_crawler
import asyncio, os, shutil

async def handle_response(res, folder):
    try:
        data = await res.json()
        for match in data:
            if match["seasonCategoryName"] != "정규시즌": continue
            gmkey = match.get("gmkey")
            gameDate = match.get("gameDate")
            seasonName = match.get("seasonName1")
            if gmkey and gameDate:
                url = f"https://www.kbl.or.kr/match/record/{gmkey}/{gameDate}"
                file_path = f"../{folder}/{seasonName}/{gmkey}.json"
                await kbl_crawler(url, file_path)
    except:
        print("Error occurred while processing response")

async def main(s, e, folder, reset=False):
    print("Checking KBL schedule...")
    
    BUTTON_SELECTOR = "#root > main > div > div.contents > div.filter-wrap > div > ul > li:nth-child(1) > button"
    DATE_SELECTOR = "#root > main > div > div.contents > div.filter-wrap > div > ul > li:nth-child(2) > p"
    TARGET_PREFIX = "https://api.kbl.or.kr/match/list?"
    URL = "https://kbl.or.kr/match/schedule"
    if reset and os.path.exists(folder):
        shutil.rmtree(folder)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # (1) 초기 로딩에서 발생한 응답 먼저 대기
        async with page.expect_response(lambda r: r.url.startswith(TARGET_PREFIX)) as resp_info:
            await page.goto(URL, wait_until="networkidle")
            await asyncio.sleep(0.5)

        res = await resp_info.value
        await page.wait_for_selector(DATE_SELECTOR, timeout=1000)
        date = await page.query_selector(DATE_SELECTOR)
        
        if (s == 0):
            print(await date.inner_text())
            await handle_response(res, folder)

        # (2) 버튼 클릭 -> 해당 응답 대기 반복
        await page.wait_for_selector(BUTTON_SELECTOR)
        for _ in range(s-1):
            await page.click(BUTTON_SELECTOR)
            await asyncio.sleep(0.5)
        
        steps = max(0, e - s + 1 if s > 0 else e - s)
        for _ in range(steps):
            async with page.expect_response(lambda r: r.url.startswith(TARGET_PREFIX)) as resp_info:
                await page.click(BUTTON_SELECTOR)
                await asyncio.sleep(0.5)
            
            res = await resp_info.value
            await page.wait_for_selector(DATE_SELECTOR, timeout=1000)
            date = await page.query_selector(DATE_SELECTOR)
            
            print(await date.inner_text())
            await handle_response(res, folder)

        await browser.close()

if __name__ == "__main__":
    # 8월 기준
    # 24-25시즌: 3, 10
    # 23-24시즌: 15, 22
    # 22-23시즌: 27, 34
    # 21-22시즌: 39, 47

    asyncio.run(main(3, 4, "kbl_test", True))