#!/usr/bin/env python3
"""Clean VTT/SRT cues into text; never rewrite the original subtitles."""
import argparse
import csv
import html
import json
from pathlib import Path
import re

TIMING = re.compile(r"(?P<start>(?:\d+:)?\d{2}:\d{2}[.,]\d+)\s*-->\s*(?P<end>(?:\d+:)?\d{2}:\d{2}[.,]\d+)")


def seconds(value):
    total = 0.0
    for part in value.replace(',', '.').split(':'):
        total = total * 60 + float(part)
    return total


def read_cues(path):
    source = Path(path).read_text(encoding='utf-8-sig').replace('\r\n', '\n').replace('\r', '\n')
    for block in re.split(r'\n\s*\n', source):
        lines = block.strip().splitlines()
        if not lines or re.match(r'^(NOTE(?:\s|$)|STYLE$|REGION$)', lines[0]):
            continue
        for i, line in enumerate(lines):
            match = TIMING.search(line)
            if match:
                payload = lines[i + 1:]
                cleaned = [html.unescape(re.sub(r'<[^>]+>', '', s)).strip() for s in payload]
                cleaned = [re.sub(r'\s+', ' ', s) for s in cleaned if s]
                yield seconds(match['start']), seconds(match['end']), cleaned
                break


def clean_vtt(path):
    output, previous_lines, previous_end = [], [], -1
    for start, end, lines in read_cues(path):
        overlap = 0
        # Only remove repeated full lines from overlapping rolling cues.
        # Repetition in separate cues, numeric speech and partial words survive.
        if start < previous_end:
            for length in range(min(len(previous_lines), len(lines)), 0, -1):
                if previous_lines[-length:] == lines[:length]:
                    overlap = length
                    break
        output.extend(lines[overlap:])
        previous_lines, previous_end = lines, end
    return ' '.join(output)


def source_id(path):
    return re.sub(r'\.[a-z]{2,3}(?:-[A-Za-z]{2,4})?(?:-orig)?$', '', path.stem)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('src')
    parser.add_argument('-o', '--out', default='transcripts')
    args = parser.parse_args()
    files = sorted(p for p in Path(args.src).glob('*') if p.suffix.lower() in ('.vtt', '.srt'))
    if not files:
        parser.error('No .vtt/.srt files found: ' + args.src)
    prepared, seen_text, used_names = [], set(), set()
    for path in files:
        text = clean_vtt(path)
        if not text:
            parser.error('No readable subtitle cues: ' + str(path))
        base = source_id(path)
        fingerprint = (base, text)
        if fingerprint in seen_text:
            continue
        seen_text.add(fingerprint)
        # Distinct language/edited variants remain separate; dots are preserved.
        name = path.stem
        if name in used_names:
            name += '.' + path.suffix[1:]
        if name in used_names:
            parser.error('Output name collision: ' + name)
        used_names.add(name)
        meta = {}
        sidecar = path.with_name(base + '.info.json')
        if sidecar.is_file():
            try:
                meta = json.loads(sidecar.read_text(encoding='utf-8'))
                if not isinstance(meta, dict): raise ValueError('expected JSON object')
            except (ValueError, OSError) as exc:
                parser.error(f'Invalid metadata {sidecar}: {exc}')
        prepared.append((name, text, meta))
    destination = Path(args.out)
    destination.mkdir(parents=True, exist_ok=True)
    with (destination / 'manifest.tsv').open('w', encoding='utf-8', newline='') as handle:
        writer = csv.writer(handle, delimiter='\t')
        writer.writerow(['id', 'title', 'duration_s', 'upload_date', 'words'])
        for name, text, meta in prepared:
            (destination / (name + '.txt')).write_text(text + '\n', encoding='utf-8')
            writer.writerow([name, meta.get('title', ''), meta.get('duration', ''), meta.get('upload_date', ''), len(text.split())])
    print(f'{len(prepared)} transcripts -> {destination}/')


if __name__ == '__main__':
    main()
