import pygame, sys
from src.settings import *
from src.debug import debug
from src.level import Level


class Game:
    def __init__ (self):
        
        #general setup
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH,HEIGHT))
        pygame.display.set_caption('PeenQis Yarn')
        self.clock = pygame.time.Clock()
        
        self.level = Level()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.screen.fill('black')
            debug('PeenQi')
            self.level.run()
            pygame.display.update()
            self.clock.tick(FPS)

if __name__ == '__main__':
    game = Game()
    game.run()                            
        