#!/usr/bin/env python3
"""
EPIC Booklet Downloader
Download children's books from getepic.com and generate saddle-stitch booklet PDFs.

Usage:
    python epic_downloader.py --book-id 47110
    python epic_downloader.py --collection 34822900
    python epic_downloader.py --book-id 47110 --output ./my_books
    python epic_downloader.py --book-id 47110 --token <epic_jwt>

Requirements:
    pip install Pillow requests

How it works:
    1. Authenticates via Epic's new auth API (educator account)
    2. Reverse-engineers the reqSig parameter (MD5 + salt)
    3. Fetches book metadata via WebBook.getFullDataForWeb
    4. Downloads all page images from CDN
    5. Generates a saddle-stitch booklet PDF (print-ready)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import glob
from pathlib import Path
from typing import Optional

try:
    import requests
except ImportError:
    print("Error: requests library required. Install with: pip install requests")
    sys.exit(1)

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow library required. Install with: pip install Pillow")
    sys.exit(1)


# ─── Constants ────────────────────────────────────────────────────────────────

EPIC_SALT = "#$%^&*(OIKJHBDE$R%^Y&UIOL"
EPIC_API_BASE = "https://api-web.getepic.com/webapi/index.php"
EPIC_CDN_BASE = "https://cdn-gcp-media-drm-v2.getepic.com"
EPIC_AUTH_PASS_SALT = "(Y&(*SYH!!--csDI)"
EPIC_NEW_AUTH_URL = "https://api-web.getepic.com/newauth/auth/login"


# ─── Signature ────────────────────────────────────────────────────────────────

def compute_reqsig(params: dict) -> str:
    """
    Compute the reqSig parameter for Epic API requests.
    
    Algorithm (reverse-engineered from main.*.js):
        1. Sort parameter keys alphabetically
        2. Concatenate: salt + key1 + value1 + key2 + value2 + ...
        3. Return MD5 hash of the result
    """
    keys = sorted(params.keys())
    sig_str = EPIC_SALT
    for k in keys:
        v = params[k]
        sig_str += k + (json.dumps(v) if isinstance(v, (dict, list)) else str(v))
    return hashlib.md5(sig_str.encode()).hexdigest()


def compute_pass_hash(password: str) -> str:
    """
    Compute the password hash for Epic login.
    
    Algorithm (reverse-engineered from main.*.js):
        MD5(password + "(Y&(*SYH!!--csDI)")
    """
    return hashlib.md5((password + EPIC_AUTH_PASS_SALT).encode()).hexdigest()


# ─── API Client ───────────────────────────────────────────────────────────────

class EpicClient:
    """Epic API client with automatic authentication and signature generation."""
    
    def __init__(self, email: Optional[str] = None, password: Optional[str] = None, token: Optional[str] = None):
        self.email = email
        self.password = password
        self.token = token
        self.session = requests.Session()
        self.session.headers.update({
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.9",
            "origin": "https://www.getepic.com",
            "referer": "https://www.getepic.com/",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/131.0.0.0 Safari/537.36",
            "x-flagsmith-auth": "1",
        })
        if self.token:
            self.session.headers["authorization"] = f"Bearer {self.token}"
    
    def login(self) -> bool:
        """Authenticate and obtain a JWT token, unless one was provided."""
        if self.token:
            print("✓ Using provided access token")
            return True

        if not self.email or not self.password:
            print("✗ Email and password required when no access token is provided")
            return False

        # Attempt 1: New auth endpoint
        try:
            pass_hash = compute_pass_hash(self.password)
            resp = self.session.post(
                EPIC_NEW_AUTH_URL,
                json={"email": self.email, "pass": pass_hash},
                headers={"content-type": "application/json"},
                timeout=10,
            )
            data = resp.json()
            if isinstance(data, dict) and data.get("accessToken"):
                self.token = data["accessToken"]
                self.session.headers["authorization"] = f"Bearer {self.token}"
                print("✓ Login successful (newauth)")
                return True
        except Exception as e:
            print(f"  newauth failed: {e}")

        # Attempt 2: WebAPI auth endpoint
        try:
            params = {
                "email": self.email,
                "pass": pass_hash,
                "dev": "web",
                "ver": "3.5",
            }
            sig = compute_reqsig({k: v for k, v in params.items() if k != "reqSig"})
            params["reqSig"] = sig
            resp = self.session.post(
                f"{EPIC_API_BASE}?class=WebAuth&method=login",
                data=params,
                headers={"content-type": "application/x-www-form-urlencoded; charset=UTF-8"},
                timeout=10,
            )
            # Handle double-encoded JSON response
            raw = resp.json()
            if isinstance(raw, str):
                raw = json.loads(raw)
            if isinstance(raw, dict) and raw.get("success") and raw.get("result", {}).get("accessToken"):
                self.token = raw["result"]["accessToken"]
                self.session.headers["authorization"] = f"Bearer {self.token}"
                print("✓ Login successful (webapi)")
                return True
        except Exception as e:
            print(f"  webapi failed: {e}")

        # Attempt 3: Playwright browser login (most reliable)
        print("  API login failed, trying Playwright browser login...")
        token = self._playwright_login()
        if token:
            self.token = token
            self.session.headers["authorization"] = f"Bearer {self.token}"
            print("✓ Login successful (Playwright)")
            return True

        print("✗ All login methods failed")
        return False

    def _playwright_login(self) -> str | None:
        """Login via Playwright browser automation. Returns JWT token or None."""
        try:
            import asyncio
            from playwright.async_api import async_playwright
        except ImportError:
            print("  Playwright not installed. Run: pip install playwright && playwright install chromium")
            return None

        async def _do_login():
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto("https://www.getepic.com/sign-in/parent", timeout=30000)
                await asyncio.sleep(2)
                await page.fill('input[placeholder="Email"]', self.email)
                await page.fill('input[type="password"]', self.password)
                await asyncio.sleep(0.5)
                await page.click('button[type="submit"]')
                await asyncio.sleep(5)
                token = await page.evaluate("localStorage.getItem('accessToken')")
                await browser.close()
                return token.strip('"') if token else None

        try:
            return asyncio.run(_do_login())
        except Exception as e:
            print(f"  Playwright login error: {e}")
            return None
    
    def _signed_get(self, cls: str, method: str, params: dict) -> dict:
        """Make a signed GET request to the Epic API."""
        sig = compute_reqsig(params)
        params["reqSig"] = sig
        
        qs = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{EPIC_API_BASE}?class={cls}&method={method}&{qs}"
        
        resp = self.session.get(url)
        return resp.json()
    
    def get_book_data(self, book_id: str) -> dict | None:
        """Fetch full book metadata including page image URLs."""
        params = {
            "bookId": book_id,
            "dev": "web",
            "isFreemium": "0",
            "needAssignmentType": "0",
            "timezoneOffsetMinutes": "480",
            "ver": "3.5",
        }
        
        data = self._signed_get("WebBook", "getFullDataForWeb", params)
        
        if data.get("success"):
            return data.get("result")
        
        print(f"  ✗ Failed to get book {book_id}: {data.get('errorMessage')}")
        return None
    
    def get_collection_books(self, collection_id: str) -> list[dict]:
        """Fetch all book IDs from a collection/favorites."""
        # First, get the favorites list
        params = {"dev": "web", "ver": "3.5"}
        data = self._signed_get("WebFavorite", "getFavoriteRowsForUserId", params)
        
        if not data.get("success"):
            print(f"  ✗ Failed to get collection: {data.get('errorMessage')}")
            return []
        
        result = data.get("result", {})
        books = []
        
        # Extract books from the result
        for key in result:
            val = result[key]
            if isinstance(val, list):
                for item in val:
                    if isinstance(item, dict):
                        bid = item.get("bookId") or item.get("id") or item.get("modelId")
                        title = item.get("title") or item.get("name")
                        if bid and title:
                            books.append({"id": str(bid), "title": title})
        
        return books


# ─── Image Download ───────────────────────────────────────────────────────────

def download_pages(urls: list[str], output_dir: str) -> list[str]:
    """Download all page images and return paths of successfully downloaded files."""
    os.makedirs(output_dir, exist_ok=True)
    downloaded = []
    
    for i, url in enumerate(urls):
        out_path = os.path.join(output_dir, f"p{i+1:03d}.jpg")
        
        # Skip if already downloaded
        if os.path.exists(out_path) and os.path.getsize(out_path) > 500:
            downloaded.append(out_path)
            continue
        
        try:
            resp = requests.get(url, timeout=15)
            if resp.status_code == 200 and len(resp.content) > 500:
                with open(out_path, "wb") as f:
                    f.write(resp.content)
                downloaded.append(out_path)
        except Exception:
            pass
    
    return downloaded


# ─── PDF Generation ───────────────────────────────────────────────────────────

def create_booklet_pdf(image_paths: list[str], output_path: str) -> bool:
    """
    Create a saddle-stitch booklet PDF from page images.
    
    The pages are reordered so that when printed double-sided
    and folded, they appear in the correct reading order.
    """
    if not image_paths:
        return False
    
    try:
        images = [Image.open(p).convert("RGB") for p in image_paths]
    except Exception as e:
        print(f"  ✗ Error loading images: {e}")
        return False
    
    # Get dimensions from first page
    w, h = images[0].size
    
    # Pad to multiple of 4 (required for booklet format)
    while len(images) % 4 != 0:
        images.append(Image.new("RGB", (w, h), (255, 255, 255)))
    
    n = len(images)
    half = n // 2
    
    # Reorder for saddle-stitch:
    # Sheet 1 front: page N, page 1
    # Sheet 1 back: page 2, page N-1
    # Sheet 2 front: page N-2, page 3
    # ...
    ordered = []
    for i in range(half):
        ordered.append(images[n - 1 - i])  # outer back
        ordered.append(images[i])           # outer front
    
    # Save as PDF
    try:
        ordered[0].save(
            output_path,
            "PDF",
            save_all=True,
            append_images=ordered[1:],
            resolution=150,
        )
        return True
    except Exception as e:
        print(f"  ✗ Error saving PDF: {e}")
        return False


# ─── Main ─────────────────────────────────────────────────────────────────────

def sanitize_filename(name: str, max_len: int = 50) -> str:
    """Remove unsafe characters from filename."""
    return re.sub(r'[<>:"/\\|?*]', '', name).strip()[:max_len]


def process_book(client: EpicClient, book_id: str, output_dir: str) -> bool:
    """Download a single book and generate its booklet PDF."""
    # Get book data
    book_data = client.get_book_data(book_id)
    if not book_data:
        return False
    
    book = book_data.get("book", {})
    epub = book_data.get("epub", {})
    spine = epub.get("spine", [])
    
    title = book.get("title", f"book_{book_id}")
    num_pages = len(spine)
    
    if num_pages == 0:
        print(f"  ✗ No pages found for {title}")
        return False
    
    print(f"  📖 {title} ({num_pages} pages)")
    
    # Extract CDN URLs
    urls = []
    for page in spine:
        cdn_url = page.get("pageCdn") or ""
        if cdn_url:
            urls.append(cdn_url)
    
    if not urls:
        print(f"  ✗ No CDN URLs found")
        return False
    
    # Download pages
    safe_title = sanitize_filename(title)
    book_dir = os.path.join(output_dir, safe_title)
    pages_dir = os.path.join(book_dir, "pages")
    
    downloaded = download_pages(urls, pages_dir)
    print(f"  ↓ Downloaded {len(downloaded)}/{num_pages} pages")
    
    if not downloaded:
        return False
    
    # Generate booklet PDF
    pdf_path = os.path.join(book_dir, f"{safe_title}.pdf")
    if create_booklet_pdf(sorted(downloaded), pdf_path):
        size_kb = os.path.getsize(pdf_path) // 1024
        print(f"  ✅ PDF: {pdf_path} ({size_kb} KB)")
        return True
    
    return False


def main():
    parser = argparse.ArgumentParser(
        description="Download Epic books and generate print-ready booklet PDFs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --book-id 47110
  %(prog)s --book-id 47110 --token <epic_jwt>
  %(prog)s --book-id 47110 --email user@edu.cn --password mypass
  %(prog)s --book-ids 47110,47200,37798
  %(prog)s --collection 34822900

Environment variables (alternative to CLI args):
  EPIC_ACCESS_TOKEN - Epic JWT access token
  EPIC_EMAIL        - Epic account email
  EPIC_PASSWORD     - Epic account password
        """,
    )
    
    parser.add_argument("--book-id", help="Single book ID to download")
    parser.add_argument("--book-ids", help="Comma-separated book IDs")
    parser.add_argument("--collection", help="Collection/favorites ID to download all books")
    parser.add_argument("--email", default=os.environ.get("EPIC_EMAIL"), help="Epic account email")
    parser.add_argument("--password", default=os.environ.get("EPIC_PASSWORD"), help="Epic account password")
    parser.add_argument("--token", default=os.environ.get("EPIC_ACCESS_TOKEN"), help="Epic JWT access token (alternative to email/password)")
    parser.add_argument("--output", "-o", default="./epic_books", help="Output directory (default: ./epic_books)")
    
    args = parser.parse_args()
    
    if not args.token and (not args.email or not args.password):
        print("Error: provide either --token/EPIC_ACCESS_TOKEN or email and password (via --email/--password or EPIC_EMAIL/EPIC_PASSWORD)")
        sys.exit(1)
    
    if not any([args.book_id, args.book_ids, args.collection]):
        print("Error: provide --book-id, --book-ids, or --collection")
        sys.exit(1)
    
    # Login
    client = EpicClient(args.email, args.password, args.token)
    if not client.login():
        sys.exit(1)
    
    os.makedirs(args.output, exist_ok=True)
    
    # Collect book IDs
    book_ids = []
    
    if args.book_id:
        book_ids.append(args.book_id)
    elif args.book_ids:
        book_ids = [bid.strip() for bid in args.book_ids.split(",")]
    elif args.collection:
        print(f"\n📚 Fetching collection {args.collection}...")
        books = client.get_collection_books(args.collection)
        if not books:
            print("No books found in collection")
            sys.exit(1)
        print(f"  Found {len(books)} books")
        book_ids = [b["id"] for b in books]
        # Save book list
        with open(os.path.join(args.output, "collection.json"), "w") as f:
            json.dump(books, f, indent=2, ensure_ascii=False)
    
    # Process each book
    print(f"\n📥 Downloading {len(book_ids)} books to {args.output}/\n")
    
    success = 0
    for i, bid in enumerate(book_ids):
        print(f"[{i+1}/{len(book_ids)}]", end=" ")
        if process_book(client, bid, args.output):
            success += 1
        time.sleep(0.3)  # Rate limit
    
    print(f"\n{'='*50}")
    print(f"✅ Done! {success}/{len(book_ids)} books downloaded")
    
    # List generated PDFs
    pdfs = glob.glob(os.path.join(args.output, "**/*.pdf"), recursive=True)
    if pdfs:
        total_mb = sum(os.path.getsize(p) for p in pdfs) / 1024 / 1024
        print(f"📄 {len(pdfs)} PDFs, {total_mb:.1f} MB total")
        print(f"\nPrint instructions:")
        print(f"  1. Print double-sided")
        print(f"  2. Flip on short edge")
        print(f"  3. Fold in half")
        print(f"  4. Staple at fold (2 staples)")


if __name__ == "__main__":
    main()
