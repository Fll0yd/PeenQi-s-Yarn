import pygame
from pytmx.util_pygame import load_pygame

from src.settings import *
from src.tile import Tile
from src.player import Player


OBJECTS = {
    "Rock": "rock.png",
    "Tree": "tree.png",
    "Cave": "cave.png",
    "HoboRhodes": "hobo_rhodes.png",
    "DampSock": "damp_sock.png",
}


class Level:
    def __init__(self):
        self.inventory = {"damp_sock": False}
        self.display_surface = pygame.display.get_surface()

        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()

        self.transition_rects = []
        self.interaction_rects = []
        self.room_messages = []

        self.dialog_active = False
        self.dialog_text = ""
        self.transition_cooldown = 0

        self.current_map = "world.tmx"
        self.create_map(self.current_map, "PlayerSpawn")

    def scale_surface(self, surface):
        return pygame.transform.scale(
            surface,
            (
                surface.get_width() * MAP_SCALE,
                surface.get_height() * MAP_SCALE,
            ),
        )

    def scale_object_surface(self, surface, obj_name):
        if obj_name == "HoboRhodes":
            return pygame.transform.scale(surface, (48, 72))

        if obj_name == "DampSock":
            return pygame.transform.scale(surface, (72, 36))

        return self.scale_surface(surface)

    def scaled_rect(self, obj):
        return pygame.Rect(
            obj.x * MAP_SCALE,
            obj.y * MAP_SCALE,
            obj.width * MAP_SCALE,
            obj.height * MAP_SCALE,
        )

    def create_map(self, map_name, spawn_name="PlayerSpawn"):
        self.visible_sprites.empty()
        self.obstacle_sprites.empty()
        self.transition_rects = []
        self.interaction_rects = []
        self.room_messages = []

        tmx_data = load_pygame(MAPS_DIR / map_name)
        print(f"TMX Loaded: {map_name}")

        tile_count = 0

        for layer in tmx_data.visible_layers:
            if hasattr(layer, "data"):
                for x, y, gid in layer:
                    if gid == 0:
                        continue

                    surface = tmx_data.get_tile_image_by_gid(gid)

                    if surface is None:
                        continue

                    tile_count += 1
                    scaled_surface = self.scale_surface(surface)

                    groups = [self.visible_sprites]

                    if layer.name == "Objects":
                        groups.append(self.obstacle_sprites)

                    Tile(
                        (x * SCALED_TILESIZE, y * SCALED_TILESIZE),
                        groups,
                        "ground",
                        scaled_surface,
                    )

        print("Tiles loaded:", tile_count)

        for obj in tmx_data.objects:
            print("OBJECT:", obj.name, obj.properties)

            if obj.name == "RoomText":
                self.room_messages.append(
                    {
                        "pos": (obj.x * MAP_SCALE, obj.y * MAP_SCALE),
                        "message": obj.properties.get("message", ""),
                    }
                )

            if obj.name in OBJECTS:
                if obj.name == "DampSock" and self.inventory["damp_sock"]:
                    continue

                surface = pygame.image.load(
                    GRAPHICS_DIR / "test" / OBJECTS[obj.name]
                ).convert_alpha()

                scaled_surface = self.scale_object_surface(surface, obj.name)

                Tile(
                    (obj.x * MAP_SCALE, obj.y * MAP_SCALE),
                    [self.visible_sprites, self.obstacle_sprites],
                    "object",
                    scaled_surface,
                )

            if obj.name in ("CaveEntrance", "ExitCave"):
                target_map = obj.properties.get("target_map")
                target_spawn = obj.properties.get("target_spawn", "PlayerSpawn")

                if target_map and not target_map.endswith(".tmx"):
                    target_map += ".tmx"

                self.transition_rects.append(
                    {
                        "rect": self.scaled_rect(obj),
                        "target_map": target_map,
                        "target_spawn": target_spawn,
                    }
                )

            if obj.name in ("HoboRhodes", "DampSock", "Sign"):
                self.interaction_rects.append(
                    {
                        "rect": self.scaled_rect(obj),
                        "name": obj.name,
                        "item": obj.properties.get("item"),
                        "message": obj.properties.get("message", "..."),
                    }
                )

        self.player = None

        for obj in tmx_data.objects:
            if obj.name == spawn_name:
                self.player = Player(
                    (obj.x * MAP_SCALE, obj.y * MAP_SCALE),
                    [self.visible_sprites],
                    self.obstacle_sprites,
                )
                break

        if self.player is None:
            print(f"Spawn '{spawn_name}' not found. Using fallback spawn.")
            self.player = Player(
                (300, 300),
                [self.visible_sprites],
                self.obstacle_sprites,
            )

    def check_transitions(self):
        for transition in self.transition_rects:
            if self.player.hitbox.colliderect(transition["rect"]):
                target_map = transition["target_map"]
                target_spawn = transition["target_spawn"]

                print("Transition triggered:", target_map, target_spawn)

                if target_map:
                    self.current_map = target_map
                    self.dialog_active = False
                    self.dialog_text = ""
                    self.transition_cooldown = 30
                    self.create_map(self.current_map, target_spawn)
                    return

    def check_interactions(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_SPACE]:
            for interaction in self.interaction_rects:
                if self.player.hitbox.colliderect(interaction["rect"]):
                    item = interaction.get("item")

                    if item and not self.inventory.get(item, False):
                        self.inventory[item] = True
                        print("Inventory:", self.inventory)

                    self.dialog_active = True
                    self.dialog_text = interaction["message"]
                    return

        if keys[pygame.K_ESCAPE]:
            self.dialog_active = False
            self.dialog_text = ""

    def draw_room_messages(self):
        font = pygame.font.Font(None, 34)

        for message_obj in self.room_messages:
            message = message_obj["message"]
            x, y = message_obj["pos"]

            screen_pos = pygame.math.Vector2(x, y) - self.visible_sprites.offset

            text_surface = font.render(message, True, "white")
            text_rect = text_surface.get_rect(center=screen_pos)

            self.display_surface.blit(text_surface, text_rect)

    def draw_dialog(self):
        if not self.dialog_active:
            return

        box_rect = pygame.Rect(80, HEIGHT - 160, WIDTH - 160, 100)

        pygame.draw.rect(self.display_surface, "black", box_rect)
        pygame.draw.rect(self.display_surface, "white", box_rect, 3)

        font = pygame.font.Font(None, 32)
        text_surface = font.render(self.dialog_text, True, "white")
        text_rect = text_surface.get_rect(
            topleft=(box_rect.x + 20, box_rect.y + 25)
        )

        self.display_surface.blit(text_surface, text_rect)

    def run(self):
        self.visible_sprites.custom_draw(self.player)
        self.draw_room_messages()

        if not self.dialog_active:
            self.visible_sprites.update()

            if self.transition_cooldown > 0:
                self.transition_cooldown -= 1
            else:
                self.check_transitions()

        self.check_interactions()
        self.draw_dialog()


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

        for sprite in self.sprites():
            if sprite.sprite_type == "ground":
                offset_pos = sprite.rect.topleft - self.offset
                self.display_surface.blit(sprite.image, offset_pos)

        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            if sprite.sprite_type != "ground":
                offset_pos = sprite.rect.topleft - self.offset
                self.display_surface.blit(sprite.image, offset_pos)