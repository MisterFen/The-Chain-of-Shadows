import os
import pygame
from config.settings import SOUNDS_ROOT_PATH, VO_ROOT_PATH
from typing import Dict

class SoundManager:
    def __init__(self):
        """
        Initialize the SoundManager, setting up the mixer and sound storage.
        """
        pygame.mixer.init()
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.vo_lines: Dict[str, pygame.mixer.Sound] = {}
        self.running_vo_line = None
        self.load_all_sfx()
        self.set_music_volume(0.1)

    def load_all_sfx(self):
        for path, directories, files in os.walk(SOUNDS_ROOT_PATH):
            for file in files:
                file_to_load = os.path.normpath(os.path.join(path, file))
                sound_name_elements = file_to_load.removesuffix(".wav").split("\\")
                sound_name = sound_name_elements[-2] + "_" + sound_name_elements [-1]
                self.load_sound(sound_name, file_to_load, self.sounds)
                if "cast" in sound_name_elements:
                    self.set_sound_volume(sound_name, 0.2)

    def load_stage_vo_lines(self, stage_name):
        self.vo_lines = {}
        for path, directories, files in os.walk(VO_ROOT_PATH):
            for file in files:
                file_to_load = os.path.normpath(os.path.join(path, file))
                vo_line_file_elements = file_to_load.removesuffix(".wav").split("\\")
                vo_line_name = vo_line_file_elements[-1]
                vo_line_name_elements = vo_line_name.split("_")
                if vo_line_name_elements[0] == stage_name:
                    self.load_sound(vo_line_name, file_to_load, self.vo_lines)

    def load_sound(self, name: str, file_path: str, sounds_list: dict) -> None:
        """
        Load a sound effect from a file and store it with a name.

        :param name: The name to reference the sound.
        :param file_path: The path to the sound file (wav or mp3).
        """
        sound = pygame.mixer.Sound(file_path)
        sounds_list[name] = sound

    def play_vo_line(self, name: str, loops: int = 0) -> None:
        self.stop_vo()
        if name in self.vo_lines:
            self.vo_lines[name].play(loops=loops)
            self.running_vo_line = self.vo_lines[name]
        else:
            print(f"VO Line '{name}' not found!")

    def play_sound(self, name: str, loops: int = 0) -> None:
        """
        Play a loaded sound effect.

        :param name: The name of the sound to play.
        :param loops: The number of times to loop the sound. Default is 0 (no loop).
        """
        if name in self.sounds:
            self.sounds[name].play(loops=loops)
        else:
            print(f"Sound '{name}' not found!")

    def stop_sound(self, name: str) -> None:
        """
        Stop a sound effect that is currently playing.

        :param name: The name of the sound to stop.
        """
        if name in self.sounds:
            self.sounds[name].stop()
        else:
            print(f"Sound '{name}' not found!")

    def play_music(self, file_path: str, loops: int = -1, start: float = 0.0) -> None:
        """
        Play background music.

        :param file_path: The path to the music file (mp3 or ogg).
        :param loops: The number of times to loop the music. Default is -1 (infinite loop).
        :param start: The position to start the music from in seconds.
        """
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play(loops=loops, start=start)

    def stop_music(self) -> None:
        """
        Stop the currently playing background music.
        """
        pygame.mixer.music.stop()

    def switch_music(self, new_track_path) -> None:
        self.stop_music()
        self.play_music(new_track_path)

    def set_music_volume(self, volume: float) -> None:
        """
        Set the volume for the background music.

        :param volume: Volume level (0.0 to 1.0).
        """
        pygame.mixer.music.set_volume(volume)

    def stop_vo(self):
        if self.running_vo_line:
            self.running_vo_line.stop()

    def set_sound_volume(self, name: str, volume: float) -> None:
        """
        Set the volume for a specific sound effect.

        :param name: The name of the sound.
        :param volume: Volume level (0.0 to 1.0).
        """
        if name in self.sounds:
            self.sounds[name].set_volume(volume)
        else:
            print(f"Sound '{name}' not found!")
        
    def load_stage(self, stage):
        self.switch_music(stage.music_track_path)
        self.load_stage_vo_lines(stage.name.lower())