from logging.config import fileConfig
from alembic.script import ScriptDirectory

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from mapa.spatial.namespace.namespace_entity import NamespaceEntity
from mapa.spatial.map_layer.map_layer_entity import MapLayerEntity
from mapa.spatial.map.map_entity import MapEntity
from mapa.spatial.connection.connection_entity import ConnectionEntity
from mapa.spatial.layer.layer_entity import LayerEntity
from mapa.spatial.definition.definition_entity import DefinitionEntity
from mapa.spatial.layer_definition.layer_definition_entity import LayerDefinitionEntity
from mapa.spatial.reference.reference_entity import ReferenceEntity
from mapa.spatial.bookmark.bookmark_entity import BookmarkEntity
from mapa.spatial.base_layer.base_layer_entity import BaseLayerEntity
from mapa.spatial.map_base_layer.map_base_layer_entity import MapBaseLayerEntity

from mapa.spatial.hook.hook_entity import HookEntity
from mapa.spatial.layer_hook.layer_hook_entity import LayerHookEntity


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
# target_metadata = mymodel.Base.metadata
target_metadata_all = [
    NamespaceEntity.metadata,
    MapEntity.metadata,
    ConnectionEntity.metadata,
    LayerEntity.metadata,
    DefinitionEntity.metadata,
    LayerDefinitionEntity.metadata,
    MapLayerEntity.metadata,
    ReferenceEntity.metadata,
    BookmarkEntity.metadata,
    BaseLayerEntity.metadata,
    MapBaseLayerEntity.metadata,
    HookEntity.metadata,
    LayerHookEntity.metadata,
]

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

"""Oluşturulan version numarasını yönetmektedir."""


def process_revision_directives(context, revision, directives):
    # extract Migration
    migration_script = directives[0]
    # extract current head revision
    head_revision = ScriptDirectory.from_config(
        context.config).get_current_head()

    if head_revision is None:
        # edge case with first migration
        new_rev_id = 1
    else:
        # default branch with incrementation
        last_rev_id = int(head_revision.lstrip('0'))
        new_rev_id = last_rev_id + 1
    # fill zeros up to 8 digits: 1 -> 00000001
    migration_script.rev_id = '{0:08}'.format(new_rev_id)


"""Şemaya ait tabloları kontrol eder"""


def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table" and object.schema != "spatial":
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
            version_table='alembic_version_spatial',
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
                version_table='alembic_version_spatial',
                process_revision_directives=process_revision_directives,
            )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
