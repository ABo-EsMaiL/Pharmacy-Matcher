import asyncio
from playwright.async_api import async_playwright

async def t():
    p = await async_playwright().start()
    ctx = await p.chromium.launch_persistent_context(
        user_data_dir=r"D:\AI_Engineer\MSEMAX-GAIStudio\c hrome_profile",
        headless=True
    )
    page = ctx.pages[0] if ctx.pages else await ctx.new_page()
    await page.goto("https://aistudio.google.com/prompts/new_chat", timeout=20000, wait_until="domcontentloaded")
    await asyncio.sleep(2)
    print("URL:", page.url)
    print("Title:", await page.title())
    await ctx.close()
    await p.stop()

if __name__ == "__main__":
    asyncio.run(t())
