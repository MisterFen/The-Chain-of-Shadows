from ability import Ability, AbilityCollisionSprite
from movement_manager import MovementManager

class PhoenixFlame(Ability):
    def __init__(self, game_manager, ability_owner):
        self.debug_name = "phoenix_flame"
        self.ability_info = game_manager.ability_info[self.debug_name]
        super().__init__(self.ability_info, game_manager, ability_owner)

    def trigger(self):
        self.queue_projectiles(self.projectiles)
        self.time_since_last_use = 0

    def spawn_projectile(self):
        PhoenixFlameSprite(self, self.game_manager.all_ability_sprites)

class PhoenixFlameSprite(AbilityCollisionSprite):
    def __init__(self, ability, *groups):
        self.ability = ability
        super().__init__(ability, *groups)

    def update(self, dt):
        super().update(dt)
        # Update the position based on the new angle
        # Use the MovementManager to update position
        center = self.game_manager.player.rect.center  # Player's center as the orbit center
        new_pos, self.angle = MovementManager.move_in_a_circle(center, self.ability.radius, self.angle, self.ability.speed/10, dt)
        self.rect.center = new_pos

    def on_collision(self, target):
        super().on_collision(target)
        target.take_damage(self.ability.damage)