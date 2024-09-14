import encounters.forest_encounters as forest_encounters
import encounters.universal_encounters as universal_encounters

def get_stage_encounter_functions(stage_name):
    if stage_name == "Forest":
        return forest_encounter_functions
    if stage_name == "Library":
        return library_encounter_functions
    if stage_name == "Dungeon":
        return dungeon_encounter_functions
    if stage_name == "Fortress":
        return fortress_encounter_functions
    if stage_name == "Abyss":
        return abyss_encounter_functions

universal_encounter_functions = {
    "Temporal Rift": universal_encounters.temporal_rift,
}

forest_encounter_functions = {
    "Carnivorous Plants": forest_encounters.carnivorous_plants,
    "Fallen Stars": forest_encounters.fallen_stars
}

library_encounter_functions = {

}

dungeon_encounter_functions = {
    
}

fortress_encounter_functions = {
    
}

abyss_encounter_functions = {
    
}