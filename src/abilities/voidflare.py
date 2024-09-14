from ability import Ability, AbilityCollisionSprite
from enum import Enum
from movement_manager import MovementManager

class VoidFlareState(Enum):
    ZOOMING = 1
    RESTING = 2

class VoidFlare(Ability):
    def __init__(self, game_manager, ability_owner):
        self.debug_name = "voidflare"
        self.ability_info = game_manager.ability_info[self.debug_name]
        super().__init__(self.ability_info, game_manager, ability_owner)

    def trigger(self):
        self.queue_projectiles(self.projectiles)
        self.time_since_last_use = 0

    def spawn_projectile(self):
        VoidFlareSprite(self, self.game_manager.all_ability_sprites)

class VoidFlareSprite(AbilityCollisionSprite):
    def __init__(self, ability, *groups):
        self.ability = ability
        self.time_since_zoom = 0
        self.state = VoidFlareState.RESTING
        self.target_pos = None
        super().__init__(ability, *groups)

    def update(self, dt):
        super().update(dt)

        if self.state == VoidFlareState.RESTING:
            self.time_since_zoom += dt
            assert hasattr(self.ability, 'time_between_zooms'), f"Unable to find attribute TimeBetweenZooms for {self.ability.name}"
            if self.time_since_zoom > self.ability.time_between_zooms:
                self.state = VoidFlareState.ZOOMING
                self.target_pos = self.game_manager.enemy_manager.get_random_enemy().rect.center

        if self.state == VoidFlareState.ZOOMING:
            self.rect.x, self.rect.y = MovementManager.move((self.rect.x, self.rect.y), self.ability.speed, dt, target_pos=(self.target_pos[0], self.target_pos[1]))
            if abs(self.rect.x - self.target_pos[0]) <= 5 and abs(self.rect.y - self.target_pos[1]) <= 5:
                self.state = VoidFlareState.RESTING
                self.time_since_zoom = 0
        

    def on_collision(self, target):
        super().on_collision(target)
        target.take_damage(self.ability.damage)