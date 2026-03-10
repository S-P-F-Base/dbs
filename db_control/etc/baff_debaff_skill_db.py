from typing import Literal

from ..base_db import BaseDB, TableSpec

BaffDebaffType = Literal[
    "mex_baff",
    "mex_debaff",
    "rp_baff",
    "rp_debaff",
    "skill",
]


class BaffDebaffSkillDB(BaseDB):
    _db_name = "baff_debaff_skill_db"

    TABLE = TableSpec(
        name="baff_debaff_skill_db",
        columns=[
            "uid INTEGER PRIMARY KEY AUTOINCREMENT",  # uuid
            "name TEXT NOT NULL",  # имя
            "description TEXT ",  # описание навыка
            "type TEXT",  # тип навыка
            "balance INTEGER",  # сколько стоит
        ],
    )
