"""
table timed_limit X:1
uid для того чтобы колизии доджить
id -> credentials.id
char_slot int
weight_bytes int
expired int timestemp
status str возможно имеет смысл локально хранить как инт, но зная себя я забуду при отдавании поменять инт на стринги и буду очень много орать
"""

from .access_db import AccessDB
from .credentials_db import CredentialsDB
from .db_char_db import DbCharDB
from .perma_limit_db import PermaLimitDB
