import asyncio
import os
from playwright.async_api import async_playwright

profiles = [
    r"D:\AI_Engineer\MSEMAX-GAIStudio\chrome_profile",
    r"D:\AI_Engineer\MSEMAX-AIStudio\aistudio_profile",
    r"D:\AI_Engineer\MSEMAX\chrome_profile",
    r"D:\AI_Engineer\MSEMAX - Copy\chrome_profile",
    r"D:\AI_Engineer\MSEMAX - Copy (2)\chrome_profile",
]

async def test_profiles():
    p = await async_playwright().start()
    for prof in profiles:
        if not os.path.exists(prof):
            print(f"[SKIP] Does not exist: {prof}")
            continue
        try:
            ctx = await p.chromium.launch_persistent_context(
                user_data_dir=prof,
                headless=True,
                args=["--disable-blink-features=AutomationControlled"]
            )
            page = ctx.pages[0] if ctx.pages else await ctx.new_page()
            await page.goto("https://aistudio.google.com/prompts/new_chat", timeout=20000, wait_until="domcontentloaded")
            await asyncio.sleep(2)
            url = page.url
            title = await page.title()
            print(f"[PROFILE] {prof}")
            print(f"   -> URL: {url}")
            print(f"   -> Title: {title}")
            is_signin = "accounts.google.com" in url or "Sign in" in title
            print(f"   -> Signed in to AI Studio? {not is_signin}\n")
            await ctx.close()
        except Exception as e:
            print(f"[ERR] {prof}: {e}\n")
    await p.stop()

if __name__ == "__main__":
    asyncio.run(test_profiles())
