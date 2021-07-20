from gym_sgw.envs.model.Cell import Cell


class Pedestrian:

    def __init__(self):
        # create dictionary of all pedestrians based on location (location:hp)
        self.objects = {}
        self.hp = 5

    def add_ped(self, location=[]):
        self.objects[location] = self.hp

    # removes pedestrian object
    def remove_ped(self, location=[]):
        # will NOT remove if hp is still above 0
        if self.get_hp(location) > 0:
            pass
        else:
            del self.objects[location]

    # take away one hp from pedestrian object (to be called when location of ped is on fire terrain)
    def hurt(self, location=[]):
        self.objects[location] -= 1

    # returns pedestrian object's hp
    def get_hp(self, location=[]):
        return self.objects[location]

    # check if pedestrian exists at given location
    def exists(self, location=[]):
        return bool(location in self.objects)