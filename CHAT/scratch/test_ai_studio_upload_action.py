import asyncio
import os
from playwright.async_api import async_playwright

CHROME_PROFILE = r"D:\AI_Engineer\MSEMAX-GAIStudio-vision\chrome_profile"
TEST_IMAGE = r"C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\scratch\test_page1_scale2.5.webp"

async def main():
    if not os.path.exists(TEST_IMAGE):
        print(f"Error: image not found at {TEST_IMAGE}")
        return

    async with async_playwright() as p:
        args = ["--disable-blink-features=AutomationControlled", "--start-maximized"]
        context = await p.chromium.launch_persistent_context(
            user_data_dir=CHROME_PROFILE,
            headless=False,
            no_viewport=True,
            args=args,
            ignore_default_args=["--enable-automation"]
        )
        page = context.pages[0] if context.pages else await context.new_page()
        print("Navigating to AI Studio new chat...")
        await page.goto("https://aistudio.google.com/prompts/new_chat", wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(4)
        
        file_input = page.locator('input[type="file"], [data-test-upload-file-input]').first
        count = await file_input.count()
        print(f"File input count: {count}")
        if count > 0:
            print(f"Setting input files with: {TEST_IMAGE}")
            await file_input.set_input_files(TEST_IMAGE)
            print("File set! Waiting 4 seconds to observe upload in UI...")
            await asyncio.sleep(4)
            
            # Take screenshot to verify image attached in prompt container
            screenshot_path = r"C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\scratch\verify_upload_ui.png"
            await page.screenshot(path=screenshot_path)
            print(f"Screenshot saved to {screenshot_path}")
            
            # Inspect chips or attached thumbnails
            thumbnails = await page.evaluate('''() => {
                const chips = Array.from(document.querySelectorAll('.prompt-box-container img, ms-prompt-box img, .media-chunk, .file-chip, [data-test*="media"]')).map(el => ({
                    tag: el.tagName,
                    src: el.src ? el.src.slice(0, 100) : '',
                    cls: el.className
                }));
                return chips;
            }''')
            print("Detected thumbnails/chips:", thumbnails)

        await context.close()

if __name__ == "__main__":
    asyncio.run(main())
