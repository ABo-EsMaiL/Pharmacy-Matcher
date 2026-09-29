import asyncio
from playwright.async_api import async_playwright

CHROME_PROFILE_DIR = r"D:\AI_Engineer\MSEMAX-GAIStudio\chrome_profile"

async def main():
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=CHROME_PROFILE_DIR,
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = context.pages[0] if context.pages else await context.new_page()
        await page.goto("https://aistudio.google.com/prompts/new_chat", wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(3)
        
        # Check current state of Grounding with Google Search
        search_toggle = page.locator('button[aria-label="Grounding with Google Search"], button[aria-label*="Google Search" i]')
        remove_btn = page.locator('button[aria-label="Remove Grounding with Google Search"]')
        
        print("Initial count search_toggle:", await search_toggle.count())
        print("Initial count remove_btn:", await remove_btn.count())
        
        if await remove_btn.count() > 0:
            print("Clicking remove_btn...")
            await remove_btn.first.click()
            await asyncio.sleep(1)
        elif await search_toggle.count() > 0:
            checked = await search_toggle.first.get_attribute("aria-checked")
            print("Toggle checked:", checked)
            if checked == "true":
                print("Clicking search_toggle to turn OFF...")
                await search_toggle.first.click()
                await asyncio.sleep(1)

        # Check state after
        cnt_remove = await remove_btn.count()
        checked_after = None
        if await search_toggle.count() > 0:
            checked_after = await search_toggle.first.get_attribute("aria-checked")
            
        print(f"State after: remove_btn count={cnt_remove}, toggle checked={checked_after}")
        await context.close()

if __name__ == "__main__":
    asyncio.run(main())
