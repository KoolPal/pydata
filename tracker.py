"""
iCarry Tracking Script using Zendriver
Author: KoolPal
Created: 2025-02-16
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

from bs4 import BeautifulSoup
import zendriver as zd

# Configure logging
logging.basicConfig(
    level=os.getenv('ZENDRIVER_LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TrackingError(Exception):
    """Custom exception for tracking-related errors"""
    pass

async def extract_tracking_data(content: str) -> Dict:
    """
    Extract tracking information from the page content.
    Uses BeautifulSoup for reliable HTML parsing.
    """
    try:
        soup = BeautifulSoup(content, 'lxml')
        
        # Extract tracking status
        status_elem = soup.select_one('div.tracking-status strong')
        if not status_elem:
            raise TrackingError("Could not find tracking status element")
        
        # Extract location and timestamp
        location_elem = soup.select_one('div.current-location')
        timestamp_elem = soup.select_one('div.last-update time')
        
        # Extract tracking events
        events = []
        for event in soup.select('div.tracking-event'):
            events.append({
                'date': event.select_one('.event-date').get_text(strip=True),
                'time': event.select_one('.event-time').get_text(strip=True),
                'location': event.select_one('.event-location').get_text(strip=True),
                'description': event.select_one('.event-desc').get_text(strip=True)
            })
        
        tracking_data = {
            'tracking_number': os.getenv('TRACKING_NUMBER'),
            'status': status_elem.get_text(strip=True),
            'current_location': location_elem.get_text(strip=True) if location_elem else None,
            'last_update': timestamp_elem.get_text(strip=True) if timestamp_elem else None,
            'events': events,
            'extracted_at': datetime.now(timezone.utc).isoformat()
        }
        
        return tracking_data
    
    except Exception as e:
        raise TrackingError(f"Failed to extract tracking data: {str(e)}") from e

async def main():
    browser = None
    tracking_number = os.getenv('TRACKING_NUMBER')
    if not tracking_number:
        raise ValueError("TRACKING_NUMBER environment variable is required")
    
    start_time = datetime.now(timezone.utc)
    logger.info(f"Starting tracking check at {start_time.isoformat()}")
    
    try:
        # Configure browser with optimal settings based on recent issues
        config = zd.Config(
            headless=True,
            sandbox=False,  # Required for GitHub Actions (issue #70)
            browser_executable_path='/usr/bin/google-chrome',  # Explicit path for GitHub Actions
            browser_connection_timeout=5.0,  # Increased timeout (issue #61)
            browser_connection_max_tries=20,
            browser_args=[
                '--disable-dev-shm-usage',  # Fix for CI environments
                '--disable-blink-features=AutomationControlled',  # Reduce detection
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-site-isolation-trials'
            ]
        )
        
        logger.info("Initializing browser with config:")
        logger.info(f"Executable: {config.browser_executable_path}")
        logger.info(f"Connection timeout: {config.browser_connection_timeout}")
        logger.info(f"Max retries: {config.browser_connection_max_tries}")
        
        # Initialize browser
        browser = await zd.Browser.create(config)
        logger.info("Browser started successfully")
        
        # Create new tab and navigate
        page = await browser.new_page()
        logger.info("Created new page")
        
        url = f'https://www.icarry.in/track-shipment?a={tracking_number}'
        logger.info(f"Navigating to: {url}")
        
        # Navigate and wait for load
        await page.goto(url)
        await page.wait_for_ready_state("complete")
        await page.wait(3)  # Additional wait for dynamic content
        logger.info("Page loaded")
        
        # Take screenshot before extraction
        screenshot_path = Path('tracking_screenshot.png')
        await page.save_screenshot(screenshot_path)
        logger.info(f"Screenshot saved to {screenshot_path}")
        
        # Get content and extract data
        content = await page.get_content()
        tracking_data = await extract_tracking_data(content)
        
        # Save tracking data
        output_path = Path('tracking_data.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(tracking_data, indent=2, ensure_ascii=False, f)
        logger.info(f"Tracking data saved to {output_path}")
        
        # Log summary
        logger.info(f"Status: {tracking_data['status']}")
        logger.info(f"Location: {tracking_data['current_location']}")
        logger.info(f"Last Update: {tracking_data['last_update']}")
        
    except TrackingError as e:
        logger.error(f"Tracking data extraction failed: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        if browser and hasattr(browser, '_process'):
            stderr = await browser._process.stderr.read()
            logger.error(f"Chrome stderr output: {stderr.decode()}")
        sys.exit(1)
    finally:
        if browser:
            try:
                await browser.stop()
                logger.info("Browser closed successfully")
            except Exception as e:
                logger.error(f"Error closing browser: {str(e)}")
        
        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()
        logger.info(f"Tracking check completed at {end_time.isoformat()} (duration: {duration:.2f}s)")

if __name__ == "__main__":
    asyncio.run(main())
