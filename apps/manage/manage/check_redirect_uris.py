from typing import List
from sqlalchemy import create_engine, Table, MetaData, select, update

def check_redirect_uris(conn_string: str, name_list: List[str], domain: str):
    # Setup the database connection
    engine = create_engine(conn_string)
    connection = engine.connect()
    metadata = MetaData()
    clients_table = Table('client', metadata, autoload_with=engine, schema='manage')

    try:
        # Query the table for clients with names in the given name list
        query = select(clients_table).where(clients_table.c.name.in_(name_list))
        result = connection.execute(query)
        data = [dict(row) for row in result.mappings()] if result.returns_rows else []
        
        for row in data:
            redirect_uris = list(row.get('redirect_uris') or [])
            logout_uris = list(row.get('logout_uris') or [])
            web_origins = list(row.get('web_origins') or [])
            cors_origins = list(row.get('cors_origins') or [])
            
            client_id = row["client_id"]
            name = row["name"]
            
            uris = [
                f"http://{name}.{domain}/callback",
                f"http://{name}.{domain}/callback_silent",
                f"https://{name}.{domain}/callback",
                f"https://{name}.{domain}/callback_silent",
                f"https://{name}-dev.mapaenterprise.com/callback",
                f"https://{name}-dev.mapaenterprise.com/callback_silent",
            ]
            
            l_uris = [
                f"http://{name}.{domain}/logout",
                f"https://{name}.{domain}/logout",
                f"https://{name}-dev.mapaenterprise.com/logout",
            ]
            
            origins = [
                f"http://{name}.{domain}",
                f"https://{name}.{domain}",
                f"https://{name}-dev.mapaenterprise.com",
            ]
            
            modified = False
            
            for u in uris:
                if u not in redirect_uris:
                    redirect_uris.append(u)
                    modified = True
                    
            for u in l_uris:
                if u not in logout_uris:
                    logout_uris.append(u)
                    modified = True
                    
            for o in origins:
                if o not in web_origins:
                    web_origins.append(o)
                    modified = True
                if o not in cors_origins:
                    cors_origins.append(o)
                    modified = True

            # If this is client_id_application, fetch all dynamic apps and add their callbacks
            if client_id == "client_id_application":
                try:
                    app_table = Table('app', metadata, autoload_with=engine, schema='application')
                    tenant_table = Table('tenant', metadata, autoload_with=engine, schema='manage')
                    j = app_table.join(tenant_table, app_table.c.tenant_id == tenant_table.c.id)
                    q = select(tenant_table.c.name.label('tenant_name'), app_table.c.code.label('app_code')).select_from(j)
                    res = connection.execute(q)
                    apps = [dict(r) for r in res.mappings()]
                    
                    for app in apps:
                        base = f"/{app['tenant_name']}/{app['app_code']}"
                        dyn_uris = [
                            f"http://{name}.{domain}{base}/callback",
                            f"http://{name}.{domain}{base}/callback_silent",
                            f"https://{name}.{domain}{base}/callback",
                            f"https://{name}.{domain}{base}/callback_silent",
                            f"https://{name}-dev.mapaenterprise.com{base}/callback",
                            f"https://{name}-dev.mapaenterprise.com{base}/callback_silent",
                        ]
                        dyn_l_uris = [
                            f"http://{name}.{domain}{base}/logout",
                            f"https://{name}.{domain}{base}/logout",
                            f"https://{name}-dev.mapaenterprise.com{base}/logout",
                        ]
                        
                        for u in dyn_uris:
                            if u not in redirect_uris:
                                redirect_uris.append(u)
                                modified = True
                        for u in dyn_l_uris:
                            if u not in logout_uris:
                                logout_uris.append(u)
                                modified = True
                except Exception as ex:
                    print(f"Warning: Could not fetch dynamic apps for client_id_application: {ex}")

            if modified:
                # Update the redirect_uris field in the database
                update_stmt = (
                    update(clients_table)
                    .where(clients_table.c.client_id == client_id)
                    .values(
                        redirect_uris=redirect_uris,
                        logout_uris=logout_uris,
                        web_origins=web_origins,
                        cors_origins=cors_origins
                    )
                )
                connection.execute(update_stmt)
                connection.commit()
                print(f"URIs updated for client {client_id}")
            else:
                print(f"URIs already exist for client {client_id}")

        # Now handle individual app client_ids
        try:
            app_table = Table('app', metadata, autoload_with=engine, schema='application')
            tenant_table = Table('tenant', metadata, autoload_with=engine, schema='manage')
            j = app_table.join(tenant_table, app_table.c.tenant_id == tenant_table.c.id)
            q = select(tenant_table.c.name.label('tenant_name'), app_table.c.code.label('app_code'), app_table.c.client_id.label('app_client_id')).select_from(j)
            res = connection.execute(q)
            apps = [dict(r) for r in res.mappings()]
            
            for app in apps:
                app_client_id = app.get('app_client_id')
                if not app_client_id:
                    continue
                    
                client_q = select(clients_table).where(clients_table.c.client_id == app_client_id)
                c_res = connection.execute(client_q)
                c_row = c_res.fetchone()
                if not c_row:
                    continue
                
                c_dict = dict(c_row._mapping)
                c_redirect_uris = list(c_dict.get('redirect_uris') or [])
                c_logout_uris = list(c_dict.get('logout_uris') or [])
                c_web_origins = list(c_dict.get('web_origins') or [])
                c_cors_origins = list(c_dict.get('cors_origins') or [])
                
                base = f"/{app['tenant_name']}/{app['app_code']}"
                # The name variable is not easily available, we use default 'application' for domain parts
                name = "application"
                dyn_uris = [
                    f"http://{name}.{domain}{base}/callback",
                    f"http://{name}.{domain}{base}/callback_silent",
                    f"https://{name}.{domain}{base}/callback",
                    f"https://{name}.{domain}{base}/callback_silent",
                    f"https://{name}-dev.mapaenterprise.com{base}/callback",
                    f"https://{name}-dev.mapaenterprise.com{base}/callback_silent",
                ]
                dyn_l_uris = [
                    f"http://{name}.{domain}{base}/logout",
                    f"https://{name}.{domain}{base}/logout",
                    f"https://{name}-dev.mapaenterprise.com{base}/logout",
                ]
                dyn_origins = [
                    f"http://{name}.{domain}",
                    f"https://{name}.{domain}",
                    f"https://{name}-dev.mapaenterprise.com",
                ]
                
                c_modified = False
                for u in dyn_uris:
                    if u not in c_redirect_uris:
                        c_redirect_uris.append(u)
                        c_modified = True
                for u in dyn_l_uris:
                    if u not in c_logout_uris:
                        c_logout_uris.append(u)
                        c_modified = True
                for o in dyn_origins:
                    if o not in c_web_origins:
                        c_web_origins.append(o)
                        c_modified = True
                    if o not in c_cors_origins:
                        c_cors_origins.append(o)
                        c_modified = True
                        
                if c_modified:
                    update_stmt = (
                        update(clients_table)
                        .where(clients_table.c.client_id == app_client_id)
                        .values(
                            redirect_uris=c_redirect_uris,
                            logout_uris=c_logout_uris,
                            web_origins=c_web_origins,
                            cors_origins=c_cors_origins
                        )
                    )
                    connection.execute(update_stmt)
                    connection.commit()
                    print(f"URIs updated for app client {app_client_id}")

        except Exception as ex:
            print(f"Warning: Could not process individual app clients: {ex}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        connection.close()