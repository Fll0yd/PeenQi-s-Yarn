import pygame
import math
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

        self.inventory_open = False
        self.i_key_was_pressed = False

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

        self.item_get_sound = None
        sound_path = ASSETS_DIR / "audio" / "item_get.wav"

        if sound_path.exists():
            self.item_get_sound = pygame.mixer.Sound(sound_path)
            self.item_get_sound.set_volume(0.5)
            
        self.item_get_sock_image = pygame.image.load(
            GRAPHICS_DIR / "test" / "damp_sock.png"
        ).convert_alpha()

        self.item_get_sock_image = pygame.transform.scale(
            self.item_get_sock_image,
            (160, 80)
        )
        self.right_click_was_pressed = False

    def check_inventory_toggle(self):
        keys = pygame.key.get_pressed()
        i_pressed = keys[pygame.K_i]

        if i_pressed and not self.i_key_was_pressed:
            self.inventory_open = not self.inventory_open

        self.i_key_was_pressed = i_pressed
        
    def draw_inventory(self):
        if not self.inventory_open:
            return

        # Main inventory panel
        panel = pygame.Rect(160, 80, WIDTH - 320, HEIGHT - 160)
        pygame.draw.rect(self.display_surface, (12, 12, 18), panel)
        pygame.draw.rect(self.display_surface, "white", panel, 3)

        title_font = pygame.font.Font(None, 42)
        label_font = pygame.font.Font(None, 26)
        item_font = pygame.font.Font(None, 24)

        title = title_font.render("PEENQI'S POCKETS", True, "white")
        self.display_surface.blit(title, (panel.x + 25, panel.y + 20))

        # Item grid box
        grid_box = pygame.Rect(panel.x + 25, panel.y + 75, 420, 260)
        pygame.draw.rect(self.display_surface, (0, 0, 0), grid_box)
        pygame.draw.rect(self.display_surface, (80, 220, 120), grid_box, 3)

        grid_label = label_font.render("ITEMS", True, "white")
        self.display_surface.blit(grid_label, (grid_box.x + 10, grid_box.y - 28))

        # Equipment/status box
        equip_box = pygame.Rect(panel.x + 470, panel.y + 75, 260, 260)
        pygame.draw.rect(self.display_surface, (0, 0, 0), equip_box)
        pygame.draw.rect(self.display_surface, (230, 190, 80), equip_box, 3)

        equip_label = label_font.render("EQUIPPED", True, "white")
        self.display_surface.blit(equip_label, (equip_box.x + 10, equip_box.y - 28))

        # Draw item slots
        slot_size = 54
        padding = 16
        start_x = grid_box.x + 25
        start_y = grid_box.y + 25

        for row in range(3):
            for col in range(6):
                slot = pygame.Rect(
                    start_x + col * (slot_size + padding),
                    start_y + row * (slot_size + padding),
                    slot_size,
                    slot_size,
                )
                pygame.draw.rect(self.display_surface, (25, 25, 35), slot)
                pygame.draw.rect(self.display_surface, (120, 120, 140), slot, 2)

        # Damp Sock item icon
        selected_item_name = None
        selected_item_desc = "No item selected."

        if self.inventory.get("damp_sock"):
            sock_icon = pygame.transform.scale(self.item_get_sock_image, (60, 30))
            sock_rect = sock_icon.get_rect(center=(start_x + 27, start_y + 27))
            self.display_surface.blit(sock_icon, sock_rect)

            selected_item_name = "Damp Sock"
            selected_item_desc = "A suspiciously moist starter weapon."

            # Selection border around first slot
            selected_slot = pygame.Rect(start_x, start_y, slot_size, slot_size)
            pygame.draw.rect(self.display_surface, (255, 255, 120), selected_slot, 3)

        # Equipped weapon preview
        if self.inventory.get("damp_sock"):
            equipped_text = item_font.render("Weapon:", True, "white")
            weapon_text = item_font.render("Damp Sock", True, (220, 220, 220))

            self.display_surface.blit(equipped_text, (equip_box.x + 25, equip_box.y + 30))
            self.display_surface.blit(weapon_text, (equip_box.x + 25, equip_box.y + 60))

            big_sock = pygame.transform.scale(self.item_get_sock_image, (120, 60))
            big_sock_rect = big_sock.get_rect(center=(equip_box.centerx, equip_box.y + 145))
            self.display_surface.blit(big_sock, big_sock_rect)
        else:
            empty_text = item_font.render("No weapon equipped.", True, "gray")
            self.display_surface.blit(empty_text, (equip_box.x + 25, equip_box.y + 35))

        # Bottom description box
        desc_box = pygame.Rect(panel.x + 25, panel.y + 360, panel.width - 50, 90)
        pygame.draw.rect(self.display_surface, (0, 0, 0), desc_box)
        pygame.draw.rect(self.display_surface, "white", desc_box, 2)

        if selected_item_name:
            name_surface = label_font.render(selected_item_name, True, "white")
            desc_surface = item_font.render(selected_item_desc, True, "gray")

            self.display_surface.blit(name_surface, (desc_box.x + 20, desc_box.y + 15))
            self.display_surface.blit(desc_surface, (desc_box.x + 20, desc_box.y + 48))
        else:
            empty_surface = item_font.render("Nothing but pocket lint.", True, "gray")
            self.display_surface.blit(empty_surface, (desc_box.x + 20, desc_box.y + 30))

        # Footer hint
        hint = item_font.render("Press I to close", True, "gray")
        self.display_surface.blit(hint, (panel.right - 150, panel.bottom - 35))

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
            return pygame.transform.scale(surface, (60, 76))

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

                sprite = Tile(
                    (obj.x * MAP_SCALE, obj.y * MAP_SCALE),
                    [self.visible_sprites, self.obstacle_sprites],
                    "object",
                    scaled_surface,
                )

                sprite.name = obj.name

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
                    self.inventory,
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
        mouse_buttons = pygame.mouse.get_pressed()

        right_click_pressed = mouse_buttons[2]

        if right_click_pressed and not self.right_click_was_pressed:

            if self.dialog_active:
                self.dialog_active = False
                self.dialog_text = ""
                self.right_click_was_pressed = True
                return

            for interaction in self.interaction_rects[:]:
                if self.player.hitbox.colliderect(interaction["rect"]):

                    if interaction["name"] == "DampSock":
                        if self.inventory["damp_sock"]:
                            return

                        self.inventory["damp_sock"] = True
                        print("Inventory:", self.inventory)

                        self.player.start_get_item_pose()

                        if self.item_get_sound:
                            self.item_get_sound.play()

                        for sprite in self.visible_sprites:
                            if getattr(sprite, "name", None) == "DampSock":
                                sprite.kill()

                        self.interaction_rects.remove(interaction)

                        self.dialog_active = True
                        self.dialog_text = "You got a Damp Sock!"
                        self.right_click_was_pressed = True
                        return

                    self.dialog_active = True
                    self.dialog_text = interaction["message"]
                    self.right_click_was_pressed = True
                    return

        self.right_click_was_pressed = right_click_pressed

        if keys[pygame.K_ESCAPE]:
            self.dialog_active = False
            self.dialog_text = ""

    def draw_item_get_overlay(self):
        if not self.player.getting_item:
            return

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.display_surface.blit(overlay, (0, 0))

        player_screen_pos = pygame.math.Vector2(
            self.player.rect.centerx,
            self.player.rect.top
        ) - self.visible_sprites.offset

        beam_center_x = int(player_screen_pos.x)
        beam_top_y = int(player_screen_pos.y - 90)
        beam_bottom_y = int(player_screen_pos.y + 20)

        beam_points = [
            (beam_center_x - 35, beam_top_y),
            (beam_center_x + 35, beam_top_y),
            (beam_center_x + 14, beam_bottom_y),
            (beam_center_x - 14, beam_bottom_y),
        ]

        beam_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.polygon(
            beam_surface,
            (255, 240, 120, 90),
            beam_points,
        )
        self.display_surface.blit(beam_surface, (0, 0))

        y_offset = math.sin(pygame.time.get_ticks() * 0.01) * 5

        sock_rect = self.item_get_sock_image.get_rect(
            center=(beam_center_x, beam_top_y + 25 + y_offset)
        )

        self.display_surface.blit(self.item_get_sock_image, sock_rect)

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

        attack_rect = self.player.get_attack_rect()

        if attack_rect:
            pygame.draw.rect(
                self.display_surface,
                (255, 0, 0),
                attack_rect,
                2
            )
            
        self.draw_item_get_overlay()
        self.draw_room_messages()

        self.check_inventory_toggle()

        if self.inventory_open:
            self.draw_inventory()
            return
        if self.dialog_active:
            self.check_interactions()
            self.draw_dialog()
            return

        self.visible_sprites.update()

        if self.transition_cooldown > 0:
            self.transition_cooldown -= 1
        else:
            self.check_transitions()

        self.check_interactions()

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