This is a repository for storing my attempts at implementing certain sorting
algorithms in different languages, just for learning and practice. The main
rule I have for myself is every implementation must only rely on the standard
library for each language, however that's defined for that particular language.

There's one file or module per language that contains every algorithm as a
function. Running a language's respective file (by whatever means that language
uses) as a command should:

- Take lines of content to be sorted from the name of a file or stdin if `-` is used
- Allow specifying a number of times to repeat the sorting, timing each loop and
  averaging those times out to a final result
  - Should be `--loops`/`-n`
- Output the sorted lines to stdout
- Output the averaged time to stderr
