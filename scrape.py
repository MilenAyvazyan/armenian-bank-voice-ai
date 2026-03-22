import json
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup


async def get_page_text(browser, url):
    page = await browser.new_page()
    print(f"scraping: {url}")
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(5000)

        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')

        for tag in soup(["script", "style", "header", "footer", "nav"]):
            tag.decompose()

        lines = soup.get_text(separator='\n').splitlines()
        return '\n'.join(line.strip() for line in lines if line.strip())

    except Exception as e:
        print(f"failed on {url}: {e}")
        return ""
    finally:
        await page.close()


async def main():
    with open('config.json', 'r') as f:
        config = json.load(f)

    all_data = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        for bank in config['banks']:
            print(f"\n--- {bank['name']} ---")
            for page in bank['pages']:
                text = await get_page_text(browser, page['url'])
                if text:
                    all_data.append({
                        "bank": bank['name'],
                        "topic": page['topic'],
                        "url": page['url'],
                        "text": text
                    })

        await browser.close()

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print(f"\ndone. total pages: {len(all_data)}")


if __name__ == "__main__":
    asyncio.run(main())
