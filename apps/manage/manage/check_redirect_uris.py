from typing import List
from sqlalchemy import create_engine, Table, MetaData, select, update

def check_redirect_uris(conn_string: str, client_id_list: List[str], domain: str):
    # Setup the database connection
    engine = create_engine(conn_string)
    connection = engine.connect()
    metadata = MetaData()
    clients_table = Table('client', metadata, autoload_with=engine, schema='manage')

    try:
        # Query the table for clients with names in the given name list
        query = select(clients_table).where(clients_table.c.client_id.in_(client_id_list))
        result = connection.execute(query)
        data = [dict(row) for row in result.mappings()
                ] if result.returns_rows else []
        for row in data:
            redirect_uris = row['redirect_uris']
            client_id = row["client_id"]
            uris = [
                f"http://{client_id}.{domain}/callback",
                f"http://{client_id}.{domain}/callback_silent",
                f"https://{client_id}.{domain}/callback",
                f"https://{client_id}.{domain}/callback_silent",                
            ]
            
            if uris[0] not in redirect_uris:
                redirect_uris.extend(uris)
                # Update the redirect_uris field in the database
                update_stmt = (
                    update(clients_table)
                    .where(clients_table.c.client_id == client_id)
                    .values(redirect_uris=redirect_uris)
                )
                connection.execute(update_stmt)
                connection.commit()
            else:
                print(f"URI already exists for client {client_id}: {domain}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        connection.close()