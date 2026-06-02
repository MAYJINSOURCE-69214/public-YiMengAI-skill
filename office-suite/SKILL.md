# Office 五件套技能

> 版本：v1.3.0（增强版 + PDF 支持 + 旧版 Word 兼容）
> 最后更新：2026-05-26 14:25
> 环境：Win11 + Python 3.14
> 参考：ha-docx 专业技能 + openclaw 技能结构

---

## 📖 功能说明

完整支持 Microsoft Office 五件套：**Word (.docx, .doc)**、**Excel (.xlsx)**、**PowerPoint (.pptx)**、**PDF (.pdf)**。

| 格式 | 读取 | 创建 | 编辑 | 信息 | 批注 | Markdown 导出 |
|------|------|------|------|------|------|-------------|
| **Word (.docx)** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Word (.doc)** | ✅ | ❌ | ❌ | ✅ |  | ❌ |
| **Excel (.xlsx)** | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| **PowerPoint (.pptx)** | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ |
| **PDF (.pdf)** | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ |
| **旧版 .xls** | ❌ |  | ❌ | ❌ | ❌ |  |

---

## 🛠️ 使用方法

### 自动触发（推荐）

**当你在对话中提到 `.docx`/`.doc`/`.xlsx`/`.pptx`/`.pdf` 文件路径或"读取这个 Word/Excel/PPT/PDF"时，我会立即执行以下流程：**

1. ✅ **直接使用 `run_shell_command` 调用技能命令**：
   ```bash
   python "C:\Users\ASUS\.qwen\skills\office-suite\skill.py" read "文件路径"
   ```
2. ❌ **绝不尝试**：
   - 用 `read_file` 读取（二进制文件会失败）
   - 用 Python 一行代码读取（路径空格容易出错）
   - 用 `glob` 查找文件（用户已给完整路径）
3. ✅ **直接输出结果**：读取成功后，立即总结内容并回复。

**示例**：
- 用户："@E:\MayJinSource\Application\忆梦 AI\AI 分享会.pptx 看看这个"
- AI：立即执行 `python skill.py read "E:\MayJinSource\Application\忆梦 AI\AI 分享会.pptx"` → 输出内容总结

### 手动调用

```bash
# 检查环境依赖
python skill.py check

# 读取文档
python skill.py read "C:\path\to\file.docx"
python skill.py read "C:\path\to\file.doc"
python skill.py read "C:\path\to\file.xlsx"
python skill.py read "C:\path\to\file.pptx"
python skill.py read "C:\path\to\file.pdf"

# 创建示例文档
python skill.py create "C:\Users\ASUS\Desktop\测试.docx"
python skill.py create "C:\Users\ASUS\Desktop\测试.xlsx"

# 文档信息
python skill.py info "C:\path\to\file.docx"
```

---

## 🎯 命令分类

### 读取类

| 命令 | 用途 | 支持格式 |
|------|------|---------|
| `read` | 读取文档内容（段落/表格/批注/页面） | .docx, .doc, .xlsx, .pptx, .pdf |
| `info` | 显示文档信息（段落数/表格数/页数） | .docx, .doc, .xlsx, .pptx, .pdf |

### 创建类

| 命令 | 用途 | 支持格式 |
|------|------|---------|
| `create` | 创建示例文档（含标题/段落/表格/列表） | .docx, .xlsx |

### 工具类

| 命令 | 用途 |
|------|------|
| `check` | 检查环境依赖（python-docx/openpyxl/python-pptx/pypdf/pywin32） |

---

## 🚀 v3.4 新增功能

| 功能 | 说明 | 来源 |
|------|------|------|
| **旧版 Word 读取** | 支持读取 `.doc` 格式（Word 97-2003），利用 Windows COM 自动转 `.docx` | pywin32 库 |
| **PDF 读取** | 支持读取文本型 PDF 内容（账单/合同/报表） | pypdf 库 |
| **PDF 元数据** | 可提取 PDF 的作者/标题/创建时间等元数据 | pypdf metadata |
| **PDF 限制** | 仅支持文本型 PDF，扫描件/图片型 PDF 无法提取文字 | 技术限制 |

---

## ⚠️ 注意事项

| 问题 | 说明 |
|------|------|
| **.doc 旧格式** | 支持读取，通过 COM 转为 .docx 后解析，需本地安装 Microsoft Word |
| **.docm 宏文件** | 宏代码无法执行 |
| **Excel 公式** | `data_only=True` 读取计算结果，不读取公式；创建公式后建议用 LibreOffice 重新计算验证 |
| **PPT 动画** | 无法读取/创建动画效果 |
| **PDF 扫描件** | 仅支持文本型 PDF，扫描件/图片型 PDF 无法提取文字，需 OCR 工具 |
| **修订跟踪** | python-docx 限制，无法精确跟踪修订。如需专业修订，建议安装 pandoc：`pandoc --track-changes=all input.docx -o output.md` |
| **样式保留** | 基础样式支持，复杂样式可能简化 |
| **Windows 编码** | CMD 中 emoji 可能显示为乱码，不影响实际功能 |
| **金融模型** | 如需创建金融模型，建议遵循行业标准：蓝色=输入，黑色=公式，绿色=内部链接，红色=外部链接，黄色=关键假设 |

---

## 🚀 高级功能（可选依赖）

### pandoc（Word 修订跟踪支持）

如果安装了 pandoc，可以读取带修订标记的 Word 文档：

```bash
# 安装 pandoc
# Windows: winget install pandoc
# macOS: brew install pandoc
# Linux: sudo apt-get install pandoc

# 读取带修订的文档
pandoc --track-changes=all input.docx -o output.md

# 接受所有修订
pandoc --track-changes=accept input.docx -o cleaned.md
```

### LibreOffice（Excel 公式重新计算）

如果安装了 LibreOffice，可以重新计算 Excel 公式：

```bash
# Windows: 安装 LibreOffice 后添加到 PATH
# 重新计算公式
soffice --headless --calc --convert-to xlsx input.xlsx
```

---

## 🔧 依赖安装

```bash
pip install python-docx openpyxl python-pptx pypdf pywin32
```

或者使用环境检查命令：

```bash
python skill.py check
```

---

## 📂 文件位置

- **技能目录**：`skills/office-suite/`
- **SKILL.md**：本文件
- **工具脚本**：`skill.py`
- **元数据**：`_meta.json`
