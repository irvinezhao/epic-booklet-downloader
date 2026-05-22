---
name: epic-booklet
description: |
  Download children's books from getepic.com and generate print-ready saddle-stitch booklet PDFs.
  Use this skill whenever the user wants to download Epic books, create printable booklets from Epic,
  or mentions getepic.com book downloading. Also trigger on: EPIC绘本, 绘本下载, 骑马钉PDF, booklet PDF.
  Supports single book download by ID, batch collection download, and automatic PDF generation.
---

# Epic Booklet Downloader

A standalone Python tool for downloading EPIC children's books and generating printable saddle-stitch booklet PDFs.

**Repository**: https://github.com/irvinezhao/epic-booklet-downloader

## Quick Start

### 1. Install

```bash
git clone https://github.com/irvinezhao/epic-booklet-downloader.git
cd epic-booklet-downloader
pip install -r requirements.txt
```

### 2. Set Credentials

```bash
export EPIC_EMAIL=your@email.com
export EPIC_PASSWORD=yourpass
```

### 3. Download

```bash
# Single book
python scripts/epic_downloader.py --book-id 47110

# Multiple books
python scripts/epic_downloader.py --book-ids 47110,47200,37798

# Entire collection
python scripts/epic_downloader.py --collection 34822900
```

## CLI Options

```
--book-id ID          Download single book by ID
--book-ids ID,ID,...  Download multiple books (comma-separated)
--collection ID       Download entire collection
--output DIR          Output directory (default: ./epic_books)
--email EMAIL         Epic account email
--password PASS       Epic account password
```

## How It Works

1. **Login**: Authenticates via Epic's auth API (educator/parent account)
2. **Signature**: Computes `reqSig` using reverse-engineered MD5 + salt algorithm
3. **Fetch**: Gets book metadata via `WebBook.getFullDataForWeb` API
4. **Download**: Downloads all page images from CDN (no auth required)
5. **PDF**: Generates saddle-stitch booklet with proper page ordering

### The `reqSig` Algorithm

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
- **Browser-based auth**: If API login fails, provide a fresh JWT token from browser DevTools (Network tab → find any `api-web.getepic.com` request → copy Bearer token)

## Documentation

- English: [README.md](https://github.com/irvinezhao/epic-booklet-downloader/blob/main/README.md)
- 中文: [README.zh-CN.md](https://github.com/irvinezhao/epic-booklet-downloader/blob/main/README.zh-CN.md)
