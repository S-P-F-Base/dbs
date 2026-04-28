from enum import Enum


class RWD(Enum):
    READ = 0b001
    WRITE = 0b010
    DELETE = 0b100

    READ_WRITE = 0b011
    READ_DELETE = 0b101
    WRITE_DELETE = 0b110

    ALL = 0b111
    NONE = 0b000


BASE_ACCESS = {
    "full": False,
    "give": False,
    "modules": {
        "admin": RWD.NONE.value,
    },
}
