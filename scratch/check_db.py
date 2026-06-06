import psycopg2

conn = psycopg2.connect("postgresql://postgres:postgres@postgres/mapa_test")
cur = conn.cursor()

tables = [
    'manage.user', 'manage.tenant', 'manage.tenant_user',
    'messaging.room', 'messaging.room_users', 'messaging.message'
]

for t in tables:
    try:
        cur.execute(f"SELECT COUNT(*) FROM {t};")
        count = cur.fetchone()[0]
        print(f"Row count for {t}: {count}")
    except Exception as e:
        print(f"Failed to count rows for {t}: {e}")
        conn.rollback()

cur.close()
conn.close()
