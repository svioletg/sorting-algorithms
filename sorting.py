import sys
from argparse import ArgumentParser
from collections.abc import Callable
from time import perf_counter_ns
from typing import Protocol


class SupportsGreaterThan(Protocol):
    def __gt__(self, value, /) -> bool: ...

type SortFunc = Callable[[list[SupportsGreaterThan]], list[SupportsGreaterThan]]

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
    sorting_funcs_available: dict[str, Callable[[list[SupportsGreaterThan]], list]] = \
        {name.removeprefix('sort_'):obj for name, obj in globals().items() if name.startswith('sort_')}

    parser = ArgumentParser(description='Sorts the lines of a given file (or stdin), sending the sorted'
        + ' content to stdout and performance report to stderr.')
    parser.add_argument('algorithm', type=lambda s: s.split(','),
        help='Which sorting algorithm(s) to use. "ALL" runs every available algorithm and prints their results'
        + ' as each one finishes. If multiple algorithms are given, the sorted content is only printed for the'
        + ' first algorithm. Invalid choices are ignored. Available choices are:'
        + f' {', '.join(sorting_funcs_available.keys())}')
    parser.add_argument('to_sort', type=str,
        help='Path to a file to sort the lines of. Use a single hyphen to read from stdin.')
    parser.add_argument('--loops', '-n', type=int, default=1,
        help='How many times to perform the sort.')
    parser.add_argument('--quiet', '-q', action='store_true',
        help='Only outputs the performance results.')

    args = parser.parse_args()
    sorting_funcs: tuple[SortFunc, ...] = \
        tuple(sorting_funcs_available.values()) if args.algorithm == ['ALL'] else tuple(
        func for name, func in sorting_funcs_available.items() if name.removeprefix('sort_') in args.algorithm
    )
    content_stream = sys.stdin if args.to_sort == '-' else open(args.to_sort, encoding='utf-8')

    content: list[str] = [i.strip() for i in content_stream.readlines()]
    if content_stream is not sys.stdin:
        content_stream.close()

    run_count: int = args.loops
    if run_count < 1:
        print('Value to argument --loops/-n cannot be less than 1', file=sys.stderr)
        return 1

    quiet: bool = args.quiet

    # End argument parsing

    result_printed: bool = False

    for sort_func in sorting_funcs:
        runs: list[int] = []

        for _ in range(run_count):
            ta: int = perf_counter_ns()
            # Not really sure why ty raises an issue about this sort_func call but it works fine
            sorted_content: list[str] = sort_func(content.copy())  # ty:ignore[invalid-argument-type]
            tb: int = perf_counter_ns()
            runs.append(tb - ta)

        runs_avg: int = sum(runs) // len(runs)

        perf_report: str = f'{sort_func.__name__}: Sorted {len(content)} lines {runs_avg / 1e9:.8f}s ({runs_avg}ns)' \
            + f' averaged from {run_count} loop(s)'  # ty:ignore[unresolved-attribute]

        if (not quiet) and (not result_printed):
            print('\n'.join(sorted_content))
            result_printed = True
        print(perf_report, file=sys.stderr)

    return 0

if __name__ == '__main__':
    sys.exit(main())
