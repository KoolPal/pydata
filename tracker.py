import asyncio
import logging
import zendriver as zd

logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)

async def main():
    try:
        logger.info("Starting browser")
        browser = await zd.start(
            browser_executable_path="/usr/bin/google-chrome",
            headless=True,
            no_sandbox=True
        )
        logger.info("Browser started successfully")
        await browser.stop()
        
    except Exception as e:
        logger.error(f"Browser start failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
