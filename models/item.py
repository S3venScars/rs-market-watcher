from datetime import datetime
from dataclasses import dataclass, field

@dataclass
class ItemPrice:
    item_id: int
    name: str
    high: int
    low: int
    high_time: int
    low_time: int

    @property
    def high_time_str(self):
        return datetime.fromtimestamp(self.high_time).strftime("%Y-%m-%d %H:%M:%S")

    @property
    def low_time_str(self):
        return datetime.fromtimestamp(self.low_time).strftime("%Y-%m-%d %H:%M:%S")

    def to_row(self):
        return [
            str(self.item_id),
            self.name,
            str(self.high),
            self.high_time_str,
            str(self.low),
            self.low_time_str
        ]
