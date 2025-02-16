import asyncio
import json
import os
from datetime import datetime
import zendriver as zd
from bs4 import BeautifulSoup

async def extract_tracking_data(content):
    soup = BeautifulSoup(content, 'lxml')
    
    # Extract basic information
    status = soup.find('span', style='font-size: 16px; color:green')
    zone = soup.find('span', style='font-size: 16px; color:blue')
    destination = soup.find_all('span', style='font-size: 16px; color:blue')[1]
    
    # Extract tracking details
    tracking_details = []
    table = soup.find('table')
    if table:
        rows = table.find_all('tr')[1:]  # Skip header row
        for row in rows:
            cells = row.find_all('td')
            if len(cells) == 3:
                tracking_details.append({
                    'date': cells[0].text.strip(),
                    'location': cells[1].text.strip(),
                    'remarks': cells[2].text.strip()
                })
    
    # Extract courier details
    courier_info = {}
    courier_table = soup.find_all('table')[1]
    if courier_table:
        rows = courier_table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) == 2:
                key = cells[0].text.strip().rstrip(':')
                value = cells[1].text.strip()
                courier_info[key] = value
    
    return {
        'status': status.text.strip() if status else None,
        'estimated_zone': zone.text.strip() if zone else None,
        'destination': destination.text.strip() if destination else None,
        'tracking_details': tracking_details,
        'courier_info': courier_info,
        'timestamp': datetime.utcnow().isoformat()
    }

async def main():
    browser = None
    print(f"Starting scraping at {datetime.utcnow().isoformat()}")
    
    try:
        # Initialize the browser with specific configurations for GitHub Actions
        chrome_path = '/opt/hostedtoolcache/chrome/stable/x64/chrome'
        
        # Initialize browser with correct arguments
        browser = await zd.start(
            headless=True,
            no_sandbox=True,
            disable_dev_shm=True,
            browser_executable_path=chrome_path if os.path.exists(chrome_path) else None,
            extra_args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-software-rasterizer',
                '--disable-extensions'
            ]
        )
        print("Browser started successfully")
        
        # Create a new page and navigate to the tracking URL
        page = await browser.get('https://www.icarry.in/track-shipment?a=347720741487')
        print("Navigated to tracking page")
        
        # Wait for the page to load completely
        await page.wait(5)  # Wait 5 seconds for any dynamic content
        print("Page loaded")
        
        # Get the page content
        content = await page.get_content()
        print("Retrieved page content")
        
        # Extract and process the data
        data = await extract_tracking_data(content)
        
        # Print the results
        print("\n=== Tracking Information ===")
        print(f"Status: {data['status']}")
        print(f"Estimated Zone: {data['estimated_zone']}")
        print(f"Destination: {data['destination']}")
        print("\n=== Tracking Timeline ===")
        for detail in data['tracking_details']:
            print(f"\nDate: {detail['date']}")
            print(f"Location: {detail['location']}")
            print(f"Status: {detail['remarks']}")
        
        print("\n=== Courier Information ===")
        for key, value in data['courier_info'].items():
            print(f"{key}: {value}")
            
        # Save the data to a JSON file
        with open('tracking_data.json', 'w') as f:
            json.dump(data, f, indent=2)
            
        # Take a screenshot for verification
        await page.save_screenshot('tracking_page.png')
        print("Screenshot saved")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise e
        
    finally:
        # Always close the browser
        if browser:
            try:
                await browser.stop()
                print("Browser closed successfully")
            except Exception as e:
                print(f"Error closing browser: {str(e)}")
        print(f"Completed scraping at {datetime.utcnow().isoformat()}")

if __name__ == "__main__":
    asyncio.run(main())
