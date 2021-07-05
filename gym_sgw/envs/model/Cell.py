from gym_sgw.envs.enums.Enums import MapObjects, Terrains


class Cell:

    def __init__(self, terrain: Terrains = Terrains.none):
        self.terrain = terrain
        self.objects = []

    def add_map_object(self, obj: MapObjects):
        self.objects.append(obj)

    def remove_map_object(self, obj: MapObjects):
        # If there's an error on the following line, the most likely error is due to the player
        # object being removed when trying to step forward and the player isn't really there.
        # What would you do to protect against this?
        self.objects.remove(obj)

    def get_data(self):
        meta_data = {
            'terrain': self.terrain.name,
            'terrain_key': str(self.terrain.value),
            'objects': [str(obj.name) for obj in self.objects],
            'object_keys': [str(obj.value) for obj in self.objects]
        }
        return meta_data
