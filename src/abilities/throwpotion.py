from ability import Ability, AbilityCollisionSprite
from movement_manager import MovementManager

class ThrowPotion(Ability):
    def __init__(self, game_manager, ability_owner):
        self.debug_name = "throw_potion"
        self.ability_info = game_manager.ability_info[self.debug_name]
        super().__init__(self.ability_info, game_manager, ability_owner)

    def trigger(self):
        self.queue_projectiles(self.projectiles)
        self.time_since_last_use = 0

    def spawn_projectile(self):
        ThrowPotionSprite(self, self.game_manager.all_ability_sprites)

class ThrowPotionSprite(AbilityCollisionSprite):
    def __init__(self, ability, *groups):
        self.ability = ability
        super().__init__(ability, *groups)
        self.triggers_on_collision = False
        self.start_pos = self.game_manager.player.get_pos()
        self.end_pos = MovementManager.get_random_position_on_circle(self.start_pos, self.ability.radius)
        self.t = 0.0
        self.control_point = MovementManager.calculate_control_point(self.start_pos, self.end_pos, self.ability.curve_height)
    
    def update(self, dt):
        super().update(dt)
        self.rect.x, self.rect.y = MovementManager.move_along_curve(self.start_pos , self.end_pos, self.control_point, self.t)
        self.t += self.ability.speed * dt

        if self.t >= 1: # End of curve
            self.on_impact()

    def on_impact(self):
        explosion_ability = PotionExplosionAbility(self.game_manager)
        explosion_ability.trigger(self.end_pos)
        self.kill()
        pass

    def on_collision(self, target):
        pass

class PotionExplosionAbility(Ability):
    def __init__(self, game_manager):
        self.debug_name = "potion_explosion"
        self.ability_info = game_manager.ability_info[self.debug_name]
        super().__init__(self.ability_info, game_manager, game_manager.player)

    def trigger(self, pos):
        explosion = PotionExplosionSprite(self, pos)
        self.game_manager.all_sprites.add(explosion)
        self.time_since_last_use = 0

class PotionExplosionSprite(AbilityCollisionSprite):
    def __init__(self, ability, pos):
        self.ability = ability
        super().__init__(ability)
        (self.rect.x, self.rect.y) = pos
    
    def on_collision(self, target):
        super().on_collision(target)
        target.take_damage(self.ability.damage)