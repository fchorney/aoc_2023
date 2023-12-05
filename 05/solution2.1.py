from pathlib import Path


input_file = Path("input")


class RangeMap(object):
    def __init__(self, destination: int, source: int, count: int):
        self.source = range(source, source + count)
        self.destination = range(destination, destination + count)

    def __str__(self):
        return (
            f"RangeMap<source={self.source.start}, "
            f"destination={self.destination.start}, "
            f"count={self.source.stop - self.source.start}>"
        )

    def __repr__(self):
        return str(self)


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


class Maps(object):
    def __init__(self, filepath):
        self.seeds = []
        self.seed_to_soil = []
        self.soil_to_fertilizer = []
        self.fertilizer_to_water = []
        self.water_to_light = []
        self.light_to_temperature = []
        self.temperature_to_humidity = []
        self.humidity_to_location = []

        self.seed_mem = {}

        current_map = None
        with input_file.open() as f:
            for line in map(str.strip, f.readlines()):
                if not line:
                    current_map = None

                if current_map is not None:
                    current_map.append(RangeMap(*list(map(int, line.split(" ")))))

                if line.startswith("seeds: "):
                    for source, count in chunks(
                        list(map(int, line.split("seeds: ")[1].split(" "))), 2
                    ):
                        self.seeds.append(range(source, source + count))
                    continue

                if line.startswith("seed-to-soil map"):
                    current_map = self.seed_to_soil
                    continue

                if line.startswith("soil-to-fertilizer map"):
                    current_map = self.soil_to_fertilizer
                    continue

                if line.startswith("fertilizer-to-water map"):
                    current_map = self.fertilizer_to_water
                    continue

                if line.startswith("water-to-light map"):
                    current_map = self.water_to_light
                    continue

                if line.startswith("light-to-temperature map"):
                    current_map = self.light_to_temperature
                    continue

                if line.startswith("temperature-to-humidity map"):
                    current_map = self.temperature_to_humidity
                    continue

                if line.startswith("humidity-to-location map"):
                    current_map = self.humidity_to_location
                    continue

    def _get_source(self, did: int, mapping: list):
        for r in mapping:
            if did in r.destination:
                return r.source[r.destination.index(did)]
        return did

    def find_lowest_location(self) -> int:
        # Find highest location value
        max_location = max(
            self.humidity_to_location, key=lambda x: x.destination.stop
        ).destination.stop

        # Work backwards from location 0 and go up
        for location in range(0, max_location + 1):
            seed = soil = fertilizer = water = light = temperature = humidity = -1

            humidity = self._get_source(location, self.humidity_to_location)
            temperature = self._get_source(humidity, self.temperature_to_humidity)
            light = self._get_source(temperature, self.light_to_temperature)
            water = self._get_source(light, self.water_to_light)
            fertilizer = self._get_source(water, self.fertilizer_to_water)
            soil = self._get_source(fertilizer, self.soil_to_fertilizer)
            seed = self._get_source(soil, self.seed_to_soil)

            for seed_range in self.seeds:
                if seed in seed_range:
                    print(
                        f"{seed} -> {soil} -> {fertilizer} -> {water} -> {light} -> "
                        f"{temperature} -> {humidity} -> {location}"
                    )
                    return seed

        return -1


maps = Maps(input_file)
lowest = maps.find_lowest_location()

# print(lowest)
