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
        await asyncio.sleep(4)
        
        info = await page.evaluate('''() => {
            const elements = [];
            // Look for toggles, checkboxes, slide-toggles, buttons
            const nodes = document.querySelectorAll('mat-slide-toggle, mat-checkbox, button, [role="switch"], .tool-item, ms-tool-toggle, mat-expansion-panel');
            nodes.forEach(n => {
                const text = (n.innerText || n.textContent || '').trim().replace(/\\s+/g, ' ');
                const aria = n.getAttribute('aria-label') || '';
                const checked = n.getAttribute('aria-checked') || n.classList.contains('mat-mdc-slide-toggle-checked') || n.querySelector('input[type="checkbox"]')?.checked;
                if (/search|ground|tool|function|code/i.test(text + ' ' + aria)) {
                    elements.push({
                        tag: n.tagName,
                        className: n.className,
                        text: text.slice(0, 100),
                        ariaLabel: aria,
                        checked: checked,
                        id: n.id
                    });
                }
            });
            return elements;
        }''')
        
        print("Found Search/Tool elements:")
        for idx, item in enumerate(info):
            print(f"[{idx}] Tag: {item['tag']} | Checked: {item['checked']} | Aria: '{item['ariaLabel']}' | Text: '{item['text']}'")

        # Also take screenshot
        await page.screenshot(path="scratch_studio_tools.png")
        await context.close()

if __name__ == "__main__":
    asyncio.run(main())
