import asyncio
import logging
import os

import zendriver as zd

logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)

async def main():
    try:
        # Focus only on browser launch settings
        config = zd.Config(
            headless=True,
            sandbox=False,
            no_sandbox=True,  # Explicitly set no_sandbox
            browser_executable_path='/usr/bin/google-chrome',
            browser_args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage'
            ]
        )
        
        logger.info("Starting browser")
        browser = await zd.Browser.create(config)
        
        # Just try to load about:blank first to verify browser works
        page = await browser.new_page()
        await page.goto("about:blank")
        
        logger.info("Browser started successfully")
        await browser.stop()
        
    except Exception as e:
        logger.error(f"Browser start failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
