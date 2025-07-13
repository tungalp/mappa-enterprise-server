from sqlalchemy import Engine, text

from mapa.core.data.async_db import AsyncDatabase


async def create_kisi_model(db: AsyncDatabase):
    async with db.session() as session:
        await session.execute(text(
            "create schema adhoc authorization postgres"
        ))
        await session.execute(text(
            "GRANT USAGE ON SCHEMA adhoc TO mapa"
        ))
        await session.execute(text(
            "CREATE table if not exists adhoc.ulke ("
	        "id serial NOT NULL,"
	        "ad text NOT NULL,"
	        "CONSTRAINT ulke_il_pkey PRIMARY KEY (id))"
        ))        
        await session.execute(text(
            "CREATE table if not exists adhoc.il ("
	        "id serial NOT NULL,"
	        "ad text NOT NULL,"
            "ulke_id int4 not null,"
	        "CONSTRAINT il_pkey PRIMARY KEY (id),"
            "CONSTRAINT il_ulke_fkey FOREIGN KEY (ulke_id) REFERENCES adhoc.ulke(id))"
        ))        
        await session.execute(text(
            "CREATE TABLE adhoc.ilce ("
            "id serial NOT NULL,"
            "ad text NOT NULL,"
            "il_id int4 not null,"
            "CONSTRAINT ilce_pkey PRIMARY KEY (id),"
            "CONSTRAINT ilce_il_fkey FOREIGN KEY (il_id) REFERENCES adhoc.il(id))"
        ))
        await session.execute(text(
            "CREATE TABLE adhoc.sokak ("
            "id serial NOT NULL,"
            "ad text NOT NULL,"
            "il_id int4 not null,"
            "CONSTRAINT sokak_pkey PRIMARY KEY (id),"
            "CONSTRAINT sokak_il_fkey FOREIGN KEY (il_id) REFERENCES adhoc.il(id))"
        ))
        await session.execute(text(
            "CREATE TABLE adhoc.adres ("
            "id serial NOT NULL,"
            "kapi_no text NOT NULL,"
            "sokak_id int4 NOT NULL,"
            "CONSTRAINT adres_pkey PRIMARY KEY (id),"
            "CONSTRAINT adres_sokak_fkey FOREIGN KEY (sokak_id) REFERENCES adhoc.sokak(id))"
        ))
        await session.execute(text(
            "CREATE TABLE adhoc.kisi ("
            "id serial NOT NULL,"
            "ad varchar(100) NOT NULL,"
            "soyad varchar(100) NOT NULL,"
            "ev_adres_id int4 not NULL,"
            "is_adres_id int4 null,"
            "ilce_id int4 not null,"
            "created_at timestamp NOT NULL DEFAULT now(),"
            "parent_id int4 null,"
            "CONSTRAINT kisi_pkey PRIMARY KEY (id),"
            "CONSTRAINT kisi_ev_adres_fkey FOREIGN KEY (ev_adres_id) REFERENCES adhoc.adres(id),"
            "CONSTRAINT kisi_is_adres_fkey FOREIGN KEY (is_adres_id) REFERENCES adhoc.adres(id),"
            "CONSTRAINT kisi_ilce_fkey FOREIGN KEY (ilce_id) REFERENCES adhoc.ilce(id),"
            "CONSTRAINT kisi_parent_fkey FOREIGN KEY (parent_id) REFERENCES adhoc.kisi(id))"
        ))
        await session.execute(text(
            "CREATE TABLE adhoc.kisi2 ("
            "id serial NOT NULL,"
            "ad varchar(100) NOT NULL,"
            "soyad varchar(100) NOT NULL,"
            "ev_adres_id int4 not NULL,"
            "is_adres_id int4 null,"
            "ilce_id int4 not null,"
            "dogum_tarihi date null,"
            "uyruk int4 null,"
            "created_at timestamp NOT NULL DEFAULT now(),"
            "CONSTRAINT kisi2_pkey PRIMARY KEY (id),"
            "CONSTRAINT kisi2_ev_adres_fkey FOREIGN KEY (ev_adres_id) REFERENCES adhoc.adres(id),"
            "CONSTRAINT kisi2_is_adres_fkey FOREIGN KEY (is_adres_id) REFERENCES adhoc.adres(id),"
            "CONSTRAINT kisi2_ilce_fkey FOREIGN KEY (ilce_id) REFERENCES adhoc.ilce(id))"
        ))
        await session.execute(text(
            "insert into adhoc.ulke (id, ad) values "
            "(1, 'Türkiye'), (2, 'Rusya')"
        ))
        
        await session.execute(text(
            "insert into adhoc.il (id, ad, ulke_id) values "
            "(1, 'Antalya', 2), (2, 'Ankara', 1),"
            "(3, 'Mersin', 2), (4, 'Yozgat', 1)"
        ))
        await session.execute(text(
            "insert into adhoc.ilce (id, ad, il_id) values "
            "(1, 'Muratpasa', 1), (2, 'Konyaaltı', 1), (3, 'Çankaya', 2), (4, 'Yenimahalle', 2),"
            "(5, 'Tarsus', 3), (6, 'Silifke', 3), (7, 'Sorgun', 4), (8, 'Yerköy', 4)"
        ))
        await session.execute(text(
            "insert into adhoc.sokak (id, ad, il_id) values "
            "(1, '1001', 1), (2, '1002', 1), (3, '1003', 1), (4, '1004', 1),"
            "(5, '2001', 2), (6, '2002', 2), (7, '2003', 2), (8, '2004', 2)"
        ))
        await session.execute(text(
            "insert into adhoc.adres (id, kapi_no, sokak_id) values "
            "(1, '1', 1), (2, '2', 2), (3, '3', 3), (4, '4', 4),"
            "(5, '5', 5), (6, '6', 6), (7, '7', 7), (8, '8', 8)"
        ))
        await session.execute(text(
            "insert into adhoc.kisi (id, ad, soyad, ev_adres_id, is_adres_id, ilce_id, parent_id) values "
            "(1, 'aAd 1', 'Soyad 1', 1, 5, 1, null),"
            "(2, 'dAd 2', 'Soyad 2', 2, 6, 2, 1),"
            "(3, 'bAd 3', 'Soyad 3', 3, 7, 3, null),"
            "(4, 'hAd 4', 'Soyad 4', 4, 8, 4, 3),"
            "(5, 'tAd 5', 'Soyad 5', 4, 8, 3, 1),"
            "(6, 'eAd 6', 'Soyad 6', 1, 5, 1, 1),"
            "(7, 'sAd 7', 'Soyad 7', 3, 7, 4, 4),"
            "(8, 'kAd 8', 'Soyad 8', 2, 6, 2, 3),"
            "(9, 'mAd 9', 'Soyad 9', 1, 5, 1, null),"
            "(10, 'rAd 10', 'Soyad 10', 2, 6, 2, 1),"
            "(11, 'pAd 11', 'Soyad 11', 1, 5, 1, null),"
            "(12, 'oAd 12', 'Soyad 12', 2, 6, 2, 1),"
            "(13, 'uAd 13', 'Soyad 13', 3, 7, 3, null),"
            "(14, 'yAd 14', 'Soyad 14', 4, 8, 4, 3),"
            "(15, 'tAd 15', 'Soyad 15', 4, 8, 3, 1),"
            "(16, 'rAd 16', 'Soyad 16', 1, 5, 1, 1),"
            "(17, 'eAd 17', 'Soyad 17', 3, 7, 4, 4),"
            "(18, 'wAd 18', 'Soyad 18', 2, 6, 2, 3),"
            "(19, 'qAd 19', 'Soyad 19', 1, 5, 1, null),"
            "(20, 'qAd 10', 'Soyad 10', 2, 6, 2, 1),"
            "(21, 'aAd 21', 'Soyad 21', 1, 5, 1, null),"
            "(22, 'dAd 22', 'Soyad 22', 2, 6, 2, 1),"
            "(23, 'fAd 23', 'Soyad 23', 3, 7, 3, null),"
            "(24, 'gAd 24', 'Soyad 24', 4, 8, 4, 3),"
            "(25, 'gAd 25', 'Soyad 25', 4, 8, 3, 1),"
            "(26, 'hAd 26', 'Soyad 26', 1, 5, 1, 1),"
            "(27, 'lAd 27', 'Soyad 27', 3, 7, 4, 4),"
            "(28, 'iAd 28', 'Soyad 28', 2, 6, 2, 3),"
            "(29, 'jAd 29', 'Soyad 29', 1, 5, 1, null),"
            "(30, 'kAd 30', 'Soyad 30', 2, 6, 2, 1)"            
        ))
        await session.execute(text(
            "insert into adhoc.kisi2 (id, ad, soyad, ev_adres_id, is_adres_id, ilce_id, uyruk) values "
            "(1, 'aAd 1', 'Soyad 1', 1, 5, 1, 1),"
            "(2, 'dAd 2', 'Soyad 2', 2, 6, 2, 1),"
            "(3, 'bAd 3', 'Soyad 3', 3, 7, 3, 1),"
            "(4, 'hAd 4', 'Soyad 4', 4, 8, 4, 1),"
            "(5, 'tAd 5', 'Soyad 5', 4, 8, 3, 1),"
            "(6, 'eAd 6', 'Soyad 6', 1, 5, 1, 1),"
            "(7, 'sAd 7', 'Soyad 7', 3, 7, 4, 1),"
            "(8, 'kAd 8', 'Soyad 8', 2, 6, 2, 1),"
            "(9, 'mAd 9', 'Soyad 9', 1, 5, 1, 1),"
            "(10, 'rAd 10', 'Soyad 10', 2, 6, 2, 1),"
            "(11, 'pAd 11', 'Soyad 11', 1, 5, 1, 1),"
            "(12, 'oAd 12', 'Soyad 12', 2, 6, 2, 1),"
            "(13, 'uAd 13', 'Soyad 13', 3, 7, 3, 1),"
            "(14, 'yAd 14', 'Soyad 14', 4, 8, 4, 1),"
            "(15, 'tAd 15', 'Soyad 15', 4, 8, 3, 1),"
            "(16, 'rAd 16', 'Soyad 16', 1, 5, 1, 1),"
            "(17, 'eAd 17', 'Soyad 17', 3, 7, 4, 1),"
            "(18, 'wAd 18', 'Soyad 18', 2, 6, 2, 1),"
            "(19, 'qAd 19', 'Soyad 19', 1, 5, 1, 1),"
            "(20, 'qAd 10', 'Soyad 10', 2, 6, 2, 1),"
            "(21, 'aAd 21', 'Soyad 21', 1, 5, 1, 1),"
            "(22, 'dAd 22', 'Soyad 22', 2, 6, 2, 1),"
            "(23, 'fAd 23', 'Soyad 23', 3, 7, 3, 1),"
            "(24, 'gAd 24', 'Soyad 24', 4, 8, 4, 1),"
            "(25, 'gAd 25', 'Soyad 25', 4, 8, 3, 1),"
            "(26, 'hAd 26', 'Soyad 26', 1, 5, 1, 1),"
            "(27, 'lAd 27', 'Soyad 27', 3, 7, 4, 1),"
            "(28, 'iAd 28', 'Soyad 28', 2, 6, 2, 1),"
            "(29, 'jAd 29', 'Soyad 29', 1, 5, 1, 1),"
            "(30, 'kAd 30', 'Soyad 30', 2, 6, 2, 1)"
        ))
        await session.execute(text(
            "GRANT ALL ON SCHEMA adhoc TO mapa"
        ))
        await session.execute(text(
            "GRANT ALL ON TABLE adhoc.ulke TO mapa"
        ))
        await session.execute(text(
            "GRANT ALL ON TABLE adhoc.il TO mapa"
        ))
        await session.execute(text(
            "GRANT ALL ON TABLE adhoc.ilce TO mapa"
        ))
        await session.execute(text(
            "GRANT ALL ON TABLE adhoc.sokak TO mapa"
        ))
        await session.execute(text(
            "GRANT ALL ON TABLE adhoc.adres TO mapa"
        ))
        await session.execute(text(
            "GRANT ALL ON TABLE adhoc.kisi TO mapa"
        ))
        await session.execute(text(
            "GRANT ALL ON TABLE adhoc.kisi2 TO mapa"
        ))
        await session.execute(text(
            "GRANT ALL ON SEQUENCE adhoc.ulke_id_seq TO mapa"
        ))
        await session.execute(text(
            "GRANT ALL ON SEQUENCE adhoc.il_id_seq TO mapa"
        ))
        await session.execute(text(
            "GRANT ALL ON SEQUENCE adhoc.ilce_id_seq TO mapa"
        ))
        await session.execute(text(
            "GRANT ALL ON SEQUENCE adhoc.sokak_id_seq TO mapa"
        ))
        await session.execute(text(
            "GRANT ALL ON SEQUENCE adhoc.adres_id_seq TO mapa"
        ))
        await session.execute(text(
            "GRANT ALL ON SEQUENCE adhoc.kisi_id_seq TO mapa"
        ))
        await session.execute(text(
            "GRANT ALL ON SEQUENCE adhoc.kisi2_id_seq TO mapa"
        ))
        await session.execute(text(
            "SELECT setval('adhoc.ulke_id_seq', (SELECT MAX(id) FROM adhoc.ulke) + 1)"
        ))
        await session.execute(text(
            "SELECT setval('adhoc.il_id_seq', (SELECT MAX(id) FROM adhoc.il) + 1)"
        ))
        await session.execute(text(
            "SELECT setval('adhoc.ilce_id_seq', (SELECT MAX(id) FROM adhoc.ilce) + 1)"
        ))
        await session.execute(text(
            "SELECT setval('adhoc.sokak_id_seq', (SELECT MAX(id) FROM adhoc.sokak) + 1)"
        ))
        await session.execute(text(
            "SELECT setval('adhoc.adres_id_seq', (SELECT MAX(id) FROM adhoc.adres) + 1)"
        ))
        await session.execute(text(
            "SELECT setval('adhoc.kisi_id_seq', (SELECT MAX(id) FROM adhoc.kisi) + 1)"
        ))
        await session.execute(text(
            "SELECT setval('adhoc.kisi2_id_seq', (SELECT MAX(id) FROM adhoc.kisi2) + 1)"
        ))
        await session.commit()
