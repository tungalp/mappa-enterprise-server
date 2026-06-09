import json
from sqlalchemy import create_engine, text

engine = create_engine('postgresql://postgres:postgres@postgres/mapa_test')

with engine.connect() as conn:
    res = conn.execute(text("SELECT id, name, title, designer_schema FROM application.content_page WHERE name = 'Overlay Rules'"))
    row = res.fetchone()
    if row:
        print("FOUND PAGE:")
        print("ID:", row[0])
        print("NAME:", row[1])
        print("TITLE:", row[2])
        with open('scratch_schema.json', 'w', encoding='utf-8') as f:
            json.dump(row[3], f, indent=2, ensure_ascii=False)
        print("Saved schema to scratch_schema.json")
    else:
        print("PAGE NOT FOUND")
