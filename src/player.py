import pygame
from src.settings import *


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites, inventory):
        self.sprite_type = "player"
        super().__init__(groups)
        self.inventory = inventory
        self.status = "down"
        self.direction = pygame.math.Vector2()
        self.speed = 5
        self.obstacle_sprites = obstacle_sprites

        self.getting_item = False
        self.get_item_timer = 0

        self.animations = {
            "down": [
                self.load_player_image("down_walk2.png", (60, 79)),
                self.load_player_image("down_walk4.png", (60, 79)),
            ],
            "up": [
                self.load_player_image("up_walk2.png", (60, 79)),
                self.load_player_image("up_walk4.png", (60, 79)),
            ],
            "left": [
                self.load_player_image("left_idle.png", (60, 79)),
                self.load_player_image("left_walk1.png", (60, 79)),
                self.load_player_image("left_walk2.png", (60, 79)),
                self.load_player_image("left_walk3.png", (60, 79)),
                self.load_player_image("left_walk4.png", (60, 79)),
            ],
            "right": [
                self.load_player_image("right_idle.png", (60, 79)),
                self.load_player_image("right_walk1.png", (60, 79)),
                self.load_player_image("right_walk2.png", (60, 79)),
                self.load_player_image("right_walk3.png", (60, 79)),
                self.load_player_image("right_walk4.png", (60, 79)),
            ],
        }
        self.attacking = False
        self.attack_frame_index = 0
        self.attack_animation_speed = 0.35
        self.attack_direction = "down"
        self.attack_animations = {
            "right": [
                self.load_player_image("sock_attack1.png", (90, 90)),
                self.load_player_image("sock_attack2.png", (90, 90)),
                self.load_player_image("sock_attack3.png", (90, 90)),
                self.load_player_image("sock_attack4.png", (90, 90)),
                self.load_player_image("sock_attack5.png", (90, 90)),
                self.load_player_image("sock_attack6.png", (90, 90)),
            ],
            "left": [
                self.load_player_image("left_sock_attack1.png", (90, 90)),
                self.load_player_image("left_sock_attack2.png", (90, 90)),
                self.load_player_image("left_sock_attack3.png", (90, 90)),
                self.load_player_image("left_sock_attack4.png", (90, 90)),
                self.load_player_image("left_sock_attack5.png", (90, 90)),
                self.load_player_image("left_sock_attack6.png", (90, 90)),
            ],
            "up": [
                self.load_player_image("up_sock_attack1.png", (90, 90)),
                self.load_player_image("up_sock_attack2.png", (90, 90)),
                self.load_player_image("up_sock_attack3.png", (90, 90)),
                self.load_player_image("up_sock_attack4.png", (90, 90)),
                self.load_player_image("up_sock_attack5.png", (90, 90)),
            ],
            "down": [
                self.load_player_image("down_sock_attack1.png", (90, 90)),
                self.load_player_image("down_sock_attack2.png", (90, 90)),
                self.load_player_image("down_sock_attack3.png", (90, 90)),
                self.load_player_image("down_sock_attack4.png", (90, 90)),
            ],
        }

        self.get_item_image = self.load_player_image("get_item.png", (90, 119))

        self.frame_index = 0
        self.animation_speed = 0.15

        self.image = self.animations[self.status][0]
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(-20, -36)

    def load_player_image(self, filename, size):
        image = pygame.image.load(
            GRAPHICS_DIR / "test" / filename
        ).convert_alpha()

        return pygame.transform.scale(image, size)

    def start_get_item_pose(self):
        center = self.rect.center

        self.status = "up"
        self.getting_item = True
        self.get_item_timer = 120

        self.direction.x = 0
        self.direction.y = 0

        self.image = self.get_item_image
        self.rect = self.image.get_rect(center=center)
        self.hitbox = self.rect.inflate(-20, -36)

    def input(self):
        keys = pygame.key.get_pressed()

        self.direction.x = 0
        self.direction.y = 0

        if keys[pygame.K_w]:
            self.direction.y = -1
            self.status = "up"
        elif keys[pygame.K_s]:
            self.direction.y = 1
            self.status = "down"

        if keys[pygame.K_a]:
            self.direction.x = -1
            self.status = "left"
        elif keys[pygame.K_d]:
            self.direction.x = 1
            self.status = "right"

    def animate(self):
        if self.direction.magnitude() == 0:
            self.frame_index = 0
            self.image = self.animations[self.status][0]
            return

        self.frame_index += self.animation_speed

        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index = 0

        self.image = self.animations[self.status][int(self.frame_index)]

    def move(self, speed):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        self.hitbox.x += self.direction.x * speed
        self.collision("horizontal")

        self.hitbox.y += self.direction.y * speed
        self.collision("vertical")

        self.rect.center = self.hitbox.center

    def collision(self, direction):
        if direction == "horizontal":
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0:
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0:
                        self.hitbox.left = sprite.hitbox.right

        if direction == "vertical":
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0:
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0:
                        self.hitbox.top = sprite.hitbox.bottom

    def get_base_direction(self):
        if "up" in self.status:
            return "up"
        if "down" in self.status:
            return "down"
        if "left" in self.status:
            return "left"
        if "right" in self.status:
            return "right"

        return "down"

    def attack_input(self):
        mouse_buttons = pygame.mouse.get_pressed()

        if not self.inventory.get("damp_sock"):
            return

        if mouse_buttons[0] and not self.attacking:
            self.attacking = True
            self.attack_frame_index = 0
            self.attack_direction = self.get_base_direction()
            print("ATTACK DIR:", self.attack_direction)

    def animate_attack(self):
        frames = self.attack_animations.get(
            self.attack_direction,
            self.attack_animations["right"]
        )

        self.attack_frame_index += self.attack_animation_speed

        if self.attack_frame_index >= len(frames):
            center = self.rect.center

            self.attacking = False
            self.attack_frame_index = 0
            self.image = self.animations[self.status][0]
            self.rect = self.image.get_rect(center=center)
            self.hitbox = self.rect.inflate(-20, -36)
            return

        center = self.rect.center
        self.image = frames[int(self.attack_frame_index)]
        self.rect = self.image.get_rect(center=center)
        self.hitbox = self.rect.inflate(-20, -36)

    def get_attack_rect(self):

        if not self.attacking:
            return None

        if self.status == "right":
            return pygame.Rect(
                self.rect.right,
                self.rect.top,
                60,
                self.rect.height
            )

        elif self.status == "left":
            return pygame.Rect(
                self.rect.left - 60,
                self.rect.top,
                60,
                self.rect.height
            )

        elif self.status == "up":
            return pygame.Rect(
                self.rect.left,
                self.rect.top - 60,
                self.rect.width,
                60
            )

        elif self.status == "down":
            return pygame.Rect(
                self.rect.left,
                self.rect.bottom,
                self.rect.width,
                60
            )

        return None

    def update(self):
        if self.getting_item:
            self.get_item_timer -= 1
            self.image = self.get_item_image

            if self.get_item_timer <= 0:
                center = self.rect.center
                self.getting_item = False
                self.image = self.animations[self.status][0]
                self.rect = self.image.get_rect(center=center)
                self.hitbox = self.rect.inflate(-20, -36)

            return

        self.input()

        if self.attacking:
            self.animate_attack()
            return

        self.attack_input()
        self.move(self.speed)
        self.animate()