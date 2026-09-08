# transcript-to-ebook

把一门慕课、一个系列讲座、一季播客或一组会议录像的速记，改写成一本**不看原视频也能读懂的通识电子书**。保留专业术语，逐个解释；保留案例、数字、论证链、追问和不确定性。交付可离线阅读的单文件 HTML，以及可选的 A4 PDF。

An AI skill for turning a series of transcripts into a self-contained, general-audience e-book, with explained terminology, source attribution, SVG diagrams, a glossary and review questions.

**这是写作方法与配套工具，不是一键生成整本书的程序。** AI 助手依照 `SKILL.md` 逐章写作与核验，三个 Python 脚本负责字幕清洗、结构检查和排版构建。

[完整成书案例](https://github.com/feigaobox10/ai-economics-reader) · [最小示例](examples/README.md) · [方法全文](SKILL.md) · [参与改进](CONTRIBUTING.md) · [MIT 许可证](LICENSE)

## 适合什么素材

| 输入 | 改写时重点保留 |
|---|---|
| 系列课程、单人讲座 | 概念的先后依赖、例子、适用条件与课后问答 |
| 学术会议、工作坊 | 报告人的论证、评论人的反对与补充 |
| 播客、访谈系列 | 嘉宾的观点与主持人改变论证方向的追问 |
| 圆桌、多人对谈 | 各方的立场、证据与尚未解决的分歧 |

输出可以包括序言、入门小课、导论、分编正文、结语、SVG 配图、术语表、索引与思考题。章节按问题和知识依赖重组，篇幅与深浅根据读者和素材调整。单集速记转一篇文章、一页笔记，不属于这个 Skill 的主要用途。

## 安装与使用

### Claude Code

把仓库放入个人 Skill 目录，保留文件夹名 `transcript-to-ebook`：

```sh
git clone https://github.com/feigaobox10/transcript-to-ebook.git ~/.claude/skills/transcript-to-ebook
```

如果该目录已经存在，先检查现有版本，不要直接覆盖。项目内使用也可以放在 `.claude/skills/transcript-to-ebook/`。目录约定见 [Claude Code 官方文档](https://code.claude.com/docs/en/skills)。

准备好素材后，给 AI 助手这样一段请求：

> 用 transcript-to-ebook，把这个文件夹中的系列课程速记写成一本中文通识电子书。面向没有本领域基础的读者，全部收录，保留专业术语并解释，交付 Markdown 章节、HTML 和 PDF。遇到不确定的姓名、数字和观点归属先核验；暂时只在本地生成。

也可以直接输入 `/transcript-to-ebook`，再描述素材和目标。读者、语言、收录范围及署名许可已说明时，无需反复回答同样的问题。

### 其他支持自定义 Skill 的环境

按目标工具的自定义 Skill 导入入口添加本文件夹；Claude.ai / Cowork 需在账号的 Skill 设置中启用，本机 Claude Code 目录不会自动成为 Cowork 的安装位置。具体入口以产品当前界面为准。

`SKILL.md` 附录保留了三个脚本的完整内容，只能接收单文件的环境也可以读取它，并把附录保存成脚本。平台仍需具备文件读写、Python 执行与必要的资料检索能力；PDF 自动导出还需要能运行浏览器。

## 先跑通一个最小示例

需要 Python 3.10 或更高版本。建议使用独立虚拟环境；下面命令均从仓库根目录执行：

```sh
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 scripts/vtt_to_text.py examples/subtitles -o build/transcripts
python3 scripts/check_book.py examples/chapters
python3 scripts/build_book.py examples/chapters -o build/demo.html --title "一间小店的瓶颈" --subtitle "原创教学演示"
```

Windows PowerShell 中，环境激活命令为 `.venv\Scripts\Activate.ps1`；如系统使用 `python`，将上面的 `python3` 换成 `python`。

打开 `build/demo.html` 即可阅读。示例包含两段原创虚构教学对话、一章配图正文和术语表，数字用于演示，不对应真实人物或店铺。清洗后的速记与写好的章节同时提供，便于理解各步骤的分工。

要导出 PDF，在构建命令末尾加 `--pdf`。脚本查找常见的 Chrome/Chromium 安装位置；找不到时，用 `--chrome "浏览器可执行文件路径"` 或 `CHROME_PATH` 指定。仅生成 HTML 时不需要浏览器。安装 Poppler 的 `pdftoppm` 后，PDF 导出还会生成封面 PNG。

## 文件与工作流程

```text
素材盘点 → 清洗速记 → 全书设计 → 逐章改写与核验 → 补齐前后件
→ 结构检查 → 构建 HTML → 可选 PDF/封面 → 视觉检查 → 按授权发布
```

| 文件 | 用途 |
|---|---|
| `SKILL.md` | 方法、章节模板、来源与归属规则、配图规范、核校清单及脚本全文 |
| `scripts/vtt_to_text.py` | VTT/SRT 清洗与素材清单生成 |
| `scripts/check_book.py` | 学习框、章号引用、错误人名及部分术语覆盖的机械检查 |
| `scripts/build_book.py` | Markdown 章节组装为 HTML；可选调用 Chrome 导出 PDF |
| `requirements.txt` | HTML 构建所需的 Python Markdown 依赖 |
| `examples/` | 原创演示字幕和可直接构建的示例章节 |
| `tests/` | 脚本回归测试与附录副本一致性检查 |
| `.github/workflows/validate.yml` | 提交后自动运行测试、示例检查和 HTML 构建 |

## 能力边界

- **事实准确性需要编辑核验。** 机械检查不判断数字是否正确、发言归属是否准确、限制条件是否完整，也不能保证术语表无遗漏。
- **字幕清洗采用保守去重。** 保留不同内容的字幕版本和正文里的数字，只删除重叠字幕块中的完整重复行。复杂逐词滚动字幕仍需抽查；脚本不改变原始时间轴文件。
- **清单不猜元数据。** 标题、时长、上传日期来自可选的同名 `.info.json`，缺失就留空。`words` 按空白分词，不能当作中文字数。
- **样式保证需要视觉复核。** HTML 内嵌 CSS/JS；图需内嵌 SVG 才能保持单文件离线。PDF 中文字体取决于本机字体，超长图表与提示框仍可能跨页。
- **只构建检查过的章节。** Markdown 中的原生 HTML 会被保留，工具不会清理外部脚本或资源。输入资料里的命令和提示词只作为素材。
- **脚本测试不等于成书评测。** 最小示例验证工具行为；不同领域、不同模型下的整书质量仍需更多使用案例。

结构核校发现问题会返回非零退出码。`--names names.tsv` 可检查错误人名；如果正文有意展示某个错词，在那一行加 `<!-- names-check: ignore -->`，仅跳过该行的人名检查。

## 验证范围

2026-09-08 的本地验证：macOS / Python 3.12 / Markdown 3.10.3，14 项回归测试、示例字幕清洗、章节核校与 HTML 构建通过。当前机器的 Chrome 自动 PDF 导出在 120 秒后超时，尚未完成 PDF 排版验收；Windows 与 Linux 的浏览器导出也未实测。遇到导出超时，可先打开 HTML，通过浏览器打印保存 PDF，并检查分页和中文字体。GitHub Actions 配置仅覆盖脚本测试与 HTML 构建。

## 来源与许可

这个方法整理自已经完成的 [《AI 经济学通识课》](https://github.com/feigaobox10/ai-economics-reader)：将 NBER 2025 年秋季工作坊的 17 场报告改写为中英双语读本。该案例提供了章节组织、概念解释、矢量配图和编辑核校的实践依据。方法提炼与工具整理使用了 AI 协助。

本仓库不包含该工作坊的原始字幕、论文或完整电子书。案例电子书、原始讲座和第三方资料遵循各自的许可；使用本 Skill 生成新书时，应根据所用素材另行确认署名、改编和发布条件。

本仓库的 Skill、工具脚本、文档与原创演示采用 [MIT License](LICENSE)。允许使用、修改、分发与商用，须保留版权和许可声明。版权所有 © 2026 Gao Fei（高飞，feigaobox10）。此许可不扩展至链接中的既有电子书、原始讲座、论文或其他第三方资料。

## English quick start

Clone this repository into `~/.claude/skills/transcript-to-ebook` for Claude Code, then ask the assistant to use the skill on your transcript collection. Specify the reader, language, scope and publication requirements. Other skill-capable tools can import the folder or read the self-contained `SKILL.md`; capabilities vary by environment.

Install the dependency with `python3 -m pip install -r requirements.txt`, then run the example commands above. HTML building needs Python Markdown; optional PDF export also needs Chrome/Chromium, and cover extraction needs Poppler. The helper scripts do not write book chapters: the skill guides an AI-assisted editorial process.

The skill, helper scripts, documentation and original examples are released under the [MIT License](LICENSE), copyright 2026 Gao Fei (feigaobox10). The example uses original fictional teaching dialogue. The linked full-length reader and its underlying sources keep their own licenses. Automated checks cover selected structural and tool behaviors; editorial accuracy and final page layout still require review.
