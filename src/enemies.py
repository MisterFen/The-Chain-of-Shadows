from npc import NPC, NPCTypes

class Enemy(NPC):
    """
    Enemy class that extends NPC. Represents enemy characters in the game,
    which attack the player, have health, and can be frozen, controlled, or paralyzed.
    """
    
    def __init__(self, pos, npc_info, game_manager, *groups):
        """
        Initializes the Enemy class.
        
        Args:
            pos (tuple): The (x, y) position of the enemy on the map.
            npc_info (dict): Dictionary containing information about the NPC (e.g., health, damage).
            game_manager (GameManager): Reference to the main game manager instance.
            groups (tuple): Sprite groups that the enemy belongs to (optional).
        """
        self.type = NPCTypes.ENEMY  # Defines this NPC's type as an enemy.
        super().__init__(pos, npc_info, game_manager, *groups)
        self.calculate_stats(game_manager.current_wave_number)  # Calculates stats based on the current wave.

    def calculate_stats(self, wave_number):
        """
        Adjusts the enemy's stats (health, damage) based on the current wave number.
        
        Args:
            wave_number (int): The current wave number in the game.
        """
        self.health = self.base_health + ((wave_number - 1) * 0.8)  # Health scales with wave number.
        self.damage = self.base_damage + (wave_number * 0.8)  # Damage also scales with the wave number.

    def update(self, dt):
        """
        Updates the enemy's state. Called every frame.
        
        Args:
            dt (float): Delta time since the last update.
        """
        super().update(dt)

    def attack(self):
        """
        Performs an attack on the target if the enemy is allowed to attack (cooldown, etc.).
        """
        if self.can_attack():
            print(f"Enemy attacks {self.target}!")
            if hasattr(self.target, 'take_damage'):
                self.target.take_damage(self.damage)  # Inflicts damage on the target if applicable.
            self.time_since_last_attack = 0  # Resets attack cooldown timer.

    def freeze(self, duration):
        """
        Freezes the enemy, preventing movement and actions for a specified duration.
        
        Args:
            duration (float): The length of time (in seconds) to freeze the enemy.
        """
        self.time_frozen = 0  # Timer to track how long the enemy has been frozen.
        self.frozen = True  # Sets the frozen state to True.
        self.freeze_duration = duration  # Duration for which the enemy will be frozen.
    
    def get_controlled(self, duration):
        """
        Puts the enemy under control (e.g., by a spell), preventing certain actions for a duration.
        
        Args:
            duration (float): The length of time (in seconds) the enemy will be controlled.
        """
        self.time_controlled = 0  # Timer to track the controlled duration.
        self.controlled = True  # Sets the controlled state to True.
        self.controlled_duration = duration  # Duration for which the enemy will be controlled.

    def get_paralyzed(self, duration):
        """
        Paralyzes the enemy, preventing movement and attacks for a specified duration.
        
        Args:
            duration (float): The length of time (in seconds) the enemy will be paralyzed.
        """
        self.time_paralyzed = 0  # Timer to track the paralyzed duration.
        self.paralyzed = True  # Sets the paralyzed state to True.
        self.paralyzed_duration = duration  # Duration for which the enemy will be paralyzed.

    def on_death(self):
        """
        Handles the logic for when the enemy dies.
        Increments defeated enemies, spawns loot, and removes the enemy from the game.
        """
        print("Enemy has died.")
        self.game_manager.enemies_defeated += 1  # Increments the count of defeated enemies in the game manager.
        self.game_manager.loot_manager.spawn_random_drop(self.drops, self.rect.center)  # Spawns loot at the enemy's location.
        self.kill()  # Removes the enemy from all sprite groups, effectively removing it from the game.

class CarnivorousPlantNPC(Enemy):
    """
    Special type of enemy NPC: Carnivorous Plant.
    Inherits all behavior and functionality from the Enemy class.
    """
    
    def __init__(self, pos, npc_info, game_manager, *groups):
        """
        Initializes the CarnivorousPlantNPC class.
        
        Args:
            pos (tuple): The (x, y) position of the plant on the map.
            npc_info (dict): Dictionary containing information about the plant NPC.
            game_manager (GameManager): Reference to the main game manager instance.
            groups (tuple): Sprite groups that the plant belongs to (optional).
        """
        super().__init__(pos, npc_info, game_manager, *groups)