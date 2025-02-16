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
        
        logger.info("Opening tracking page")
        tab = await browser.new_tab()
        await tab.goto("https://www.icarry.in/track-shipment?a=347720741487")
        
        # Just get and log the content
        content = await tab.get_content()
        logger.info("Page content:")
        print(content)
        
        await browser.stop()
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
