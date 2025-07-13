# ALEMBİC KULLANANIM DOKUMANTASYONU



# Yeni bir modulun alembic entegrasyonu yapılacak ise...

Note : Alembic işlemleri `apps` tarafında yapılmaktadır.

1. `libs\app` dan depend olması gerek. `libs\app` üzerinde alembic paketleri tanımlıdır.

2. Yeni modul dizininden (workspace\apps\yeni_module_adı) `poetry update` yapılarak alembic paketleri kullanılabilir hale getirilir.

3. Alembic komutlarının çalıştırılması için yeni modulun dizininde `poetry shell` komutu çalıştırılarak venv a geçiş yapılması gerek.

4. Alembic ve ilgili dosyalarının kurulması için `alembic init migrations` komutu çalıştırılır. Yeni modulde `migrations` klasörü oluşması gerek.

5. Bu adımlardan sonra değiştirilmesi/güncellenmesi gereken dosyalar;    

    *  `apps` \ [yeni_modul_adı] \ `alembic.ini` üzerinde ki güncellemeler ; 

                # sqlalchemy.url = driver://user:pass@localhost/dbname >>> satırı kullanılacak olan veritabanı bağlantısıdır ve aşağıdaki gibi güncellenmesi gerekmektedir.
            
                >>> sqlalchemy.url =  postgresql://mapa:12345Abc.@localhost/mapa_test

    *  `apps` \ [yeni_modul_adı] \ `migrations` \ `script.py.mako` üzerinde ki güncellemeler ; 

                Bu dosya version script dosyalarının hazır bir template'idir. Bu template üzerinde import kısımlarına aşağıdaki satır eklenmelidir.
                
                >>> import sqlalchemy_utils

                Note :  Eğer bir migration işleminden sonra oluşan version dosyasında import edilmesi gereken bir paket ihtiyacı olursa tekrar bu dosyanın import kısmına eklenebilir. Bu sayade bir sonraki migrations işlemlerinde otomatik olarak import satırı da eklenmiş olur. 

    *   `apps` \ [yeni_modul_adı] \ `migrations` \ `env.py` üzerinde ki güncellemeler ; 

        `target_metadata` : migration yapılacak metadata entity listeleri olarak tanımlanmalıdır.

            target_metadata_all = [
                    AuthorizationCodeEntity.metadata,
                    ConsentEntity.metadata,
                    UserSessionClientEntity.metadata,
                    RefreshTokenEntity.metadata,
                    UserSessionEntity.metadata,
            ]

        `Eklenecek Methodlar`

            """Oluşturulan version numarasını yönetmektedir."""
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
                    last_rev_id = int(head_revision.lstrip('0'))
                    new_rev_id = last_rev_id + 1
                # fill zeros up to 8 digits: 1 -> 00000001
                migration_script.rev_id = '{0:08}'.format(new_rev_id)

            """Şemaya ait tabloları kontrol eder"""
            def include_object(object, name, type_, reflected, compare_to):
                if type_ == "table" and object.schema != "[yeni_modul_seması]":
                    return False
                else:
                    return True

        `Mevcutları ile Değiştirilecek Methodlar`

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
                            include_object = include_object,
                            literal_binds=True,
                            dialect_opts={"paramstyle": "named"},
                            version_table_schema=target_metadata.schema,
                            version_table='alembic_version_[yeni_modul_seması]',
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
                        conn = connection.execution_options(schema_translate_map={"[yeni_modul_seması]": target_metadata_all})
                        print("Migrating tenant schema %s" % target_metadata)

                        context.configure(
                            connection=connection,
                            target_metadata=target_metadata,
                            include_schemas=True,
                            include_object = include_object,
                            version_table_schema=target_metadata.schema,
                            version_table='alembic_version_[yeni_modul_seması]',
                            process_revision_directives=process_revision_directives,
                    )

                    with context.begin_transaction():
                        context.run_migrations()

6. `apps` \ [yeni_modul_adı] \ [yeni_modul_adı] \ `app.py` dosyasında eklenmesi gerekenler;

    * Aşağıda ki iki satır en üste import kısımlarına eklenmesi gerek.

      > from mapa.alembic.migration import Migration

    * Aşağıda ki iki satırda `create_application` methodunun sonuna eklenerek, ilgili modulun ayağa kalması sırasında otomatik migration işlemini yapmış olur.

      >  migration = Migration(str(pathlib.Path(__file__).parent.parent / "migrations"), container.config.alembic()["url"])
      >  migration.upgrade_migrations()

7. `apps` \ [yeni_modul_adı] \ [yeni_modul_adı] \ `config` içerisindeki `config.dev.yml` `config.prod.yml` ve `config.yml` dosyalarının en altına aşağıdaki bilgilerin eklenmesi gerekmektedir.

    > alembic:

    > migrations_path: "../[yeni_modul_adı]/migrations"

    > url: "postgresql://mapa:12345Abc.@localhost/mapa_test"


# Var olan bir modulde alembic çalıştırılması...

Note : Alembic işlemleri `apps` tarafında yapılmaktadır.

1.  Alembic komutlarının çalıştırılması için modulun dizininde poetry shell komutu çalıştırılarak venv a geçiş yapılması gerek.

2.  Module ait yeni bir version dosyası hazırlanacak ise;

    * > alembic revision -m "mesaj içeriği"   

        komutu ile standart upgrade ve downgrade işlemlerini boş bir şekilde oluşturur.

    * > alembic revision --autogenerate -m "mesaj içeriği"  

        komutu ile ilgili modulun güncel version'u ile o an ki database entity lerini karşılaştırarak upgrade ve downgrade methodları
        otomatik bir şekilde doldurur ve hazırlar.

3. Hazırlanan version dosyasının veritabanına upgrade işlemi için,

    * > alembic upgrade head 

        komutu ile en güncel versiona ait upgrade işlemi yapar.

    * > alembic upgrade "version numarası" 

        komutu ile ilgili version numarasına ait upgrade işlemi yapar

4. Veritabanına downgrade işlemi için,

    * > alembic downgrade -1 

        komutu ile bir version geriye geçilir.

    * > alembic downgrade base

        komutu ile sondan başa doğru downgrade işlemlerini gerçekleştirir.


# Multi tenant özelliği kazandırmak için tenant_id olan tablolar eklendiği zaman oluşturulan migration version dosyalarına aşağıdakiler eklenmelidir.        
  
* # Tablo listesi tanımlanır  
        table_list = [
            "base_layer",
            "bookmark",
            "map_base_layer",
            "reference",
        ]

* # def upgrade() in en altına 
        # tenant_isolation
        execute_tenant_isolation("spatial", table_list, enable=True)  

* # def downgrade() in en altına 
        # tenant_isolation
        down_list = table_list.copy()
        down_list.reverse()
        execute_tenant_isolation("spatial", down_list, enable=False) 

* # execute_tenant_isolation 
        def execute_tenant_isolation(schema, tables, enable):
            for table in tables:
                full_name = f"{schema}.{table}"
                if enable:
                    op.execute( f"alter table {full_name} enable row level security")
                    op.execute( f"create policy tenant_isolation_insert on {full_name} "
                                f"for INSERT "
                                f"WITH CHECK (current_setting('app.tenant_id') is not null and (select true from (select pg_typeof(uuid(current_setting('app.tenant_id')))::text as typ) s where s.typ = 'uuid'))"
                                )
                    op.execute( f"create policy tenant_isolation_select on {full_name} "
                                f"for SELECT "
                                f"using  ((current_setting('app.tenant_id') = tenant_id::text) OR ((tenant_id)::text = '{str(NULL_TENANT_ID)}'))"
                                )
                    op.execute( f"create policy tenant_isolation_update on {full_name} "
                                f"for UPDATE "
                                f"using  ((current_setting('app.tenant_id') = tenant_id::text))"
                                )
                    op.execute( f"create policy tenant_isolation_delete on {full_name} "
                                f"for DELETE "
                                f"using  ((current_setting('app.tenant_id') = tenant_id::text))"
                                )
                else:
                    op.execute(f"drop policy tenant_isolation_insert on {full_name}")
                    op.execute(f"drop policy tenant_isolation_select on {full_name}")
                    op.execute(f"drop policy tenant_isolation_update on {full_name}")
                    op.execute(f"drop policy tenant_isolation_delete on {full_name}")
                    op.execute(f"alter table {full_name} disable row level security")
