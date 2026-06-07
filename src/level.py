import pygame
from src.settings import *
from src.tile import Tile
from src.player import Player
from src.debug import debug

from pytmx.util_pygame import load_pygame

class Level:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()

        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()

        self.create_map()

    def create_map(self):
        tmx_data = load_pygame(MAPS_DIR / "world.tmx")

        print("TMX Loaded!")
        print(tmx_data)
        print("Map Size:", tmx_data.width, "x", tmx_data.height)

        for layer in tmx_data.visible_layers:
            if hasattr(layer, "data"):
                for x, y, gid in layer:
                    surface = tmx_data.get_tile_image_by_gid(gid)

                    if surface:
                        Tile(
                            (x * TILESIZE, y * TILESIZE),
                            [self.visible_sprites],
                            "ground",
                            surface,
                        )

        for obj in tmx_data.objects:
            if obj.name == "Player":
                print(f"Spawning Player at ({obj.x}, {obj.y})")

                self.player = Player(
                    (obj.x, obj.y),
                    [self.visible_sprites],
                    self.obstacle_sprites,
                )

                print("Player rect center:", self.player.rect.center)

    def run(self):
        self.visible_sprites.custom_draw(self.player)
        self.visible_sprites.update()


class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()

        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()

    def custom_draw(self, player):
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

        # draw ground first
        for sprite in self.sprites():
            if sprite.sprite_type == "ground":
                offset_pos = sprite.rect.topleft - self.offset
                self.display_surface.blit(sprite.image, offset_pos)

        # draw everything else with Y-sort
        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            if sprite.sprite_type != "ground":
                offset_pos = sprite.rect.topleft - self.offset
                self.display_surface.blit(sprite.image, offset_pos)