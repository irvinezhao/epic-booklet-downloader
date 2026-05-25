---
name: epic-booklet
description: |
  Download children's books from getepic.com and generate print-ready saddle-stitch booklet PDFs.
  Use this skill whenever the user wants to download Epic books, create printable booklets from Epic,
  or mentions getepic.com book downloading. Also trigger on: EPIC绘本, 绘本下载, 骑马钉PDF, booklet PDF.
  Supports single book download by ID, batch collection download, and automatic PDF generation.
---

# Epic Booklet Downloader

Download children's books from getepic.com and generate print-ready saddle-stitch booklet PDFs.

## Prerequisites

```bash
pip install Pillow requests
```

## Authentication (IMPORTANT)

Epic's API auth has changed. **Token-based auth is now the primary and most reliable method.** Email/password login may fail due to API changes.

### Token Auth (Recommended)

```bash
export EPIC_ACCESS_TOKEN=your_jwt_token
python scripts/epic_downloader.py --book-id 47110
```

**How to get a token:**
1. Open https://www.getepic.com/sign-in in your browser
2. Click "Students & Educators" → "Enter Educator Email"
3. Log in with your educator account
4. Open DevTools (F12) → Network tab
5. Find any request to `api-web.getepic.com`
6. Copy the token from the `Authorization` header (the part after `Bearer `)
7. Use it with `--token` or set `EPIC_ACCESS_TOKEN`

**Token lifetime:** ~24 hours. Re-login to refresh.

### Email/Password Auth (Fallback)

```bash
export EPIC_EMAIL=your@email.com
export EPIC_PASSWORD=yourpass
python scripts/epic_downloader.py --book-id 47110
```

⚠️ **Note:** Email/password auth tries 3 methods (noAuthlogin, newauth, WebAuth) but all may fail if Epic has changed their API. If login fails, use token auth.

### CLI Flags

```bash
python scripts/epic_downloader.py --token your_jwt --book-id 47110
python scripts/epic_downloader.py --email your@email.com --password yourpass --book-id 47110
```

## Usage

### Single Book
```bash
python scripts/epic_downloader.py --book-id 47110
```

### Multiple Books
```bash
python scripts/epic_downloader.py --book-ids 47110,47200,37798
```

### Entire Collection
```bash
python scripts/epic_downloader.py --collection 34822900
```

### Custom Output Directory
```bash
python scripts/epic_downloader.py --book-id 47110 --output ./my_books
```

## The reqSig Algorithm (for reference)

```python
import hashlib, json

EPIC_SALT = "#$%^&*(OIKJHBDE$R%^Y&UIOL"

def compute_reqsig(params: dict) -> str:
    keys = sorted(params.keys())
    sig_str = EPIC_SALT
    for k in keys:
        v = params[k]
        sig_str += k + (json.dumps(v) if isinstance(v, (dict, list)) else str(v))
    return hashlib.md5(sig_str.encode()).hexdigest()
```

## API Details

### Book Data Endpoint
```
GET https://api-web.getepic.com/webapi/index.php
  ?class=WebBook&method=getFullDataForWeb
  &bookId=<ID>&dev=web&isFreemium=0&needAssignmentType=0
  &timezoneOffsetMinutes=480&ver=3.5&reqSig=<SIG>
```

### Response Structure
```json
{
  "success": 1,
  "result": {
    "book": {"id": "47110", "title": "二月二的故事", "numPages": 23},
    "epub": {
      "spine": [
        {"pageCdn": "https://cdn-gcp-media-drm-v2.getepic.com/drm/0/47110/...jpg?Expires=...&Signature=..."}
      ]
    }
  }
}
```

### Login Endpoints (tried in order)
1. `WebAccount.noAuthlogin` — Primary (found in Angular source)
2. `newauth/auth/login` — Legacy
3. `WebAuth.login` — Legacy fallback (returns double-encoded JSON)

## Output Structure
```
epic_books/
├── 二月二的故事/
│   ├── pages/
│   │   ├── p001.jpg
│   │   ├── p002.jpg
│   │   └── ...
│   └── 二月二的故事.pdf
└── collection.json  (if downloading a collection)
```

## Print Instructions
1. Print double-sided (flip on short edge)
2. Fold in half along the spine
3. Staple at fold (2 staples)

## Pitfalls

- **Token is king**: Email/password auth is unreliable due to Epic API changes. Always prefer `--token`
- **Token expiry**: JWT tokens expire after ~24 hours. Re-login if API returns "Not Authed"
- **CDN URLs**: Page image URLs expire after ~24 hours. Re-run to refresh
- **Rate limiting**: Script includes 0.3s delay between books. Don't remove it
- **Double-encoded JSON**: The `WebAuth.login` endpoint returns a JSON string inside JSON. The script handles this automatically
- **Browser session**: Headless browser sessions expire quickly. Use token auth for CLI usage
- **Special chars in titles**: `/` in titles creates nested directories. Replaced with `_` or stripped

## Troubleshooting

### "All login methods failed"
→ Use token auth. Follow the instructions in the error message to get a token from browser DevTools.

### "Not Authed" on book download
→ Token expired. Get a fresh token from browser.

### No pages found
→ Book ID might be wrong, or the book requires a subscription your account doesn't have.

### PDF is blank
→ CDN URLs expired. Re-run the download.

## Repository

GitHub: https://github.com/irvinezhao/epic-booklet-downloader

- English: [README.md](https://github.com/irvinezhao/epic-booklet-downloader/blob/main/README.md)
- 中文: [README.zh-CN.md](https://github.com/irvinezhao/epic-booklet-downloader/blob/main/README.zh-CN.md)
