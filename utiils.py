from typing import Callable, Iterable, TypeVar, Optional

T = TypeVar("T")

def find(predicate: Callable[[T], bool], iterable: Iterable[T]) -> Optional[T]:
    """
    Returns the first element in iterable that matches the predicate.
    If no match is found, returns None.
    """
    return next((item for item in iterable if predicate(item)), None)