from ability import Ability, AbilityCollisionSprite
from movement_manager import MovementManager

class Mindshackle(Ability):
    def __init__(self, game_manager, ability_owner):
        self.debug_name = "mindshackle"
        self.ability_info = game_manager.ability_info[self.debug_name]
        super().__init__(self.ability_info, game_manager, ability_owner)

    def trigger(self):
        MindshackleBoltSprite(self, self.game_manager.all_ability_sprites)
        self.time_since_last_use = 0

class MindshackleBoltSprite(AbilityCollisionSprite):
    def __init__(self, ability, *groups):
        self.ability = ability
        super().__init__(ability, *groups)
        self.closest_enemy = self.game_manager.enemy_manager.get_closest_enemy()
        self.direction = MovementManager.calculate_direction((self.rect.center), (self.closest_enemy.rect.center))

    def update(self, dt):
        super().update(dt)
        
        # Continue moving in given direction
        if self.closest_enemy:
            self.rect.x, self.rect.y = MovementManager.move((self.rect.x, self.rect.y), self.ability.speed,  dt, direction=self.direction)

    def on_collision(self, target):
        super().on_collision(target)
        target.take_damage(self.ability.damage)
        target.get_controlled(self.ability.duration)