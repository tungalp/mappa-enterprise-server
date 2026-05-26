from logging.config import fileConfig
from alembic.script import ScriptDirectory

from sqlalchemy import engine_from_config, pool, text

from alembic import context

# Import entities to ensure they are registered on the Base.metadata
from desktop_mobile.models.entities import (
    Base,
    CollectionEntity,
    MapEntity,
    LayerEntity,
    ApiKeyEntity,
    ApiKeyPermissionEntity
)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata_all = [Base.metadata]

def process_revision_directives(context, revision, directives):
    migration_script = directives[0]
    head_revision = ScriptDirectory.from_config(
        context.config).get_current_head()

    if head_revision is None:
        new_rev_id = 1
    else:
        last_rev_id = int(head_revision.lstrip('0'))
        new_rev_id = last_rev_id + 1
    migration_script.rev_id = '{0:08}'.format(new_rev_id)

def include_object(object, name, type_, reflected, compare_to):
    # Only manage tables that are part of the desktop_mobile schema
    if type_ == "table" and object.schema != "desktop_mobile":
        return False
    else:
        return True

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    for target_metadata in target_metadata_all:
        context.configure(
            url=url,
            target_metadata=target_metadata,
            include_schemas=True,
            include_object=include_object,
            literal_binds=True,
            dialect_opts={"paramstyle": "named"},
            version_table_schema="desktop_mobile",
            version_table='alembic_version_desktop_mobile',
            process_revision_directives=process_revision_directives,
        )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        with connection.begin():
            connection.execute(text("CREATE SCHEMA IF NOT EXISTS desktop_mobile"))

        for target_metadata in target_metadata_all:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                include_schemas=True,
                include_object=include_object,
                version_table_schema="desktop_mobile",
                version_table='alembic_version_desktop_mobile',
                process_revision_directives=process_revision_directives,
            )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
