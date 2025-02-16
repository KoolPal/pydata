import asyncio
import json
import os
from datetime import datetime
import zendriver as zd
from bs4 import BeautifulSoup

async def extract_tracking_data(content):
    # ... [keeping the same extraction function as before]
    pass

async def main():
    browser = None
    print(f"Starting scraping at {datetime.utcnow().isoformat()}")
    
    try:
        # Create config with proper settings for GitHub Actions
        config = zd.Config(
            headless=True,
            sandbox=False,  # Required for GitHub Actions
            browser_executable_path='/usr/bin/google-chrome',
            # Increase timeouts for GitHub Actions environment
            browser_connection_timeout=2.0,
            browser_connection_max_tries=15
        )
        
        print("Browser configuration:")
        print(f"Executable: {config.browser_executable_path}")
        print(f"Connection timeout: {config.browser_connection_timeout}")
        print(f"Connection retries: {config.browser_connection_max_tries}")
        
        # Initialize browser
        browser = await zd.Browser.create(config)
        print("Browser started successfully")
        
        # Navigate to tracking page
        page = await browser.new_page()
        print("Created new page")
        
        url = 'https://www.icarry.in/track-shipment?a=347720741487'
        print(f"Navigating to: {url}")
        await page.goto(url)
        
        # Wait for page load
        await page.wait(5)
        print("Page loaded")
        
        # Get content and extract data
        content = await page.get_content()
        data = await extract_tracking_data(content)
        
        # Print results
        print("\n=== Tracking Information ===")
        print(json.dumps(data, indent=2))
        
        # Save data
        with open('tracking_data.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        # Take screenshot
        await page.save_screenshot('tracking_page.png')
        print("Screenshot saved")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        if browser and hasattr(browser, '_process'):
            stderr = await browser._process.stderr.read()
            print(f"Chrome stderr output: {stderr.decode()}")
        raise e
        
    finally:
        if browser:
            try:
                await browser.stop()
                print("Browser closed successfully")
            except Exception as e:
                print(f"Error closing browser: {str(e)}")
        print(f"Completed scraping at {datetime.utcnow().isoformat()}")

if __name__ == "__main__":
    asyncio.run(main())
