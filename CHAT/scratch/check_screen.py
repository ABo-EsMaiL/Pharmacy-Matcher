import asyncio
from playwright.async_api import async_playwright

async def main():
    p = await async_playwright().start()
    ctx = await p.chromium.launch_persistent_context(
        user_data_dir=r"D:\AI_Engineer\MSEMAX-GAIStudio\chrome_profile",
        headless=False,
        args=["--disable-blink-features=AutomationControlled", "--start-maximized"]
    )
    page = ctx.pages[0] if ctx.pages else await ctx.new_page()
    await page.goto("https://aistudio.google.com/prompts/new_chat", wait_until="networkidle")
    await asyncio.sleep(2)
    print("URL:", page.url)
    print("Title:", await page.title())
    body = await page.locator("body").inner_text()
    print("Body text snippet:\n", body[:400])
    await page.screenshot(path=r"D:\AI_Engineer\MSEMAX-GAIStudio\debug_screen.png")
    print("Screenshot saved to debug_screen.png")
    await ctx.close()
    await p.stop()

if __name__ == "__main__":
    asyncio.run(main())
