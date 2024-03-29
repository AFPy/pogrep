import pytest

try:
    from test.support.os_helper import change_cwd
except ImportError:
    from test.support import change_cwd
from pogrep import GrepColors, colorize, process_path, find_in_po

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


@pytest.fixture
def about_po(tmp_path):
    (tmp_path / "about.po").write_text(POText)
    with change_cwd(tmp_path):
        yield tmp_path


def test_in_source(about_po):
    errors, results = find_in_po("About", ("about.po",))
    assert not errors
    assert "about.po" in {result.file for result in results}


def test_not_in_source(about_po):
    errors, results = find_in_po("propos", ("about.po",))
    assert not errors
    assert not results


def test_in_translation(about_po):
    errors, results = find_in_po(
        "propos",
        ("about.po",),
        in_translation=True,
        not_in_source=True,
    )
    assert not errors
    assert "about.po" in {result.file for result in results}


def test_not_in_translation(about_po):
    errors, results = find_in_po(
        "About",
        ("about.po",),
        in_translation=True,
        not_in_source=True,
    )
    assert not errors
    assert not results


TEST_TEXT = """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad
minim veniam, quis nostrud exercitation ullamco laboris nisi ut
aliquip ex ea commodo consequat. Duis aute irure dolor in
reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla
pariatur.  Excepteur sint occaecat cupidatat non proident, sunt in
culpa qui officia deserunt mollit anim id est laborum."""
TEST_PREFIXES = [["25:", "glossary.po:"], ["42:", "consectetur:"], ["42:", ""]]


def test_pattern():
    grep_colors = GrepColors()
    grep_colors.get_from_env_variables("ms=99")
    assert "\33[99m\33[K" + "fugiat" + grep_colors.NO_COLOR in colorize(
        text=TEST_TEXT, pattern="fugiat", grep_colors=grep_colors, prefixes=[]
    )
    assert "\33[99m\33[K" not in colorize(
        text=TEST_TEXT, pattern="hello", grep_colors=grep_colors, prefixes=[]
    )


def test_prefixes():
    text = " 42:" + TEST_TEXT
    grep_colors = GrepColors()
    grep_colors.get_from_env_variables("ln=99:fn=88:ms=77")
    assert "\33[99m\33[K" + "42:" + grep_colors.NO_COLOR in colorize(
        text=text, pattern="fugiat", grep_colors=grep_colors, prefixes=TEST_PREFIXES
    )
    text = " consectetur:" + text[1:]
    result = colorize(
        text=text,
        pattern="consectetur",
        grep_colors=grep_colors,
        prefixes=TEST_PREFIXES,
    )
    assert (
        "\33[88m\33[K" + "consectetur:" + "\33[99m\33[K" + "42:" + grep_colors.NO_COLOR
        in result
    )
    assert "\33[77m\33[K" + "consectetur" + grep_colors.NO_COLOR in result


@pytest.fixture
def few_files(tmp_path):
    for file in (
        "file1.txt",
        "file2.txt",
        "first.po",
        "second.po",
        "library/lib1.po",
        "venv/file1.po",
    ):
        (tmp_path / file).parent.mkdir(exist_ok=True)
        (tmp_path / file).touch()
    with change_cwd(tmp_path):
        yield tmp_path


def test_directory_and_no_recursion(few_files):
    with pytest.raises(SystemExit) as excinfo:
        process_path(".", recursive=False)
    assert excinfo.value.code == 1


def test_no_file(few_files):
    with pytest.raises(SystemExit) as excinfo:
        process_path("non_exists_file.po", recursive=False)
    assert excinfo.value.code == 1


def test_list_of_files(few_files):
    assert set(process_path(["file1.txt", "file2.txt"], recursive=False)) == {
        "file1.txt",
        "file2.txt",
    }


def test_empty_and_recursive(few_files):
    assert set(process_path([], recursive=True)) == {
        "first.po",
        "second.po",
        "library/lib1.po",
        "venv/file1.po",
    }


def test_read_grep_colors_envvar():
    grep_colors = GrepColors()
    grep_colors.get_from_env_variables("ms=:ln=99:fn=88")
    assert grep_colors.start("fn") == "\33[88m\33[K"
    assert grep_colors.start("ln") == "\33[99m\33[K"
    assert grep_colors.start("ms") == "\33[99m\33[K"
