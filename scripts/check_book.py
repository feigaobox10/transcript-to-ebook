#!/usr/bin/env python3
"""python3 check_book.py chapters/ [--names names.tsv]  names.tsv 两列: 错误写法<TAB>正确写法。章标题识别"第 N 章"或"Chapter N"。"""
import glob, os, re, argparse
ap = argparse.ArgumentParser(); ap.add_argument("chapters"); ap.add_argument("--names"); a = ap.parse_args()
files = sorted(glob.glob(os.path.join(a.chapters, "*.md")))
if not files: ap.error("没有找到 Markdown 文件: " + a.chapters)
if a.names and not os.path.isfile(a.names): ap.error("找不到人名表: " + a.names)
allmd = "\n".join(open(f, encoding="utf-8").read() for f in files)
CH = r"^##\s*(?:第\s*(\d+)\s*章|Chapter\s*(\d+))"
chap_nums = set(int(x or y) for x, y in re.findall(CH, allmd, re.M | re.I)); bad = 0
def warn(m):
    global bad; bad += 1; print("  ! " + m)
if not chap_nums: warn("没有识别到章标题，请使用 ## 第 1 章 或 ## Chapter 1")
nums = [int(x or y) for x, y in re.findall(CH, allmd, re.M | re.I)]
for n in sorted(chap_nums):
    if nums.count(n) > 1: warn(f"章号重复: {n}")
for f in files:
    t = open(f, encoding="utf-8").read()
    for n in set(int(x or y) for x, y in re.findall(r"(?:第\s*(\d+)\s*章|Chapter\s*(\d+))", t, re.I)):
        if n not in chap_nums: warn(f"{os.path.basename(f)} 引用了不存在的 第 {n} 章")
    if not re.search(CH, t, re.M | re.I): continue
    if len(re.findall(CH, t, re.M | re.I)) > 1: warn("请每章一个文件")
    print(os.path.basename(f))
    for box, lo, hi in [("learn",1,1),("who",0,1),("summary",1,1),("quiz",1,1),("concept",1,9)]:
        n = len(re.findall(rf'class="box {box}"', t))
        if not lo <= n <= hi: warn(f"box.{box} 出现 {n} 次（期望 {lo}-{hi}）")
    lb = re.search(r'class="box learn".*?</(?:ul|ol)>', t, re.S)
    if lb and not 3 <= len(re.findall(r"<li>", lb.group(0))) <= 5: warn("learn 框要点数不在 3-5")
    qb = re.search(r'class="box quiz".*?</ol>', t, re.S)
    if qb and len(re.findall(r"<li>", qb.group(0))) != 3: warn("quiz 不是 3 题")
    if not re.search(r'<figure class="diagram"|class="fig"', t): print("  · 本章无图/大字数据块")
if a.names and os.path.exists(a.names):
    names_text = "\n".join(line for line in allmd.splitlines() if "<!-- names-check: ignore -->" not in line)
    for line in open(a.names, encoding="utf-8"):
        if "\t" in line:
            wrong, right = line.rstrip("\n").split("\t")[:2]
            if wrong and wrong in names_text: warn(f"残留错误写法 “{wrong}” → “{right}”")
gl = [f for f in files if "glossary" in f]
if gl:
    g = open(gl[0], encoding="utf-8").read()
    plain = re.sub(r"<[^>]+>", "", allmd)
    for zh, en in set(re.findall(r"核心概念[:：]\s*([^<（(]{2,20})[（(]([A-Za-z][^）)]{2,40})[）)]", plain)):
        if zh.strip() not in g and en.strip() not in g: warn(f"术语表未收录: {zh}（{en}）")
print("OK" if not bad else f"{bad} 个问题")
raise SystemExit(1 if bad else 0)
