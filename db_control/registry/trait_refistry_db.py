from typing import Literal

from ..base_db import BaseDB, TableSpec

DomainType = Literal["mech", "rp"]
KindType = Literal["buff", "debuff", "skill"]
IsBioType = Literal["yes", "no", "any"]


class TraitRegistryDB(BaseDB):
    _db_name = "trait_registry"

    TABLE = TableSpec(
        name="trait_registry",
        columns=[
            "uid INTEGER PRIMARY KEY AUTOINCREMENT",  # uuid
            "name TEXT NOT NULL",  # имя
            "description TEXT",  # описание навыка
            "domain TEXT",  # DomainType
            "kind TEXT",  # KindType
            "cost INTEGER",  # Стоймость
            "is_bio TEXT",  # Является ли био
        ],
    )

    @classmethod
    def set_up(cls) -> None:
        cls._init_from_spec(cls.TABLE)
