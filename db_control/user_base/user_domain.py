from . import AccessDB, CredentialsDB, CustomizationDB, LimitDB


class UserDomain:
    @staticmethod
    def set_up_bd():
        CredentialsDB.set_up()
        AccessDB.set_up()
        CustomizationDB.set_up()
        LimitDB.set_up()

    @staticmethod
    def create_new_user(discord_id: int, steam_id: int | None = None) -> int:
        """TODO:"""
        ...

    @staticmethod
    def delete_user(cid: int) -> None:
        CredentialsDB.set_dead(cid)

    @staticmethod
    def restore_user(cid: int) -> None:
        CredentialsDB.clear_dead(cid)
