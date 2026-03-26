from itertools import cycle
from collections.abc import Iterable, Sequence, Callable
import string
import sys
from argparse import ArgumentParser

CHARSET_CHOICES: dict[str, str] = {
    'lower': ''.join(reversed(string.ascii_lowercase)),
    'upper': ''.join(reversed(string.ascii_uppercase)),
    'letters': ''.join(reversed(string.ascii_letters)),
    'alphanum': ''.join(reversed('0123456789' + string.ascii_uppercase + string.ascii_lowercase)),
}

def tabulate(
        data: Iterable[tuple[object, object]],
        *,
        sep: str = ' | ',
        strfunc: Callable[[object], str] = str,
    ) -> str:
    """Takes an iterable of two-tuples and returns the data formatted into a table-like string."""
    strung: tuple[tuple[str, str], ...] = tuple((strfunc(k), strfunc(v)) for k, v in data)
    longest_key: int = max(len(k) for k, _ in strung)
    return '\n'.join(f'{k:<{longest_key}}{sep}{v}' for k, v in strung)

def main(argv: Sequence[str] | None = None) -> int:
    parser = ArgumentParser(description='Generates lines of unsorted data based on the given options, printing those'
        + ' lines to stdout.')
    parser.add_argument('charset', type=str, choices=CHARSET_CHOICES.keys(),
        help='The set of characters to cycle through while generating lines.')
    parser.add_argument('lines', type=int,
        help='How many lines to generate.')
    parser.add_argument('--line-length', type=int, default=1,
        help='How many characters long each line should be.')

    args = parser.parse_args(argv)
    charset: str = CHARSET_CHOICES[args.charset]
    line_count: int = args.lines
    line_length: int = args.line_length

    for n, char in enumerate(cycle(charset)):
        if n >= line_count:
            break
        print(char * line_length)

    return 0

if __name__ == '__main__':
    sys.exit(main())
