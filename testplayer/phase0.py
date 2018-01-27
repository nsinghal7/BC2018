


def earth_karbonite_search(self):
    for row in range(self.start_map.height):
        for col in range(self.start_map.width):
            loc = bc.MapLocation(self.planet, row, col)
            self.
    return [[self.start_map.initial_karbonite_at(bc.MapLocation(self.planet, row, col)) for col in range(self.start_map.width)] for row in range(self.start_map.height)]