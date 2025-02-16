import asyncio
import logging
import os

import zendriver as zd

logging.basicConfig(
    level=os.getenv('ZENDRIVER_LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    browser = None
    tracking_number = os.getenv('TRACKING_NUMBER')
    
    try:
        config = zd.Config(
            headless=True,
            sandbox=False,  # Required for GitHub Actions
            browser_executable_path='/usr/bin/google-chrome',
            browser_args=[
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
            ]
        )
        
        logger.info("Starting browser")
        browser = await zd.Browser.create(config)
        
        page = await browser.new_page()
        url = f'https://www.icarry.in/track-shipment?a={tracking_number}'
        logger.info(f"Navigating to: {url}")
        
        await page.goto(url)
        await page.wait_for_ready_state("complete")
        
        # Print page content to verify access
        content = await page.get_content()
        print(content)
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise
    finally:
        if browser:
            await browser.stop()

if __name__ == "__main__":
    asyncio.run(main())
