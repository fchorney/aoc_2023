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

        current_map = None
        with input_file.open() as f:
            for line in map(str.strip, f.readlines()):
                if not line:
                    current_map = None

                if current_map is not None:
                    current_map.append(RangeMap(*list(map(int, line.split(" ")))))

                if line.startswith("seeds: "):
                    self.seeds = list(map(int, line.split("seeds: ")[1].split(" ")))
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

    def _get_mapping(self, sid: int, mapping: list) -> int:
        for r in mapping:
            if sid in r.source:
                return r.destination[r.source.index(sid)]
        return sid

    def find_lowest_location(self) -> int:
        lowest_location = None
        for seed in self.seeds:
            # Find Soil
            soil = self._get_mapping(seed, self.seed_to_soil)
            # print(f"Seed to Soil: {seed} -> {soil}")

            fertilizer = self._get_mapping(soil, self.soil_to_fertilizer)
            # print(f"Soil to Fertilizer: {soil} -> {fertilizer}")

            water = self._get_mapping(fertilizer, self.fertilizer_to_water)
            # print(f"Fertilizer to Water: {fertilizer} -> {water}")

            light = self._get_mapping(water, self.water_to_light)
            # print(f"Water to Light: {water} -> {light}")

            temperature = self._get_mapping(light, self.light_to_temperature)
            # print(f"Light to Temperature: {light} -> {temperature}")

            humidity = self._get_mapping(temperature, self.temperature_to_humidity)
            # print(f"Temperature to Humidity: {temperature} -> {humidity}")

            location = self._get_mapping(humidity, self.humidity_to_location)
            # print(f"Humidity to Location: {humidity} -> {location}")

            print(
                f"{seed} -> {soil} -> {fertilizer} -> {water} -> {light} -> "
                f"{temperature} -> {humidity} -> {location}"
            )

            if not lowest_location or location < lowest_location:
                lowest_location = location

        return lowest_location or -1


maps = Maps(input_file)
lowest = maps.find_lowest_location()

print(lowest)
