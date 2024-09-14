from ability import Ability, AbilityCollisionSprite
from movement_manager import MovementManager

class WebWrap(Ability):
    def __init__(self, game_manager, ability_owner):
        self.debug_name = "web_wrap"
        self.ability_info = game_manager.ability_info[self.debug_name]
        super().__init__(self.ability_info, game_manager, ability_owner)

    def trigger(self):
        self.queue_projectiles(self.projectiles)
        self.time_since_last_use = 0

    def spawn_projectile(self):
        WebWrapSprite(self, self.game_manager.all_ability_sprites)

class WebWrapSprite(AbilityCollisionSprite):
    def __init__(self, ability, *groups):
        self.ability = ability
        super().__init__(ability, *groups)
        self.targets = "player"
        self.target = self.game_manager.player
        self.direction = MovementManager.calculate_direction((self.rect.center), (self.target.rect.center))

    def update(self, dt):
        super().update(dt)
        
        # Continue moving in given direction
        if self.target:
            self.rect.x, self.rect.y = MovementManager.move((self.rect.x, self.rect.y), self.ability.speed,  dt, direction=self.direction)

    def on_collision(self, target):
        super().on_collision(target)
        target.get_paralyzed(self.ability.wrap_duration)