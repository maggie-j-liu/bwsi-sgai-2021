from gym_sgw.envs.model.Cell import Cell


class Pedestrian:

    def __init__(self):
        # create dictionary of all pedestrians based on location -- {location:hp}
        self.objects = {}
        self.hp = 5

    # create a new pedestrian in object dictionary
    def add_ped(self, x, y):
        location = (x, y)
        self.objects[location] = self.hp

    # removes pedestrian object
    def remove_ped(self, x, y):
        location = (x, y)
        # will NOT remove if hp is still above 0
        if bool(self.exists(location)):
            if self.get_hp(location=location) > 0:
                pass
            else:
                del self.objects[location]

    # take away one hp from pedestrian object (to be called when location of ped is on fire terrain)
    def hurt(self, x, y):
        location = (x, y)
        # check if pedestrian exists first
        if bool(self.exists(location)):
            self.objects[location] -= 1

    # returns a pedestrian's hp level
    def get_hp(self, location=()):
        if bool(self.exists(location)):
            return self.objects[location]

    # check if pedestrian exists at given location
    def exists(self, location=()):
        return bool(location in self.objects)

    # returns the number of pedestrians remaining
    def get_num_peds(self):
        return len(self.objects)
