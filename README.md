# pogrep

Searches for string in po files. *popgrep* supports various *GNU grep* options
to ease its use.

## Pogrep is part of poutils!

[Poutils](https://pypi.org/project/poutils) (`.po` utils) is a metapackage to easily install useful Python tools to use with po files
and `pogrep` is a part of it! Go check out [Poutils](https://pypi.org/project/poutils) to discover the other tools!

## Examples

Print usage: `pogrep --help`

Find how 'flavors' has already been translated: search recursively in the
current directory, show the names of the matching files, excluding the venv
directory which contains a virtual env:

`pogrep --recursive --line-number --exclude-dir venv flavor `

Search the word 'typo' in traductions, but not in sources:

`pogrep --recursive --translation --no-source --word-regexp typo `

Blame usage of 'allogène' in traductions:

`pogrep --recursive --ignore-case  --blame allogène `


## Contributing

Please test your contribution using `tox -p auto`.
