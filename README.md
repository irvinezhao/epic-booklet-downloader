# 📚 Epic Booklet Downloader

Download children's books from [getepic.com](https://www.getepic.com) and generate print-ready saddle-stitch booklet PDFs.

![Python](https://img.shields.io/badge/python-3.10+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## ✨ Features

- 🔐 Automatic authentication via Epic's API
- 🖼️ Download all book pages as high-quality images
- 📄 Generate saddle-stitch booklet PDFs (ready for printing)
- 📚 Batch download entire collections
- 🔄 Reverse-engineered `reqSig` algorithm (MD5 + salt)
- 🖨️ Print-ready format: double-sided, fold, staple

## 🚀 Quick Start

```bash
# Install dependencies
pip install Pillow requests

# Download a single book
python epic_downloader.py --book-id 47110 --email your@email.com --password yourpass

# Download a collection
python epic_downloader.py --collection 34822900 --email your@email.com --password yourpass

# Or use environment variables
export EPIC_EMAIL=your@email.com
export EPIC_PASSWORD=yourpass
python epic_downloader.py --book-id 47110
```

## 📖 Usage

### Single Book
```bash
python epic_downloader.py --book-id <BOOK_ID>
```

### Multiple Books
```bash
python epic_downloader.py --book-ids 47110,47200,37798
```

### Entire Collection
```bash
python epic_downloader.py --collection <COLLECTION_ID>
```

### Custom Output Directory
```bash
python epic_downloader.py --book-id 47110 --output ./my_books
```

## 🖨️ Printing Instructions

1. **Print double-sided** (flip on short edge)
2. **Fold in half** along the spine
3. **Staple** at the fold (2 staples)
4. Enjoy your handmade booklet! 📖

## 🔧 How It Works

1. **Authentication**: Logs in via Epic's new auth API with your educator/parent account
2. **Signature**: Reverse-engineers the `reqSig` parameter (MD5 + salt from Epic's frontend JS)
3. **Metadata**: Fetches book data via `WebBook.getFullDataForWeb` API
4. **Download**: Downloads all page images from Epic's CDN (no auth required for CDN)
5. **PDF**: Generates a saddle-stitch booklet PDF with proper page ordering

### The `reqSig` Algorithm

```python
# From Epic's main.*.js (reverse-engineered)
def compute_reqsig(params):
    keys = sorted(params.keys())
    sig_str = "#$%^&*(OIKJHBDE$R%^Y&UIOL"  # salt
    for k in keys:
        sig_str += k + str(params[k])
    return md5(sig_str.encode()).hexdigest()
```

## 📁 Output Structure

```
epic_books/
├── 二月二的故事/
│   ├── pages/
│   │   ├── p001.jpg
│   │   ├── p002.jpg
│   │   └── ...
│   └── 二月二的故事.pdf
├── 小红帽/
│   ├── pages/
│   └── 小红帽.pdf
└── collection.json  (if downloading a collection)
```

## ⚠️ Important Notes

- **Account Required**: You need a valid Epic account (educator or parent)
- **Rate Limiting**: The script includes a 0.3s delay between books
- **CDN Expiry**: Book page URLs expire after ~24 hours (re-run to refresh)
- **For Personal Use**: This tool is for personal/educational use only

## 🛠️ Requirements

- Python 3.10+
- `Pillow` - Image processing and PDF generation
- `requests` - HTTP client

```bash
pip install Pillow requests
```

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.

## 🤝 Contributing

Contributions welcome! Please open an issue or PR.

## ⭐ Star History

If you find this useful, please star the repo!
