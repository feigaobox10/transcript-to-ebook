"""Regression coverage for data loss, false-success validation and book output."""
import importlib.util
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ToolsTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)

    def run_script(self, name, *args):
        return subprocess.run([sys.executable, str(ROOT / 'scripts' / name), *map(str, args)], capture_output=True, text=True)

    def sample(self):
        target = self.folder / 'chapters'
        shutil.copytree(ROOT / 'examples' / 'chapters', target)
        return target

    def test_subtitle_numbers_comments_tags_and_intentional_repetition(self):
        path = self.folder / 'sample.vtt'
        path.write_text('WEBVTT\n\nNOTE\nnot dialogue\n\ncue-id\n00:00.000 --> 00:01.000\n<c>2026 &amp; 2027</c>\n\n00:01.000 --> 00:02.000\n42\n\n00:02.000 --> 00:03.000\n42\n', encoding='utf-8')
        self.assertEqual(load('vtt_to_text').clean_vtt(path), '2026 & 2027 42 42')

    def test_overlapping_rolling_lines(self):
        path = self.folder / 'sample.vtt'
        path.write_text('WEBVTT\n\n00:00.000 --> 00:03.000\nFirst line\nSecond line\n\n00:02.000 --> 00:04.000\nSecond line\nThird line\n', encoding='utf-8')
        self.assertEqual(load('vtt_to_text').clean_vtt(path), 'First line Second line Third line')

    def test_dotted_names_and_distinct_variants_are_not_lost(self):
        src = self.folder / 'src'
        src.mkdir()
        cue = '1\n00:00:00,000 --> 00:00:01,000\n{}\n'
        for name, text in [('lecture.01.en.vtt', 'one'), ('lecture.01.en-orig.vtt', 'one'), ('lecture.02.srt', 'two'), ('lecture.01.fr.vtt', 'un')]:
            (src / name).write_text(cue.format(text), encoding='utf-8')
        out = self.folder / 'out'
        result = self.run_script('vtt_to_text.py', src, '-o', out)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(sorted(p.read_text().strip() for p in out.glob('*.txt')), ['one', 'two', 'un'])
        self.assertTrue((out / 'lecture.02.txt').is_file())

    def test_empty_and_invalid_subtitles_fail(self):
        self.assertNotEqual(self.run_script('vtt_to_text.py', self.folder, '-o', self.folder / 'out').returncode, 0)
        (self.folder / 'invalid.srt').write_text('not a subtitle')
        self.assertNotEqual(self.run_script('vtt_to_text.py', self.folder, '-o', self.folder / 'out').returncode, 0)

    def test_valid_example_passes(self):
        result = self.run_script('check_book.py', ROOT / 'examples' / 'chapters')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_empty_book_and_missing_names_fail(self):
        self.assertNotEqual(self.run_script('check_book.py', self.folder).returncode, 0)
        self.assertNotEqual(self.run_script('check_book.py', ROOT / 'examples' / 'chapters', '--names', self.folder / 'missing.tsv').returncode, 0)

    def test_missing_box_and_bad_learning_count_fail(self):
        for change in ['missing', 'count']:
            with self.subTest(change=change):
                target = self.folder / change
                shutil.copytree(ROOT / 'examples' / 'chapters', target)
                chapter = target / '11_bottleneck.md'
                text = chapter.read_text()
                if change == 'missing':
                    text = text.replace('class="box summary"', 'class="box note"')
                else:
                    text = re.sub(r'<ul>.*?</ul>', '<ul><li>one</li></ul>', text, count=1, flags=re.S)
                chapter.write_text(text)
                self.assertNotEqual(self.run_script('check_book.py', target).returncode, 0)

    def test_cross_reference_in_preface_is_checked(self):
        target = self.sample()
        (target / '01_preface.md').write_text('## 序言\n参见第 99 章。\n')
        result = self.run_script('check_book.py', target)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('99', result.stdout)

    def test_duplicate_chapter_numbers_fail(self):
        target = self.sample()
        shutil.copyfile(target / '11_bottleneck.md', target / '12_copy.md')
        self.assertNotEqual(self.run_script('check_book.py', target).returncode, 0)

    def test_names_ignore_is_limited_to_annotated_line(self):
        target = self.sample()
        names = self.folder / 'names.tsv'
        names.write_text('TypoName\tCorrectName\n')
        preface = target / '01_preface.md'
        preface.write_text('TypoName <!-- names-check: ignore -->\n')
        self.assertEqual(self.run_script('check_book.py', target, '--names', names).returncode, 0)
        preface.write_text(preface.read_text() + '\nTypoName\n')
        self.assertNotEqual(self.run_script('check_book.py', target, '--names', names).returncode, 0)

    def test_html_build_escapes_metadata_and_resolves_navigation(self):
        output = self.folder / 'nested folder' / 'book.html'
        result = self.run_script('build_book.py', ROOT / 'examples' / 'chapters', '-o', output, '--title', '<A&B>', '--lang', 'en" onload="bad')
        self.assertEqual(result.returncode, 0, result.stderr)
        doc = output.read_text()
        self.assertIn('&lt;A&amp;B&gt;', doc)
        self.assertNotIn('lang="en" onload=', doc)
        ids = re.findall(r'<h[123] id="([^"]+)"', doc)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(set(re.findall(r'href="#([^"]+)"', doc)) <= set(ids))
        self.assertIn('<svg ', doc)
        self.assertIn('class="box quiz"', doc)

    def test_missing_browser_fails_and_keeps_html(self):
        output = self.folder / 'book.html'
        result = self.run_script('build_book.py', ROOT / 'examples' / 'chapters', '-o', output, '--title', 'Book', '--pdf', '--chrome', self.folder / 'missing-browser')
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(output.is_file())
        self.assertFalse(output.with_suffix('.pdf').exists())

    def test_failed_pdf_render_keeps_previous_pdf(self):
        module = load('build_book')
        output = self.folder / 'book.html'
        pdf = output.with_suffix('.pdf')
        pdf.write_bytes(b'previous-pdf')
        from argparse import Namespace
        args = Namespace(chapters=str(ROOT / 'examples' / 'chapters'), output=str(output), title='Demo', subtitle='', sidebar_sub='', imprint='', imprint_sub='', cover_lines='', footer='', lang='zh-CN', pdf=True, chrome='fake')
        with mock.patch.object(module, 'find_browser', return_value='fake'), mock.patch.object(module.subprocess, 'run', return_value=None):
            with self.assertRaises(SystemExit): module.build(args)
        self.assertEqual(pdf.read_bytes(), b'previous-pdf')

    def test_inline_scripts_stay_in_sync(self):
        blocks = re.findall(r'```python\n(.*?)\n```', (ROOT / 'SKILL.md').read_text(), re.S)
        for name, block in zip(['vtt_to_text.py', 'build_book.py', 'check_book.py'], blocks):
            self.assertEqual(block.strip(), (ROOT / 'scripts' / name).read_text().strip(), name)
        self.assertEqual(len(blocks), 3)


if __name__ == '__main__':
    unittest.main()
