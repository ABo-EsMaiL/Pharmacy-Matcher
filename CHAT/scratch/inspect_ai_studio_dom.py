import asyncio
import os
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
        print("Navigating to AI Studio...")
        await page.goto("https://aistudio.google.com/prompts/new_chat", wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(5)
        
        info = await page.evaluate('''() => {
            const fileInputs = Array.from(document.querySelectorAll('input[type="file"]')).map(el => ({
                id: el.id,
                name: el.name,
                accept: el.accept,
                outer: el.outerHTML.slice(0, 150)
            }));
            
            const promptBox = document.querySelector('.prompt-box-container, .prompt-box, ms-prompt-box');
            let promptButtons = [];
            if (promptBox) {
                promptButtons = Array.from(promptBox.querySelectorAll('button')).map(b => ({
                    aria: b.getAttribute('aria-label') || '',
                    text: (b.innerText || '').trim(),
                    tooltip: b.getAttribute('mattooltip') || '',
                    html: b.outerHTML.slice(0, 150)
                }));
            }
            
            const allAddButtons = Array.from(document.querySelectorAll('button')).filter(b => {
                const a = (b.getAttribute('aria-label') || '').toLowerCase();
                const t = (b.innerText || '').toLowerCase();
                return a.includes('add') || a.includes('insert') || a.includes('upload') || t.includes('add') || t.includes('insert');
            }).map(b => ({
                aria: b.getAttribute('aria-label') || '',
                text: (b.innerText || '').trim(),
                tooltip: b.getAttribute('mattooltip') || '',
                html: b.outerHTML.slice(0, 150)
            }));
            
            return {
                url: window.location.href,
                fileInputs: fileInputs,
                promptButtons: promptButtons,
                allAddButtons: allAddButtons
            };
        }''')
        
        print(json.dumps(info, indent=2, ensure_ascii=False))
        await context.close()

if __name__ == "__main__":
    asyncio.run(main())
