drop schema if exists application cascade;
drop schema if exists spatial cascade;
drop schema if exists sso cascade;
drop schema if exists manage cascade;
drop schema if exists gateway cascade;

drop type if exists outbox_status_enum_application cascade;
drop type if exists outbox_status_enum_spatial cascade;
drop type if exists outbox_status_enum_sso cascade;
drop type if exists outbox_status_enum_manage cascade;
drop type if exists outbox_status_enum_gateway cascade;

drop table if exists public.alembic_version_application cascade;
drop table if exists public.alembic_version_spatial cascade;
drop table if exists public.alembic_version_sso cascade;
drop table if exists public.alembic_version_manage cascade;
drop table if exists public.alembic_version_gateway cascade;
