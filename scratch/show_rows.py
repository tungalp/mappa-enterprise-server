import psycopg2

conn = psycopg2.connect("postgresql://postgres:postgres@postgres/mapa_test")
cur = conn.cursor()

print("=== Users ===")
cur.execute("SELECT id, name, surname, email FROM manage.user;")
for u in cur.fetchall():
    print(u)

print("\n=== Rooms ===")
cur.execute("SELECT id, name, tenant_id FROM messaging.room;")
for r in cur.fetchall():
    print(r)

print("\n=== Room Users ===")
cur.execute("SELECT room_id, user_id FROM messaging.room_users;")
for ru in cur.fetchall():
    print(ru)

print("\n=== Messages (First 10) ===")
cur.execute("SELECT id, sender_id, room_id, message, created_at FROM messaging.message ORDER BY created_at DESC LIMIT 10;")
for m in cur.fetchall():
    print(m)

cur.close()
conn.close()
