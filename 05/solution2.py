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

    def _get_mapping(self, sid: int, mapping: list, memory: dict) -> int:
        if sid in memory:
            return memory[sid]

        for r in mapping:
            if sid in r.source:
                val = r.destination[r.source.index(sid)]
                memory[sid] = val
                return val
        memory[sid] = sid
        return sid

    def find_lowest_location(self) -> int:
        memory: dict = {x: {} for x in range(0, 7)}

        lowest_location = None
        for seed_range in self.seeds:
            for seed in seed_range:
                if seed in self.seed_mem:
                    location = self.seed_mem[seed]
                else:
                    # Find Soil
                    soil = self._get_mapping(seed, self.seed_to_soil, memory[0])
                    # print(f"Seed to Soil: {seed} -> {soil}")

                    fertilizer = self._get_mapping(
                        soil, self.soil_to_fertilizer, memory[1]
                    )
                    # print(f"Soil to Fertilizer: {soil} -> {fertilizer}")

                    water = self._get_mapping(
                        fertilizer, self.fertilizer_to_water, memory[2]
                    )
                    # print(f"Fertilizer to Water: {fertilizer} -> {water}")

                    light = self._get_mapping(water, self.water_to_light, memory[3])
                    # print(f"Water to Light: {water} -> {light}")

                    temperature = self._get_mapping(
                        light, self.light_to_temperature, memory[4]
                    )
                    # print(f"Light to Temperature: {light} -> {temperature}")

                    humidity = self._get_mapping(
                        temperature, self.temperature_to_humidity, memory[5]
                    )
                    # print(f"Temperature to Humidity: {temperature} -> {humidity}")

                    location = self._get_mapping(
                        humidity, self.humidity_to_location, memory[6]
                    )
                    # print(f"Humidity to Location: {humidity} -> {location}")

                    self.seed_mem[seed] = location

                    # print(
                    #    f"{seed} -> {soil} -> {fertilizer} -> {water} -> {light} -> "
                    #    f"{temperature} -> {humidity} -> {location}"
                    # )

                if not lowest_location or location < lowest_location:
                    lowest_location = location

        return lowest_location or -1


maps = Maps(input_file)
lowest = maps.find_lowest_location()

print(lowest)
