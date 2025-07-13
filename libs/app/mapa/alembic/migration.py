from alembic.config import Config
from alembic import command


class Migration():
    def __init__(self, script_location: str, dsn: str):
        super().__init__()
        self.script_location = script_location
        self.dsn = dsn

    def upgrade_migrations(self) -> None:
        alembic_cfg = Config()
        alembic_cfg.set_main_option('script_location', self.script_location)
        alembic_cfg.set_main_option('sqlalchemy.url', self.dsn)
        command.upgrade(alembic_cfg, 'head')
