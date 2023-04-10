from dataclasses import dataclass
from typing import Optional


NO_ACTION: int = 0
ATTACK_ACTION: int = 1
THROW_ACTION: int = 2


@dataclass
class Actor:
    object_id: int

    hit_points: int = 5
    max_hit_points: int = hit_points
    num_axes: int = 5
    max_num_axes: int = num_axes


class Characters(object):
    def __init__(self):
        self.characters = list()

    def get_by_id(self, object_id: int) -> Actor:
        """Returns the actor who matches the given object_id.
        May throw an IndexError.
        """
        return [a for a in self.characters if a.object_id == object_id][0]

    def try_get_by_id(self, object_id: int) -> Optional[Actor]:
        """Returns the actor who matches the given object_id or None
        """
        try:
            return self.get_by_id(object_id)
        except IndexError:
            return None
