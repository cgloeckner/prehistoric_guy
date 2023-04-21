from typing import List

from platformer import physics


def update_actors(platform: physics.Platform, actors_list: List[physics.Actor]) -> None:
    """Move all actors with the platform who are located at it."""
    for actor in actors_list:
        if actor.on_platform == platform:
            actor.pos += platform.hover.delta
