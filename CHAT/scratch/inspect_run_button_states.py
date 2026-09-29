import asyncio
import os
import json
from playwright.async_api import async_playwright

CHROME_PROFILE = r"D:\AI_Engineer\MSEMAX-GAIStudio-vision\chrome_profile"
TEST_IMAGE = r"C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\scratch\test_page1_scale2.5.webp"

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
        
        # State 1: Empty prompt box
        s1 = await page.evaluate('''() => {
            const btn = document.querySelector('button.ctrl-enter, button:has(.ctrl-enter), [mattooltipclass="run-button-tooltip"]');
            if (!btn) {
                // Search by text
                const all = Array.from(document.querySelectorAll('button'));
                const b = all.find(el => (el.innerText || '').includes('Run'));
                if (b) {
                    return {
                        tag: b.tagName,
                        outer: b.outerHTML.slice(0, 200),
                        disabled: b.disabled,
                        ariaDisabled: b.getAttribute('aria-disabled'),
                        classes: b.className
                    };
                }
                return null;
            }
            return {
                tag: btn.tagName,
                outer: btn.outerHTML.slice(0, 200),
                disabled: btn.disabled,
                ariaDisabled: btn.getAttribute('aria-disabled'),
                classes: btn.className
            };
        }''')
        print("State 1 (Empty):", s1)
        
        # Upload image
        file_input = page.locator('input[type="file"], [data-test-upload-file-input]').first
        await file_input.set_input_files(TEST_IMAGE)
        print("Image uploaded! Monitoring Run button state every 0.5s for 10s...")
        
        for i in range(20):
            await asyncio.sleep(0.5)
            state = await page.evaluate('''() => {
                const all = Array.from(document.querySelectorAll('button'));
                const b = all.find(el => (el.innerText || '').includes('Run') || (el.className || '').includes('ctrl-enter'));
                if (!b) return { error: "no button" };
                return {
                    disabled: b.disabled,
                    ariaDisabled: b.getAttribute('aria-disabled'),
                    classes: b.className,
                    text: (b.innerText || '').replace(/\\n/g, ' '),
                    hasTokens: Boolean(document.querySelector('.media-chunk, ms-prompt-image, .loaded-image'))
                };
            }''')
            print(f"t={i*0.5:.1f}s: {state}")
            # If enabled, break
            if state.get('disabled') is False and state.get('ariaDisabled') != 'true':
                print(f"[+] Run button is ACTIVE at t={i*0.5:.1f}s!")
                break
                
        await context.close()

if __name__ == "__main__":
    asyncio.run(main())
