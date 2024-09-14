from enum import Enum

class GameState(Enum):
    HOME_SCREEN = 1
    PLAYING = 2
    PAUSED = 3
    GAME_OVER = 4
    STAGE_SELECT = 5
    LEVEL_UP = 6
    NEW_GAME = 7
    CINEMATIC = 8
    CUTSCENE = 9
    BOSS_FIGHT = 10