from playwright.async_api import async_playwright, TimeoutError
from kbl_game_crawler import kbl_crawler
import asyncio, os, shutil

async def handle_response(res, folder):
    try:
        data = await res.json()
        for match in data:
            if match["seasonCategoryName"] != "정규시즌": continue
            gmkey = match.get("gmkey"); gameDate = match.get("gameDate")
            if gmkey and gameDate:
                url = f"https://www.kbl.or.kr/match/record/{gmkey}/{gameDate}"
                file_path = f"{folder}/{gmkey[:3]}/{gmkey}_results.json"
                await kbl_crawler(url, file_path)
    except:
        print("Error occurred while processing response")

async def main():
    print("Checking KBL schedule...")
    
    BUTTON_SELECTOR = "#root > main > div > div.contents > div.filter-wrap > div > ul > li:nth-child(1) > button"
    TARGET_PREFIX = "https://api.kbl.or.kr/match/list?"
    URL = "https://kbl.or.kr/match/schedule"
    FOLDER = "kbl_data"
    if os.path.exists(FOLDER):
        shutil.rmtree(FOLDER)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(URL, wait_until="networkidle")

        # (1) 초기 로딩에서 발생한 응답 먼저 대기
        try:
            res = await page.context.wait_for_event(
                "response",
                predicate=lambda r: r.url.startswith(TARGET_PREFIX) and r.request.method == "GET",
                timeout=1000
            )
            await handle_response(res, FOLDER)
        except TimeoutError:
            pass  # 초기 응답이 없으면 스킵

        # (2) 버튼 클릭 -> 해당 응답 대기 반복
        await page.wait_for_selector(BUTTON_SELECTOR)
        for _ in range(10):
            async with page.expect_response(lambda r: r.url.startswith(TARGET_PREFIX)) as resp_info:
                await page.click(BUTTON_SELECTOR)
            res = await resp_info.value
            await handle_response(res, FOLDER)
            await asyncio.sleep(1)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())