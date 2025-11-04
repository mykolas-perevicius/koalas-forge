#!/usr/bin/env python3
"""
🐨 Koala's Forge - Demo Recording Script
Creates an automated demo showing key features
"""

import asyncio
import subprocess
import time
from pathlib import Path
from playwright.async_api import async_playwright

async def create_demo():
    """Create a demo video/screenshots of Koala's Forge"""

    # Start the server
    project_root = Path(__file__).parent.parent
    server_process = subprocess.Popen(
        ['python3', str(project_root / 'gui' / 'koalas_forge_server.py')],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Wait for server to start
    print("🚀 Starting Koala's Forge server...")
    await asyncio.sleep(5)

    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            record_video_dir=str(project_root / 'demo'),
            record_video_size={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()

        print("📹 Recording demo...")

        # Navigate to Koala's Forge
        await page.goto('http://localhost:8080')
        await page.wait_for_load_state('networkidle')
        await asyncio.sleep(2)

        # Take screenshot of landing page
        await page.screenshot(path=str(project_root / 'demo' / '01-landing.png'))
        print("✅ Screenshot: Landing page")

        # Show Wizard Mode
        await page.click('text=🧙 Wizard Mode')
        await asyncio.sleep(1)
        await page.screenshot(path=str(project_root / 'demo' / '02-wizard-mode.png'))
        print("✅ Screenshot: Wizard mode")

        # Select purposes in wizard
        await page.click('[data-purpose="development"]')
        await asyncio.sleep(0.5)
        await page.click('[data-purpose="ai"]')
        await asyncio.sleep(0.5)
        await page.screenshot(path=str(project_root / 'demo' / '03-wizard-selection.png'))
        print("✅ Screenshot: Wizard selections")

        # Go to next step
        await page.click('text=Next →')
        await asyncio.sleep(2)
        await page.screenshot(path=str(project_root / 'demo' / '04-wizard-recommendations.png'))
        print("✅ Screenshot: Wizard recommendations")

        # Switch to Expert Mode
        await page.click('text=🔧 Expert Mode')
        await asyncio.sleep(2)
        await page.screenshot(path=str(project_root / 'demo' / '05-expert-mode.png'))
        print("✅ Screenshot: Expert mode")

        # Click on preset pack
        await page.click('[data-preset="ai-developer"]')
        await asyncio.sleep(1)
        await page.screenshot(path=str(project_root / 'demo' / '06-preset-selected.png'))
        print("✅ Screenshot: Preset selected")

        # Scroll down to see app grid
        await page.evaluate('window.scrollTo(0, 600)')
        await asyncio.sleep(1)
        await page.screenshot(path=str(project_root / 'demo' / '07-app-grid.png'))
        print("✅ Screenshot: App grid")

        # Click on a category tab
        await page.evaluate('window.scrollTo(0, 400)')
        await asyncio.sleep(0.5)
        await page.click('[data-category="creative"]')
        await asyncio.sleep(1)
        await page.screenshot(path=str(project_root / 'demo' / '08-creative-category.png'))
        print("✅ Screenshot: Creative category")

        # Use search
        await page.fill('#searchBar', 'docker')
        await asyncio.sleep(1)
        await page.screenshot(path=str(project_root / 'demo' / '09-search.png'))
        print("✅ Screenshot: Search feature")

        # Clear search and go back to all
        await page.fill('#searchBar', '')
        await page.click('[data-category="all"]')
        await asyncio.sleep(1)

        # Select a few apps manually
        await page.evaluate('window.scrollTo(0, 600)')
        await asyncio.sleep(0.5)

        # Check dry run toggle
        await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        await asyncio.sleep(1)
        await page.check('#dryRunToggle')
        await asyncio.sleep(0.5)
        await page.screenshot(path=str(project_root / 'demo' / '10-dry-run-enabled.png'))
        print("✅ Screenshot: Dry run enabled")

        # Start installation (dry run)
        await page.click('#installBtn')
        await asyncio.sleep(2)
        await page.screenshot(path=str(project_root / 'demo' / '11-installation-modal.png'))
        print("✅ Screenshot: Installation modal")

        # Wait for some progress
        await asyncio.sleep(3)
        await page.screenshot(path=str(project_root / 'demo' / '12-installation-progress.png'))
        print("✅ Screenshot: Installation in progress")

        # Wait for completion
        await asyncio.sleep(10)
        await page.screenshot(path=str(project_root / 'demo' / '13-installation-complete.png'))
        print("✅ Screenshot: Installation complete")

        # Close modal
        await page.click('.close-btn')
        await asyncio.sleep(1)

        # Final screenshot
        await page.evaluate('window.scrollTo(0, 0)')
        await asyncio.sleep(1)
        await page.screenshot(path=str(project_root / 'demo' / '14-final.png'))
        print("✅ Screenshot: Final")

        # Close browser
        await context.close()
        await browser.close()

    # Stop server
    server_process.terminate()
    server_process.wait()

    print("\n🎉 Demo recording complete!")
    print(f"📁 Screenshots saved to: {project_root / 'demo'}")
    print(f"🎬 Video saved to: {project_root / 'demo'}")

if __name__ == "__main__":
    asyncio.run(create_demo())
