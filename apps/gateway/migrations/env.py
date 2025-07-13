from logging.config import fileConfig
from alembic.script import ScriptDirectory
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

from mapa.core.data.base_entity import Base
from mapa.gateway.connection_info.connection_info_entity import ConnectionInfoEntity
from mapa.gateway.gateway_api.gateway_api_entity import GatewayApiEntity
from mapa.gateway.integration.integration_entity import IntegrationEntity
from mapa.gateway.outbox.outbox_entity import OutboxEntity
from mapa.gateway.parameter_mapping.parameter_mapping_entity import (
    ParameterMappingEntity,
)
from mapa.gateway.route.route_entity import RouteEntity
from mapa.gateway.context_var.context_var_entity import ContextVarEntity

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config


# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
target_metadata_all = [
    ConnectionInfoEntity.metadata,
    GatewayApiEntity.metadata,
    IntegrationEntity.metadata,
    ParameterMappingEntity.metadata,
    RouteEntity.metadata,
    ContextVarEntity.metadata,
    OutboxEntity.metadata,
]
# target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def process_revision_directives(context, revision, directives):
    # extract Migration
    migration_script = directives[0]
    # extract current head revision
    head_revision = ScriptDirectory.from_config(context.config).get_current_head()

    if head_revision is None:
        # edge case with first migration
        new_rev_id = 1
    else:
        # default branch with incrementation
        last_rev_id = int(head_revision.lstrip("0"))
        new_rev_id = last_rev_id + 1
    # fill zeros up to 8 digits: 1 -> 00000001
    migration_script.rev_id = "{0:08}".format(new_rev_id)


def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table" and object.schema != "gateway":
        return False
    else:
        return True


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
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
            version_table="alembic_version_gateway",
            process_revision_directives=process_revision_directives,
        )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
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
                version_table="alembic_version_gateway",
                process_revision_directives=process_revision_directives,
            )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
