import asyncio
from zendriver import CloudflareUnblockClient
from bs4 import BeautifulSoup
import re
from datetime import datetime

async def main():
    # Initialize the Cloudflare bypass client
    client = CloudflareUnblockClient()
    
    # URL to scrape
    url = "https://www.icarry.in/track-shipment?a=347720741487"
    
    try:
        # Get the page content
        response = await client.get(url)
        content = response.text
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')
        
        # Helper function to extract content using regex
        def extract_content(content, pattern):
            match = re.search(pattern, content)
            return match.group(1) if match else None
        
        # Extract tracking information
        courier_name = extract_content(content, r'Courier Name\s*:</td>\s*<td>(.*?)</td>')
        status = extract_content(content, r'Status:\s*</b>\s*<span[^>]*>(.*?)</span>')
        if status:
            status = re.sub(r'<[^>]*>', '', status)
        destination = extract_content(content, r'Destination:\s*</b>\s*<span[^>]*>(.*?)</span>')
        
        # Extract tracking details table
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
        
        # Print the results in a formatted way
        print("\n=== Tracking Information ===")
        print(f"Courier: {courier_name}")
        print(f"Status: {status}")
        print(f"Destination: {destination}")
        print("\n=== Tracking Timeline ===")
        for detail in tracking_details:
            print(f"\nDate: {detail['date']}")
            print(f"Location: {detail['location'] or 'N/A'}")
            print(f"Status: {detail['remarks']}")
            
    except Exception as e:
        print(f"Error occurred: {str(e)}")
    finally:
        await client.close()

if __name__ == "__main__":
    print(f"Starting scraping at {datetime.utcnow().isoformat()}")
    asyncio.run(main())
    print(f"Completed scraping at {datetime.utcnow().isoformat()}")
