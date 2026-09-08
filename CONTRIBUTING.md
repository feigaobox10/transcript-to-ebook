# 参与改进

欢迎提交使用案例、勘误和修复。报告问题时，请说明输入类型、运行环境、执行步骤、实际结果和期望结果。只附可公开分享的最小样例。

修改写作方法时，说明它解决了哪一种实际失真，并保留来源归属、限制条件和用户指定范围。修改脚本时，请同时更新 `SKILL.md` 附录中的对应副本：两者一致，单文件安装才可用。

提交前运行：

```sh
python3 -m pip install -r requirements.txt
python3 -m unittest discover -s tests -v
python3 scripts/check_book.py examples/chapters
```

PDF 相关修改需另外生成 PDF，检查封面、章首、图表与分页。自动检查只能证明部分结构与工具行为，不能证明书稿事实准确。

贡献按本仓库许可证发布。第三方素材请保留来源及其原有许可，不要把未授权的课程字幕或个人资料加入仓库。
