import asyncio
from playwright.async_api import async_playwright

async def m():
    p = await async_playwright().start()
    ctx = await p.chromium.launch_persistent_context(
        r"D:\AI_Engineer\MSEMAX-GAIStudio\chrome_profile",
        headless=False,
        args=["--disable-blink-features=AutomationControlled", "--start-maximized"]
    )
    page = ctx.pages[0] if ctx.pages else await ctx.new_page()
    await page.goto("https://aistudio.google.com/welcome", timeout=30000, wait_until="networkidle")
    await asyncio.sleep(2)
    print("URL:", page.url)
    print("Title:", await page.title())
    body = await page.locator("body").inner_text()
    print("Body snippet:", repr(body[:400]))
    btns = await page.locator("button, a").all()
    print(f"Found {len(btns)} buttons/links:")
    for b in btns[:10]:
        t = (await b.inner_text() or "").strip()
        h = await b.get_attribute("href") or ""
        print(f"  btn: '{t}', href: '{h}'")
    await ctx.close()
    await p.stop()

if __name__ == "__main__":
    asyncio.run(m())
