import asyncio
from playwright.async_api import async_playwright

async def inspect_ui():
    pw = await async_playwright().start()
    ctx = await pw.chromium.launch_persistent_context(
        user_data_dir=r"D:\AI_Engineer\MSEMAX-GAIStudio\chrome_profile",
        headless=False,
        args=["--disable-blink-features=AutomationControlled", "--start-maximized"]
    )
    page = ctx.pages[0] if ctx.pages else await ctx.new_page()
    await page.goto("https://aistudio.google.com/prompts/new_chat", wait_until="networkidle")
    await asyncio.sleep(3)
    print("Page URL:", page.url)
    print("Page Title:", await page.title())
    body_text = await page.locator("body").inner_text()
    print("Body snippet:", repr(body_text[:300]))
    
    # 1. mat-select elements
    mat_selects = await page.locator("mat-select").all()
    print(f"Found {len(mat_selects)} mat-select elements:")
    for i, ms in enumerate(mat_selects):
        aria = await ms.get_attribute("aria-label") or ""
        txt = (await ms.inner_text() or "").strip().replace("\n", " ")
        html = await ms.evaluate("el => el.outerHTML.slice(0, 150)")
        print(f"  mat-select[{i}]: aria='{aria}', text='{txt}', snippet: {html}")

    # 2. Look for buttons or spans mentioning model names or 'flash' or 'pro'
    print("\n=== LOOKING FOR MODEL TEXT/SELECTORS ===")
    candidates = await page.locator("[aria-label*='model' i], [aria-label*='Model' i], [class*='model' i], button:has-text('Flash'), button:has-text('Pro'), button:has-text('Gemini')").all()
    print(f"Found {len(candidates)} candidate model elements:")
    for i, c in enumerate(candidates[:15]):
        tag = await c.evaluate("el => el.tagName")
        aria = await c.get_attribute("aria-label") or ""
        txt = (await c.inner_text() or "").strip().replace("\n", " ")
        cls = await c.get_attribute("class") or ""
        print(f"  cand[{i}]: tag={tag}, aria='{aria}', class='{cls}', text='{txt}'")

    await ctx.close()
    await pw.stop()

if __name__ == "__main__":
    asyncio.run(inspect_ui())
