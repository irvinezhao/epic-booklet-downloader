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

## How It Works

1. **Login**: Authenticates via Epic's new auth API (educator/parent account)
2. **reqSig**: Reverse-engineered MD5 + salt signature algorithm
3. **Fetch**: Gets book metadata via `WebBook.getFullDataForWeb` API
4. **Download**: Downloads all page images from CDN (no auth required)
5. **PDF**: Generates saddle-stitch booklet with proper page ordering

## Usage

### Single Book
```bash
python scripts/epic_downloader.py --book-id <BOOK_ID> --email <EMAIL> --password <PASSWORD>
```

### Multiple Books
```bash
python scripts/epic_downloader.py --book-ids 47110,47200,37798 --email <EMAIL> --password <PASSWORD>
```

### Entire Collection
```bash
python scripts/epic_downloader.py --collection <COLLECTION_ID> --email <EMAIL> --password <PASSWORD>
```

### Environment Variables (alternative)
```bash
export EPIC_EMAIL=your@email.com
export EPIC_PASSWORD=yourpass
python scripts/epic_downloader.py --book-id 47110
```

## The reqSig Algorithm (for reference)

```python
import hashlib

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

- **Token expiry**: JWT tokens expire after ~24 hours. Re-login if API returns "Not Authed"
- **CDN URLs**: Page image URLs expire after ~24 hours. Re-run to refresh
- **Rate limiting**: Script includes 0.3s delay between books. Don't remove it
- **Login endpoint**: Try `newauth.getepic.com` first, fall back to `WebAuth.login`
- **Browser-based auth**: If API login fails, the user may need to provide a fresh JWT token from their browser's DevTools (Network tab → find any `api-web.getepic.com` request → copy Bearer token from Authorization header)
