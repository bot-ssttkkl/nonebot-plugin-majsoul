from typing import TypeVar, Iterable, Tuple, Optional, Callable, Any

T = TypeVar("T")


def ranked(__iterable: Iterable[T],
           *, key: Optional[Callable[[T], Any]] = None,
           reverse: bool = False) -> Iterable[Tuple[int, T]]:
    if key is None:
        key = lambda x: x

    rank = 0
    prev = None
    for x in sorted(__iterable, key=key, reverse=reverse):
        if prev is None or key(x) != prev:
            rank += 1
        yield rank, x
