import asyncio
import json
from playwright.async_api import async_playwright

async def test_cookies():
    with open(r"D:\AI_Engineer\MSEMAX\session_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    cookies_dict = data.get("cookies", {})
    
    # Format cookies for Playwright
    # Playwright cookies: list of dicts with name, value, domain, path
    google_cookies = []
    google_domains = [".google.com", "aistudio.google.com", "accounts.google.com"]
    
    for name, value in cookies_dict.items():
        if any(k in name.lower() for k in ["sid", "hsid", "ssid", "apisid", "sapisid", "nid", "account_chooser"]):
            google_cookies.append({
                "name": name,
                "value": str(value),
                "url": "https://google.com"
            })

    print(f"Loaded {len(google_cookies)} Google auth cookies.")

    p = await async_playwright().start()
    ctx = await p.chromium.launch_persistent_context(
        user_data_dir=r"D:\AI_Engineer\MSEMAX-GAIStudio\chrome_profile",
        headless=False,
        args=["--disable-blink-features=AutomationControlled", "--start-maximized"]
    )
    
    await ctx.add_cookies(google_cookies)
    page = ctx.pages[0] if ctx.pages else await ctx.new_page()
    
    await page.goto("https://aistudio.google.com/prompts/new_chat", wait_until="domcontentloaded")
    await asyncio.sleep(4)
    
    print("Page URL:", page.url)
    print("Page Title:", await page.title())
    
    is_signed_in = "accounts.google.com" not in page.url and "Sign in" not in (await page.title())
    print("Signed in to AI Studio?:", is_signed_in)
    
    await ctx.close()
    await p.stop()

if __name__ == "__main__":
    asyncio.run(test_cookies())
