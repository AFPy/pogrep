import contextlib
from io import StringIO
from pyfakefs import fake_filesystem_unittest
from pogrep import find_in_po

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

