import enum


class ZEnum(enum.Enum):
    def __str__(self):
        return self.name
