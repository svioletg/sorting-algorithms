import sys
from argparse import ArgumentParser, FileType
from collections.abc import Callable
from pathlib import Path
from time import perf_counter_ns, sleep
from typing import Protocol

class SupportsGreaterThan(Protocol):
    def __gt__(self, other: object) -> bool: ...

def sort_bubble[T: SupportsGreaterThan](to_sort: list[T]) -> list[T]:
    """Sorts a list in-place with bubble sort, then returns a reference to the same list."""
    def _bubble() -> bool:
        """Perform one pass of bubble-sorting, then return whether any swaps were performed."""
        swapped: bool = False
        for n in range(sort_len := len(to_sort)):
            if n == sort_len - 1:
                break
            i, j = to_sort[n], to_sort[n + 1]
            if i > j:
                to_sort.insert(n, to_sort.pop(n + 1))
                swapped = True
        return swapped

    while _bubble():
        pass

    return to_sort

def main() -> int:
    parser = ArgumentParser(description='Sorts the lines of a given file (or stdin), sending the sorted'
        + ' content to stdout and performance report to stderr.')
    parser.add_argument('algorithm', type=str,
        choices=tuple(name.removeprefix('sort_') for name in globals() if name.startswith('sort_')),
        help='Which sorting algorithm to use.')
    parser.add_argument('to_sort', type=str,
        help='Path to a file to sort the lines of. Use a single hyphen to read from stdin.')
    parser.add_argument('--loops', '-n', type=int, default=1,
        help='How many times to perform the sort.')

    args = parser.parse_args()
    sort_func: Callable[[list[SupportsGreaterThan]], list] = globals()['sort_' + args.algorithm]
    content: list[str] = [
        i.strip()
        for i in (sys.stdin if args.to_sort == '-' else open(args.to_sort, encoding='utf-8')).readlines()
    ]
    run_count: int = args.loops

    if run_count < 1:
        print('Value to argument --loops/-n cannot be less than 1', file=sys.stderr)
        return 1

    # End argument parsing

    runs: list[int] = []

    for _ in range(run_count):
        ta: int = perf_counter_ns()
        sorted_content = sort_func(content.copy())
        tb: int = perf_counter_ns()
        runs.append(tb - ta)

    runs_avg: int = sum(runs) // len(runs)

    perf_report: str = f'{runs_avg / 1e9:.8f}s ({runs_avg}ns) averaged from {run_count} loop(s)'

    print('\n'.join(sorted_content))
    print(perf_report, file=sys.stderr)

    return 0

if __name__ == '__main__':
    sys.exit(main())
