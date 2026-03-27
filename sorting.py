from collections import UserList
import sys
from argparse import ArgumentParser
from collections.abc import Callable, Sequence
from time import perf_counter_ns
from typing import Protocol


type SortFunc = Callable[[list[Comparable]], list[Comparable]]

class Comparable(Protocol):
    def __gt__(self, value, /) -> bool: ...
    def __lt__(self, value, /) -> bool: ...

class TrackedList[T](UserList[T]):
    """
    Subclass of `UserList` that adds attributes for tracking how many times certain operations has been performed on
    the list.

    - `__getitem__` call increments `accesses`
    - `append` call increments `appends`
    - `insert` call increments `inserts`
    - `pop` call increments `pops`
    """
    def __init__(self, initlist: list[T] | None = None) -> None:
        super().__init__(initlist)

        self.accesses: int = 0
        self.appends: int = 0
        self.inserts: int = 0
        self.pops: int = 0

    def __repr__(self) -> str:
        return repr(self.data)

    def __getitem__(self, i):  # ty:ignore[invalid-method-override]
        self.accesses += 1
        return super().__getitem__(i)

    def asdict(self) -> dict[str, int]:
        return {name:getattr(self, name) for name in ('accesses', 'appends', 'inserts', 'pops')}

    def append(self, i):  # ty:ignore[invalid-method-override]
        self.appends += 1
        return super().append(i)

    def insert(self, n, to_pop):  # ty:ignore[invalid-method-override]
        self.inserts += 1
        return super().insert(n, to_pop)

    def pop(self, i = -1):  # ty:ignore[invalid-method-override]
        self.pops += 1
        return super().pop(i)

def sort_bubble[T: Comparable](to_sort: list[T]) -> list[T]:
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

def sort_selection[T: Comparable](to_sort: list[T]) -> list[T]:
    """Sorts a list with selection sort, consuming the input list and returning a reference to a new sorted list."""
    sorted_list: list[T] = []

    while to_sort:
        lowest: T = to_sort[0]
        for i in to_sort:
            if not lowest:
                lowest = i
                continue
            lowest = min(lowest, i)
        sorted_list.append(to_sort.pop(to_sort.index(lowest)))

    return sorted_list

def main(argv: Sequence[str] | None = None) -> int:
    sorting_funcs_available: dict[str, Callable[[list[Comparable]], list]] = \
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
    parser.add_argument('--tracked-list', '-t', action='store_true',
        help='Whether to track the accesses/appends/inserts/pops of the unsorted list and print the results.'
        + ' This results in a much slower operation, thus it being off by default.')
    parser.add_argument('--report', type=str, choices=('statement', 'csv'), default='statement',
        help='What format to give the time report of each sort in. "csv" will force the --quiet option.')
    parser.add_argument('--quiet', '-q', action='store_true',
        help='Only outputs the performance results.')

    args = parser.parse_args(argv)
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

    track_list_operations: bool = args.tracked_list
    report_format: str = args.report
    quiet: bool = args.quiet or (report_format == 'csv')

    # End argument parsing

    result_printed: bool = False

    if report_format == 'csv':
        print(
            'Function,Time Average,Time Average (ns),Lines Sorted,Loops,'
            + 'List Accesses,List Appends,List Inserts,List Pops',
            file=sys.stderr,
        )

    for sort_func in sorting_funcs:
        runs: list[int] = []

        for _ in range(run_count):
            unsorted = TrackedList(content.copy()) if track_list_operations else content.copy()
            ta: int = perf_counter_ns()
            # Not really sure why ty raises an issue about this sort_func call but it works fine
            sorted_content: list[str] = sort_func(unsorted)  # ty:ignore[invalid-argument-type]
            tb: int = perf_counter_ns()
            runs.append(tb - ta)

        runs_avg: int = sum(runs) // len(runs)

        perf_report: str = ''
        match report_format:
            case 'statement':
                perf_report = f'{sort_func.__name__}: Sorted {len(content)} lines {runs_avg / 1e9:.8f}s ({runs_avg}ns)' \
                    + f' averaged from {run_count} loop(s)'  # ty:ignore[unresolved-attribute]
                if isinstance(unsorted, TrackedList):
                    perf_report += f'\n    {unsorted.asdict()}'
            case 'csv':
                perf_report = f'{sort_func.__name__},{runs_avg / 1e9:.8f},{runs_avg},{len(content)},{run_count},'  # ty:ignore[unresolved-attribute]
                if isinstance(unsorted, TrackedList):
                    perf_report += f'{unsorted.accesses},{unsorted.appends},{unsorted.inserts},{unsorted.pops}'
                else:
                    perf_report += ',,,'
            case _:
                raise ValueError(f'Invalid performance report format: {report_format}')

        if (not quiet) and (not result_printed):
            print('\n'.join(sorted_content))
            result_printed = True
        print(perf_report, file=sys.stderr)

    return 0

if __name__ == '__main__':
    sys.exit(main())
