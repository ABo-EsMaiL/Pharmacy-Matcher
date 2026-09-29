import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        # connect to existing chrome browser if remote debugging, or inspect via playwright
        pass

if __name__ == "__main__":
    pass
