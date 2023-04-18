from typing import TypeVar, Optional, List


def object_id_generator():
    n = 1
    while True:
        yield n
        n += 1


T = TypeVar('T')


class IdList(List[T]):
    """List of T elements, who are supposed to have a field `object_id: int` each."""
    def get_by_id(self, object_id: int) -> Optional[T]:
        """Returns the first element with the given object_id, or None."""
        iterator = filter(lambda obj: obj.object_id == object_id, self)
        try:
            return next(iterator)
        except StopIteration:
            return None
