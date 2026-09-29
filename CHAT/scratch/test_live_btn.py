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
            el.value = "Count 1 to 5";
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
        }''')
        await ta.focus()
        await page.keyboard.press("Space")
        await page.keyboard.press("Backspace")
        await asyncio.sleep(0.5)

        run_btn = page.locator('button.ctrl-enter-submits, button.ctrl-enter, button[mattooltipclass="run-button-tooltip"], button:has-text("Run")').first
        print("Clicking Run button...")
        await run_btn.click()
        
        js_fetch_state = '''() => {
            const allButtons = Array.from(document.querySelectorAll('button'));
            const actionBtn = document.querySelector(
                'button.ctrl-enter-submits, button.ctrl-enter, button[mattooltipclass="run-button-tooltip"]'
            ) || allButtons.find(b => {
                const cls = (b.className || '').toLowerCase();
                const txt = (b.innerText || '').toLowerCase();
                return cls.includes('ctrl-enter') || (txt.includes('stop') && !b.disabled) || (txt.includes('run') && cls.includes('primary'));
            });

            let isRunning = false;
            let isRunDisabled = false;
            let buttonText = "";

            if (actionBtn) {
                buttonText = (actionBtn.innerText || actionBtn.textContent || '').trim().toLowerCase();
                const ariaLabel = (actionBtn.getAttribute('aria-label') || '').toLowerCase();
                const ariaDis = actionBtn.getAttribute('aria-disabled');
                const isDis = actionBtn.disabled || ariaDis === 'true' || actionBtn.classList.contains('mat-button-disabled');

                const hasStop = buttonText.includes('stop') || ariaLabel.includes('stop') || ariaLabel.includes('cancel');
                const hasProgress = buttonText.includes('progress_activity') || actionBtn.querySelector('mat-spinner, ms-spinner, mat-progress-spinner') !== null;

                if ((hasStop || hasProgress) && !isDis) {
                    isRunning = true;
                } else if (buttonText.includes('run')) {
                    if (isDis) {
                        isRunDisabled = true;
                    }
                }
            }

            const hasSpinner = document.querySelector(
                'mat-progress-spinner, .typing-indicator, ms-spinner, .thought-activity-host[aria-expanded="true"], [data-test-id*="spinner" i]'
            ) !== null;

            if (hasSpinner) {
                isRunning = true;
            }

            return { is_running: isRunning, is_run_disabled: isRunDisabled, button_text: buttonText };
        }'''

        for i in range(16):
            res = await page.evaluate(js_fetch_state)
            print(f"t={i*0.5:.1f}s: is_running={res['is_running']}, is_disabled={res['is_run_disabled']}, btn='{res['button_text']}'")
            await asyncio.sleep(0.5)

        await context.close()

if __name__ == "__main__":
    asyncio.run(main())
