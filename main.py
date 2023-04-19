import pygame

from core.constants import *

from core import state_machine
import action
from platformer import editor


if __name__ == '__main__':
    game_engine = state_machine.Engine(RESOLUTION_X, RESOLUTION_Y)
    pygame.display.set_caption('Prehistoric Guy')
    #game_engine.push(action.GameState(game_engine))
    game_engine.push(editor.EditorState(game_engine))
    game_engine.run()
