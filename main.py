import sys
import pygame

from core import constants, state_machine
from platformer import editor, game


if __name__ == '__main__':
    game_engine = state_machine.Engine(constants.RESOLUTION_X, constants.RESOLUTION_Y)
    pygame.display.set_caption('Prehistoric Guy')

    if '--editor' not in sys.argv:
        game_engine.push(editor.EditorState(game_engine))
    else:
        game_engine.push(game.GameState(game_engine))

    game_engine.run()
