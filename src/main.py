from game_manager import GameManager
import cProfile

if __name__ == "__main__":
    game = GameManager()
    cProfile.run('game.run()')