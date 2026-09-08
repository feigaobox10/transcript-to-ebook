# 最小可运行示例

`subtitles/` 是两段原创虚构的教学对话；`chapters/` 是将它们合并、解释并配图后的示例章节。数字、人物角色均用于演示，不来自第三方录音。

示例验证字幕清洗、章节核校、HTML 排版及可选 PDF 导出。三个脚本不会自动写出章节；从速记到书稿的写作由使用本 Skill 的 AI 助手与编辑完成。

在仓库根目录运行：

```sh
python3 -m pip install -r requirements.txt
python3 scripts/vtt_to_text.py examples/subtitles -o build/transcripts
python3 scripts/check_book.py examples/chapters
python3 scripts/build_book.py examples/chapters -o build/demo.html --title "一间小店的瓶颈" --subtitle "原创教学演示"
```

安装 Chrome/Chromium 后，在最后一条命令末尾加 `--pdf`，会同时生成 `build/demo.pdf`。也可以打开 HTML，使用浏览器的打印功能保存为 PDF。安装 Poppler 的 `pdftoppm` 后，脚本会另外生成封面 PNG。

完整图书的入门小课、章节地图、索引、来源表等请按照 SKILL.md 补齐；这个微型示例只演示最短可运行路径。
