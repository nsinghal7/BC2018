def generate_start_map(self):
    planet_map = self.gc.starting_map(self.planet)
    self.start_map = []
    for row in range(planet_map.height):
        map_row = []
        for col in range(planet_map.width):
            loc = bc.MapLocation(self.planet, row, col)
            map_row.append(planet_map.initial_karbonite_at(loc) if planet_map.is_passable_terrain_at(loc) else -1)
        self.start_map.append(map_row)


def earth_karbonite_search(self):
    