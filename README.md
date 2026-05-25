# 📚 Epic Booklet Downloader

Download children's books from [getepic.com](https://www.getepic.com) and generate print-ready saddle-stitch booklet PDFs.

![Python](https://img.shields.io/badge/python-3.10+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
[![中文文档](https://img.shields.io/badge/文档-中文-blue)](README.zh-CN.md)

## ✨ Features

- 🔐 Automatic authentication via Epic's API
- 🖼️ Download all book pages as high-quality images
- 📄 Generate saddle-stitch booklet PDFs (ready for printing)
- 📚 Batch download entire collections
- 🔄 Reverse-engineered `reqSig` algorithm (MD5 + salt)
- 🖨️ Print-ready format: double-sided, fold, staple

## 🚀 Quick Start

### Install

```bash
git clone https://github.com/irvinezhao/epic-booklet-downloader.git
cd epic-booklet-downloader
pip install -r requirements.txt
```

### Authentication

**Token-based auth is recommended** — more reliable and your password never touches the script.

```bash
export EPIC_ACCESS_TOKEN=your_jwt_token
```

**How to get a token:**
1. Open https://www.getepic.com/sign-in in your browser
2. Click "Students & Educators" → "Enter Educator Email"
3. Log in with your educator account
4. Open DevTools (F12) → Network tab
5. Find any request to `api-web.getepic.com`
6. Copy the token from the `Authorization` header (after `Bearer `)

Alternatively, use email/password (may not work due to API changes):

```bash
export EPIC_EMAIL=your@email.com
export EPIC_PASSWORD=***
```

Or pass credentials directly via CLI flags:
```bash
--token your_epic_jwt
--email your@email.com --password yourpass
```

### Download

```bash
# Single book
python scripts/epic_downloader.py --book-id 47110

# Multiple books
python scripts/epic_downloader.py --book-ids 47110,47200,37798

# Entire collection
python scripts/epic_downloader.py --collection 34822900

# Custom output directory
python scripts/epic_downloader.py --book-id 47110 --output ./my_books
```

## 🖨️ Printing Instructions

1. **Print double-sided** (flip on short edge)
2. **Fold in half** along the spine
3. **Staple** at the fold (2 staples)
4. Enjoy your handmade booklet! 📖

## 🔧 How It Works

1. **Authentication**: Logs in via Epic's auth API with your educator/parent account
2. **Signature**: Reverse-engineers the `reqSig` parameter (MD5 + salt from Epic's frontend JS)
3. **Metadata**: Fetches book data via `WebBook.getFullDataForWeb` API
4. **Download**: Downloads all page images from Epic's CDN (no auth required for CDN)
5. **PDF**: Generates a saddle-stitch booklet PDF with proper page ordering

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

## 🤖 AI Agent Integration

This tool can be used as a skill/plugin for various AI agent platforms. Copy `SKILL.md` to your agent's skill directory and the agent can automatically download books when you ask.

### Supported Platforms

| Platform | Skill Directory | Status |
|----------|----------------|--------|
| [Hermes Agent](https://github.com/NousResearch/hermes-agent) | `~/.hermes/skills/` | ✅ Supported |
| [OpenClaw](https://github.com/open-claw/open-claw) | `~/.openclaw/skills/` | ✅ Supported |
| Any agent supporting markdown skills | Agent's skill config | ✅ Supported |

### Hermes Agent

```bash
# Copy skill to Hermes skills directory
cp SKILL.md ~/.hermes/skills/epic-booklet.md

# Then in Hermes chat:
"Download EPIC book 47110"
"Download this collection: https://www.getepic.com/app/user-collection/34822900"
```

### OpenClaw

```bash
# Copy skill to OpenClaw skills directory
cp SKILL.md ~/.openclaw/skills/epic-booklet.md

# Then in OpenClaw chat:
"Download EPIC book 47110"
"Download this collection: https://www.getepic.com/app/user-collection/34822900"
```

### Custom Agent

If your agent supports loading markdown files as skills/instructions:

1. Copy `SKILL.md` to your agent's skill directory
2. Ensure the agent has access to Python and the required dependencies
3. The agent will use the skill's instructions to run the download commands

## ⚠️ Important Notes

- **Account Required**: You need a valid Epic account (educator or parent)
- **Rate Limiting**: The script includes a 0.3s delay between books
- **CDN Expiry**: Book page URLs expire after ~24 hours (re-run to refresh)
- **For Personal Use**: This tool is for personal/educational use only

## 🛠️ Requirements

- Python 3.10+
- `Pillow` - Image processing and PDF generation
- `requests` - HTTP client
- `playwright` - Browser automation for reliable login (auto-fallback)

```bash
pip install -r requirements.txt
playwright install chromium
```

## 🤝 Contributors

Thanks to all the people who have contributed!

<!-- ALL-CONTRIBUTORS-LIST-START -->
<!-- Add your profile here: https://allcontributors.org/docs/en/basics/add-to-project -->
<table>
  <tr>
    <td align="center">
      <a href="https://github.com/irvinezhao">
        <img src="https://github.com/irvinezhao.png" width="80" style="border-radius:50%" alt="irvinezhao"/>
        <br />
        <sub><b>Irving Zhao</b></sub>
      </a>
      <br />
      <sub>Creator & Maintainer</sub>
    </td>
    <td align="center">
      <a href="https://github.com/KeaneYan">
        <img src="https://github.com/KeaneYan.png" width="80" style="border-radius:50%" alt="KeaneYan"/>
        <br />
        <sub><b>Keane Yan</b></sub>
      </a>
      <br />
      <sub>Token Auth (#1)</sub>
    </td>
  </tr>
</table>
<!-- ALL-CONTRIBUTORS-LIST-END -->

### How to Contribute

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.

## 🤝 Contributing

Contributions welcome! Please open an issue or PR.

## 📚 中文文档

请查看 [README.zh-CN.md](README.zh-CN.md)

## ⭐ Star History

<p align="center">
  <a href="https://www.star-history.com/?type=date&repos=irvinezhao%2Fepic-booklet-downloader">
    <img src="https://api.star-history.com/svg?repos=irvinezhao/epic-booklet-downloader&type=Date" width="600" />
  </a>
</p>

[![GitHub Stars](https://img.shields.io/github/stars/irvinezhao/epic-booklet-downloader?style=social)](https://github.com/irvinezhao/epic-booklet-downloader)
