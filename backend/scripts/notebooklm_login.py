#!/usr/bin/env python
"""Quick login using existing browser profile."""

import asyncio
import json
from pathlib import Path

from playwright.async_api import async_playwright


async def main():
    storage_path = Path.home() / ".notebooklm" / "storage_state.json"
    profile_path = Path.home() / ".notebooklm" / "browser_profile"

    print("Using existing browser profile...")
    print("1. If not logged in, log in now")
    print("2. When you see your notebooks, close this terminal")
    print("   (browser will close automatically)")
    print("Or press Ctrl+C to cancel")

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch_persistent_context(
                user_data_dir=str(profile_path),
                headless=False,
            )

            page = await browser.new_page()
            await page.goto("https://notebooklm.google.com")

            # Wait up to 2 minutes for user to log in
            await asyncio.wait_for(asyncio.sleep(120), timeout=130)

            cookies = await browser.cookies()

            with open(storage_path, "w") as f:
                json.dump({"cookies": cookies}, f, indent=2)

            print(f"Saved {len(cookies)} cookies")
            await browser.close()

        print(f"Done! Saved to {storage_path}")
    except asyncio.TimeoutError:
        print("Timeout - saved what we have")
    except KeyboardInterrupt:
        print("Cancelled")


if __name__ == "__main__":
    asyncio.run(main())
