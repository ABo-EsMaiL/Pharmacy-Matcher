import asyncio
import os
from playwright.async_api import async_playwright

CHROME_PROFILE = r"D:\AI_Engineer\MSEMAX-GAIStudio-vision\chrome_profile"
TEST_IMAGE = r"C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\scratch\test_page1_scale2.5.webp"
PROMPT = (
    "أنت خبير صيدلي متخصص في استخراج بيانات فواتير وقوائم الأدوية.\n"
    "قم باستخراج أول 5 أصناف أدوية من هذه الصورة بصيغة JSON: {\"items\": [{\"item_name_raw\": \"...\"}]}"
)

async def main():
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
        print("Navigating to AI Studio...")
        await page.goto("https://aistudio.google.com/prompts/new_chat", wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(3)
        
        # 1. Attach Image
        file_input = page.locator('input[type="file"], [data-test-upload-file-input]').first
        print(f"Attaching file: {TEST_IMAGE}")
        await file_input.set_input_files(TEST_IMAGE)
        
        # 2. Inject Prompt text
        ta = page.locator('textarea[placeholder*="Type something" i], textarea[aria-label*="prompt" i], ms-autosize-textarea textarea').first
        await ta.wait_for(state="visible", timeout=5000)
        await ta.evaluate('''(el, text) => {
            el.value = text;
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
        }''', PROMPT)
        await ta.focus()
        await page.keyboard.press("Space")
        await page.keyboard.press("Backspace")
        
        # 3. Hook on Run button: wait until active
        run_btn = page.locator('button.ctrl-enter, button:has-text("Run"), button[mattooltipclass="run-button-tooltip"]').first
        print("Waiting for Run button to become active (aria-disabled == false)...")
        active = False
        for i in range(30):
            aria_dis = await run_btn.get_attribute("aria-disabled")
            is_dis = await run_btn.is_disabled()
            print(f"Check {i+1}: aria-disabled={aria_dis}, is_disabled={is_dis}")
            if aria_dis == "false" and not is_dis:
                active = True
                print(f"[+] Run button is ACTIVE after {i*0.5:.1f}s! Clicking now...")
                await run_btn.click()
                break
            await asyncio.sleep(0.5)
            
        if not active:
            print("[!] Run button never became active! Trying Control+Enter fallback...")
            await page.keyboard.press("Control+Enter")
            
        print("Waiting 10 seconds to observe generation...")
        await asyncio.sleep(10)
        
        # Check if generation started
        model_text = await page.evaluate('''() => {
            const modelTurns = Array.from(document.querySelectorAll('.model-prompt-container, [data-turn-role="model"], .model.render, ms-chat-turn:has(.model)'));
            return modelTurns.map(el => (el.innerText || '').slice(0, 200));
        }''')
        print("Model turns detected:", model_text)
        
        screenshot_path = r"C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\scratch\verify_generation_started.png"
        await page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")
        
        await context.close()

if __name__ == "__main__":
    asyncio.run(main())
