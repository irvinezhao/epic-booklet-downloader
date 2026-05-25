# 📚 EPIC绘本下载器

从 [getepic.com](https://www.getepic.com) 下载儿童绘本并生成可打印的骑马钉小册子PDF。

![Python](https://img.shields.io/badge/python-3.10+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
[![English](https://img.shields.io/badge/docs-English-blue)](README.md)

## ✨ 功能特性

- 🔐 通过 Epic API 自动登录认证
- 🖼️ 下载所有绘本页面为高清图片
- 📄 生成骑马钉小册子PDF（可直接打印）
- 📚 批量下载整个Collection
- 🔄 逆向工程的 `reqSig` 签名算法（MD5 + 盐值）
- 🖨️ 打印就绪格式：双面打印、对折、订书钉

## 🚀 快速开始

### 安装

```bash
git clone https://github.com/irvinezhao/epic-booklet-downloader.git
cd epic-booklet-downloader
pip install -r requirements.txt
```

### 设置账号

**推荐使用 Token 认证** — 更可靠，密码不会传给脚本。

```bash
export EPIC_ACCESS_TOKEN=your_jwt_token
```

**获取 Token 方式：**
1. 浏览器打开 https://www.getepic.com/sign-in
2. 点击 "Students & Educators" → "Enter Educator Email"
3. 用教育者账号登录
4. 打开 DevTools (F12) → Network 标签
5. 找到任意发往 `api-web.getepic.com` 的请求
6. 复制 `Authorization` header 中的 token（`Bearer ` 后面的部分）

也可以使用邮箱/密码（可能因 API 变更而失败）：

```bash
export EPIC_EMAIL=your@email.com
export EPIC_PASSWORD=***
```

或通过命令行参数直接传入：
```bash
--token your_epic_jwt
--email your@email.com --password yourpass
```

### 下载

```bash
# 单本下载
python scripts/epic_downloader.py --book-id 47110

# 多本下载
python scripts/epic_downloader.py --book-ids 47110,47200,37798

# 整个Collection下载
python scripts/epic_downloader.py --collection 34822900

# 自定义输出目录
python scripts/epic_downloader.py --book-id 47110 --output ./my_books
```

## 🖨️ 打印说明

1. **双面打印**（短边翻转）
2. **沿书脊对折**
3. **在折痕处装订**（2个订书钉）
4. 享受你的手工小册子！📖

## 🔧 工作原理

1. **认证**：通过 Epic 的认证 API 使用教育者/家长账号登录
2. **签名**：逆向工程 `reqSig` 参数（来自 Epic 前端 JS 的 MD5 + 盐值）
3. **元数据**：通过 `WebBook.getFullDataForWeb` API 获取书籍数据
4. **下载**：从 Epic CDN 下载所有页面图片（CDN无需认证）
5. **PDF**：生成正确页面顺序的骑马钉小册子PDF

### `reqSig` 签名算法

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

## 📁 输出结构

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
└── collection.json  （如果下载整个collection）
```

## 🤖 AI Agent 集成

本工具可作为各种AI Agent平台的技能/插件使用。将 `SKILL.md` 复制到Agent的技能目录，Agent即可在你提问时自动下载绘本。

### 支持平台

| 平台 | 技能目录 | 状态 |
|------|---------|------|
| [Hermes Agent](https://github.com/NousResearch/hermes-agent) | `~/.hermes/skills/` | ✅ 支持 |
| [OpenClaw](https://github.com/open-claw/open-claw) | `~/.openclaw/skills/` | ✅ 支持 |
| 任何支持Markdown技能的Agent | Agent技能配置目录 | ✅ 支持 |

### Hermes Agent

```bash
# 复制技能到Hermes技能目录
cp SKILL.md ~/.hermes/skills/epic-booklet.md

# 然后在Hermes聊天中：
"下载EPIC绘本 47110"
"下载这个collection: https://www.getepic.com/app/user-collection/34822900"
```

### OpenClaw

```bash
# 复制技能到OpenClaw技能目录
cp SKILL.md ~/.openclaw/skills/epic-booklet.md

# 然后在OpenClaw聊天中：
"下载EPIC绘本 47110"
"下载这个collection: https://www.getepic.com/app/user-collection/34822900"
```

### 自定义Agent

如果你的Agent支持加载Markdown文件作为技能/指令：

1. 将 `SKILL.md` 复制到Agent的技能目录
2. 确保Agent可以访问Python和所需依赖
3. Agent将根据技能中的说明执行下载命令

## ⚠️ 重要提示

- **需要账号**：你需要有效的 Epic 账号（教育者或家长）
- **速率限制**：脚本包含每本书0.3秒的延迟
- **CDN过期**：书籍页面URL在约24小时后过期（重新运行刷新）
- **仅限个人使用**：此工具仅供个人/教育用途

## 🛠️ 依赖要求

- Python 3.10+
- `Pillow` - 图像处理和PDF生成
- `requests` - HTTP客户端
- `playwright` - 浏览器自动化，用于可靠登录（自动降级）

```bash
pip install -r requirements.txt
playwright install chromium
```

## 🤝 贡献者

感谢所有贡献者！

<!-- ALL-CONTRIBUTORS-LIST-START -->
<table>
  <tr>
    <td align="center">
      <a href="https://github.com/irvinezhao">
        <img src="https://github.com/irvinezhao.png" width="80" style="border-radius:50%" alt="irvinezhao"/>
        <br />
        <sub><b>Irving Zhao</b></sub>
      </a>
      <br />
      <sub>创建者 & 维护者</sub>
    </td>
    <td align="center">
      <a href="https://github.com/KeaneYan">
        <img src="https://github.com/KeaneYan.png" width="80" style="border-radius:50%" alt="KeaneYan"/>
        <br />
        <sub><b>Keane Yan</b></sub>
      </a>
      <br />
      <sub>Token 认证 (#1)</sub>
    </td>
  </tr>
</table>
<!-- ALL-CONTRIBUTORS-LIST-END -->

### 如何贡献

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 📝 许可证

MIT License - 详见 [LICENSE](LICENSE)

## 🤝 贡献

欢迎贡献！请提交 Issue 或 PR。

## 📚 English Documentation

See [README.md](README.md)

## 📊 统计

<p align="center">
  <a href="https://github.com/irvinezhao/epic-booklet-downloader/stargazers"><img src="https://img.shields.io/github/stars/irvinezhao/epic-booklet-downloader?style=social&logo=github" alt="Stars"></a>
  <a href="https://github.com/irvinezhao/epic-booklet-downloader/network/members"><img src="https://img.shields.io/github/forks/irvinezhao/epic-booklet-downloader?style=social&logo=github" alt="Forks"></a>
  <a href="https://github.com/irvinezhao/epic-booklet-downloader/issues"><img src="https://img.shields.io/github/issues/irvinezhao/epic-booklet-downloader?style=social&logo=github" alt="Issues"></a>
  <a href="https://github.com/irvinezhao/epic-booklet-downloader/blob/main/LICENSE"><img src="https://img.shields.io/github/license/irvinezhao/epic-booklet-downloader?style=social&logo=github" alt="License"></a>
</p>
