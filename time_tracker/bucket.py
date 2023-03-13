from dataclasses import dataclass, field


@dataclass
class Bucket:
    id: str = field()
    name: str = field()
    area: str = field()

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, str):
            return __o.lower() in [self.name.lower(), self.id.lower()]

        if isinstance(__o, Bucket):
            return __o.name.lower() == self.name.lower()

        raise TypeError(f"Object of type {type(__o)} can't be compared with a Bucket")

    def __str__(self) -> str:
        return f"{self.name} ({self.area})"


def parse_bucket(raw_entry):
    _id: str = raw_entry["id"]
    name: str = raw_entry["properties"]["Name"]["title"][0]["plain_text"]
    area: str = raw_entry["properties"]["Area"]["select"]["name"]

    return Bucket(_id, name, area)
