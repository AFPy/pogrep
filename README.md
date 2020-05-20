# pogrep

Searches for string in po files. *popgrep* supports various *GNU grep* options
to ease its use.

# Examples

Print usage: `pogrep --help`

Find how 'flavors' has already been translated: search recursively in the
current directory, show the names of the matching files, excluding the venv
directory which contains a virtual env:

`pogrep --recursive --line-number --exclude-dir venv flavor `

Search the word 'typo' in traductions, but not in sources:

`pogrep --recursive --translation --no-source --word-regexp typo `
