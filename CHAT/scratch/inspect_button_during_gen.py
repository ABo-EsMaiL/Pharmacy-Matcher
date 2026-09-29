import asyncio
import json
from playwright.async_api import async_playwright

CHROME_PROFILE = r"D:\AI_Engineer\MSEMAX-GAIStudio-vision\chrome_profile"

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
        await page.goto("https://aistudio.google.com/prompts/new_chat", wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(2)
        
        # Inject short prompt
        ta = page.locator('textarea[placeholder*="Type something" i], textarea[aria-label*="prompt" i], ms-autosize-textarea textarea').first
        await ta.wait_for(state="visible", timeout=5000)
        await ta.evaluate('''(el) => {
            el.value = "Count from 1 to 10 slowly with words.";
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
        }''')
        await ta.focus()
        await page.keyboard.press("Space")
        await page.keyboard.press("Backspace")
        await asyncio.sleep(0.5)

        run_btn = page.locator('button.ctrl-enter, button:has-text("Run"), button[mattooltipclass="run-button-tooltip"]').first
        print("Clicking Run button...")
        await run_btn.click()
        
        # Monitor all buttons in the bottom bar / chat view for 20 seconds
        for tick in range(30):
            buttons_info = await page.evaluate('''() => {
                const btns = Array.from(document.querySelectorAll('button, .run-button, [class*="run-button"]'));
                return btns.filter(b => {
                    const txt = (b.innerText || '').toLowerCase();
                    const aria = (b.getAttribute('aria-label') || '').toLowerCase();
                    const cls = (b.className || '').toLowerCase();
                    return txt.includes('run') || txt.includes('stop') || aria.includes('run') || aria.includes('stop') || cls.includes('ctrl-enter') || cls.includes('run');
                }).map(b => ({
                    tag: b.tagName,
                    text: b.innerText.replace(/\\n/g, ' '),
                    aria: b.getAttribute('aria-label'),
                    title: b.getAttribute('title'),
                    tooltip: b.getAttribute('mattooltip') || b.getAttribute('mat-tooltip'),
                    disabled: b.disabled,
                    aria_disabled: b.getAttribute('aria-disabled'),
                    classes: b.className,
                    outer: b.outerHTML.slice(0, 200)
                }));
            }''')
            print(f"t={tick*0.5:.1f}s: {json.dumps(buttons_info, ensure_ascii=False)}")
            await asyncio.sleep(0.5)
            
        await context.close()

if __name__ == "__main__":
    asyncio.run(main())
