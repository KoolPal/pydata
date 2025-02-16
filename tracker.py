import asyncio
import logging
import os
from datetime import datetime, timezone
import json

import zendriver as zd

# Configure logging
logging.basicConfig(
    level=os.getenv('ZENDRIVER_LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

CURRENT_USER = os.getenv('CURRENT_USER', 'KoolPal')
CURRENT_TIME = datetime.strptime(os.getenv('CURRENT_UTC', '2025-02-16 08:30:54'), '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)

async def main():
    browser = None
    tracking_number = os.getenv('TRACKING_NUMBER', '347720741487')
    
    try:
        # Configure browser with comprehensive anti-detection based on all recent issues
        config = zd.Config(
            headless=False,  # Issue #72: Headless immediately detected
            sandbox=False,
            expert=True,  # For shadow DOM access, but needs additional handling
            browser_executable_path='/usr/bin/google-chrome',
            browser_connection_timeout=10.0,
            browser_connection_max_tries=20,
            browser_args=[
                # GPU/WebGL fixes from Issue #20
                '--enable-unsafe-webgpu',
                '--enable-features=Vulkan,SkiaGraphite',
                '--use-gl=desktop',
                '--enable-gpu-rasterization',
                '--enable-zero-copy',
                '--ignore-gpu-blocklist',
                
                # Memory/shm fixes
                '--disable-dev-shm-usage',
                '--no-sandbox',
                
                # Anti-detection from multiple issues
                '--disable-blink-features=AutomationControlled',
                '--disable-features=IsolateOrigins',
                '--disable-site-isolation-trials',
                
                # Window properties
                '--window-size=1920,1080',
                '--start-maximized',
                
                # Additional Cloudflare bypass flags
                '--enable-javascript',
                '--enable-cookies',
                '--disable-web-security',
                '--disable-notifications',
                '--no-default-browser-check'
            ]
        )

        logger.info(f"Starting browser at {CURRENT_TIME.isoformat()} as {CURRENT_USER}")
        browser = await zd.Browser.create(config)
        
        # Create new page with enhanced capabilities
        page = await browser.new_page()
        
        # Inject protections before navigation (from Issue #72 and #20)
        await page.evaluate("""() => {
            // Override common detection methods
            Object.defineProperties(navigator, {
                webdriver: { get: () => undefined },
                // Add GPU capabilities (Issue #20)
                gpu: { 
                    get: () => ({
                        wgpu: {
                            requestAdapter: async () => ({
                                name: 'NVIDIA GeForce RTX 3080',
                                features: new Set(['texture-compression-bc'])
                            })
                        }
                    })
                },
                // Additional properties
                languages: { get: () => ['en-US', 'en'] },
                deviceMemory: { get: () => 8 },
                hardwareConcurrency: { get: () => 8 },
                platform: { get: () => 'Linux x86_64' }
            });

            // WebGL fingerprint protection
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                // Spoof common WebGL parameters
                const spoofedParams = {
                    37445: 'NVIDIA GeForce RTX 3080/PCIe/SSE2',
                    37446: 'NVIDIA Corporation'
                };
                return spoofedParams[parameter] || getParameter.call(this, parameter);
            };
        }""")

        url = f'https://www.icarry.in/track-shipment?a={tracking_number}'
        logger.info(f"Navigating to: {url}")
        
        await page.goto(url)
        
        # Handle Cloudflare challenge (Issue #64)
        await page.wait_for_ready_state("complete")
        content = await page.get_content()
        
        # Check for Cloudflare elements
        if "cf-" in content or "turnstile" in content:
            logger.info("Detected Cloudflare challenge")
            
            # Handle shadow DOM elements (Issue #38)
            await page.evaluate("""() => {
                document.querySelectorAll('*').forEach(el => {
                    if (el.shadowRoot) el.shadowRoot.mode = 'open'
                })
            }""")
            
            # Wait for challenge
            await page.wait(10)
        
        # Get final content
        content = await page.get_content()
        logger.info("Page HTML Content:")
        print(content)
        
        # Save screenshot for verification
        await page.save_screenshot('page.png')
        logger.info("Screenshot saved as page.png")

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        if browser and hasattr(browser, '_process'):
            stderr = await browser._process.stderr.read()
            logger.error(f"Chrome stderr output: {stderr.decode()}")
    finally:
        if browser:
            await browser.stop()
            logger.info("Browser closed successfully")

if __name__ == "__main__":
    asyncio.run(main())
