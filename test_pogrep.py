from unittest import TestCase
import contextlib
from io import StringIO
from pyfakefs import fake_filesystem_unittest
from pogrep import RED, GREEN, MAGENTA, colorize, NO_COLOR, process_path, find_in_po

POText = """        
msgid ""
msgstr ""
"Project-Id-Version: Python 3\n"
"POT-Creation-Date: 2017-04-02 22:11+0200\n"
"PO-Revision-Date: 2018-07-23 17:55+0200\n"
"Language: fr\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"

#: ../Doc/about.rst:3
msgid "About these documents"
msgstr "À propos de ces documents"

#: ../Doc/about.rst:6
msgid ""
"These documents are generated from `reStructuredText`_ sources by `Sphinx`_, "
"a document processor specifically written for the Python documentation."
msgstr ""
"Ces documents sont générés à partir de sources en `reStructuredText`_ par "
"`Sphinx`_, un analyseur de documents spécialement conçu pour la "
"documentation Python."
"""


class TestLateral(fake_filesystem_unittest.TestCase):
    def setUp(self) -> None:
        self.setUpPyfakefs()
        self.fs.create_file('about.po')
        with open('about.po', 'w') as f:
            f.write(POText)

    def testInSource(self):
        tmp_stdout = StringIO()
        pattern = 'About'
        with contextlib.redirect_stdout(tmp_stdout):
            find_in_po(pattern, ('about.po',),
                       linenum=False, file_match=True, no_messages=False)
        output = tmp_stdout.getvalue()
        self.assertIn("about.po", output, "Original text should contain " + pattern)

    def testNotInSource(self):
        tmp_stdout = StringIO()
        pattern = 'propos'
        with contextlib.redirect_stdout(tmp_stdout):
            find_in_po(pattern, ('about.po',),
                       linenum=False, file_match=True, no_messages=False)
        output = tmp_stdout.getvalue()
        self.assertTrue(len(output) == 0, "Original text should not contain " + pattern)

    def testInTranslation(self):
        tmp_stdout = StringIO()
        pattern = 'propos'
        with contextlib.redirect_stdout(tmp_stdout):
            find_in_po(pattern, ('about.po',),
                       linenum=False, file_match=True, no_messages=False, in_translation=True, not_in_source=True)
        output = tmp_stdout.getvalue()
        self.assertIn("about.po", output, "Translated text should contain " + pattern)

    def testNotInTranslation(self):
        tmp_stdout = StringIO()
        pattern = 'About'
        with contextlib.redirect_stdout(tmp_stdout):
            find_in_po(pattern, ('about.po',),
                       linenum=False, file_match=True, no_messages=False, in_translation=True, not_in_source=True)
        output = tmp_stdout.getvalue()
        self.assertTrue(len(output) == 0, "Translated text should not contain " + pattern)


class TestColorize(TestCase):
    def setUp(self) -> None:
        self.text = """Lorem ipsum dolor sit amet, consectetur adipiscing elit, 
        sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, 
        quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute 
        irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. 
        Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit 
        anim id est laborum."""
        self.prefixes = [['25:', 'glossary.po:'],
                         ['42:', 'consectetur:'],
                         ['42:', '']]

    def test_pattern(self):
        self.assertIn(RED + "fugiat" + NO_COLOR, colorize(text=self.text, pattern="fugiat", prefixes=[]))
        self.assertNotIn(RED, colorize(text=self.text, pattern="hello", prefixes=[]))

    def test_prefixes(self):
        self.text = " 42:" + self.text
        self.assertIn(GREEN + "42:" + NO_COLOR, colorize(text=self.text, pattern="fugiat", prefixes=self.prefixes))
        self.text = " consectetur:" + self.text[1:]
        result = colorize(text=self.text, pattern="consectetur", prefixes=self.prefixes)
        self.assertIn(MAGENTA + "consectetur:" + GREEN + "42:" + NO_COLOR, result)
        self.assertIn(RED + "consectetur" + NO_COLOR, result)


class TestProcessPath(fake_filesystem_unittest.TestCase):
    def setUp(self) -> None:
        self.setUpPyfakefs()
        self.fs.create_file('file1.txt')
        self.fs.create_file('file2.txt')
        self.fs.create_file('first.po')
        self.fs.create_file('second.po')
        self.fs.create_file('library/lib1.po')
        self.fs.create_file('venv/file1.po')

    def test_directory_and_no_recursion(self):
        with self.assertRaises(SystemExit) as cm:
            process_path('.', recursive=False, exclude_dir=None)
        self.assertEqual(cm.exception.code, 1)

    def test_no_file(self):
        with self.assertRaises(SystemExit) as cm:
            process_path('non_exists_file.po', recursive=False, exclude_dir=None)
        self.assertEqual(cm.exception.code, 1)

    def test_list_of_files(self):
        self.assertSequenceEqual(['file1.txt', 'file2.txt'],
                                 process_path(['file1.txt', 'file2.txt'], recursive=False, exclude_dir=None))

    def test_empty_and_recursive(self):
        self.assertSequenceEqual(['first.po', 'second.po', 'library/lib1.po', 'venv/file1.po'],
                                 process_path([], recursive=True, exclude_dir=None))

    def test_exclude_dir(self):
        self.assertSequenceEqual(['first.po', 'second.po', 'library/lib1.po'],
                                 process_path([], recursive=True, exclude_dir='venv'))
        self.assertSequenceEqual(['first.po', 'second.po', 'library/lib1.po'],
                                 process_path([], recursive=True, exclude_dir='venv/'))
        self.assertSequenceEqual(['first.po', 'second.po', 'library/lib1.po'],
                                 process_path([], recursive=True, exclude_dir='venv//'))
