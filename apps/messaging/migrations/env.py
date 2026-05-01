from logging.config import fileConfig
from alembic.script import ScriptDirectory
from sqlalchemy import engine_from_config, pool
from alembic import context
from messaging.room.entity import RoomEntity, RoomUserEntity
from messaging.message.entity import MessageEntity, MessageFileEntity, SignalEntity
from messaging.outbox.outbox_entity import OutboxEntity

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata_all = [
    RoomEntity.metadata,
    MessageEntity.metadata,
    OutboxEntity.metadata,
]

def process_revision_directives(context, revision, directives):
    migration_script = directives[0]
    head_revision = ScriptDirectory.from_config(context.config).get_current_head()
    if head_revision is None:
        new_rev_id = 1
    else:
        last_rev_id = int(head_revision.lstrip('0'))
        new_rev_id = last_rev_id + 1
    migration_script.rev_id = '{0:08}'.format(new_rev_id)

def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table" and object.schema != "messaging":
        return False
    return True

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    for target_metadata in target_metadata_all:
        context.configure(
            url=url,
            target_metadata=target_metadata,
            include_schemas=True,
            include_object=include_object,
            literal_binds=True,
            dialect_opts={"paramstyle": "named"},
            version_table_schema=target_metadata.schema,
            version_table='alembic_version_messaging',
            process_revision_directives=process_revision_directives,
        )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        for target_metadata in target_metadata_all:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                include_schemas=True,
                include_object=include_object,
                version_table_schema=target_metadata.schema,
                version_table='alembic_version_messaging',
                process_revision_directives=process_revision_directives,
            )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
