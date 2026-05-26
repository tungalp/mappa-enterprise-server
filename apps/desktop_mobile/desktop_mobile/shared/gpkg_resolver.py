import json
from datetime import datetime, timezone
import tempfile
import hashlib
import sqlite3
import os
import shutil
import glob
import binascii

from anyio import open_file, to_thread
from typing import Any, Dict, List, Optional, Union, Tuple
import pandas as pd
import geopandas as gpd
from shapely import wkb

class GPKGConflictResolver:

    row_guid = "fid"
    
    exclude_fields = [
        'fid', 'last_updated', 'download_time', 'processing_timestamp', 
        'row_id', 'created_at', 'modified_at', 'updated_at',
        'timestamp', 'sync_time', 'import_date', 'geometry', 'geom'
    ]

    def __init__(self):
        self.change_history = []

    def convert_download_time(self, time_str: str) -> Optional[datetime]:
        """
        Standardizes a time string into a UTC-aware datetime object.
        """
        if not time_str:
            return None
            
        try:
            fixed_str = time_str.replace('Z', '+00:00')
            dt = datetime.fromisoformat(fixed_str)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except ValueError:
            return None
                
    def delete_inactive_gpkg_files(self, project_folder: str):
        """
        Deletes .gpkg files in the specified folder only if they 
        do not have associated active WAL or SHM files.
        """
        gpkg_pattern = os.path.join(project_folder, "*.gpkg")
        gpkg_files = glob.glob(gpkg_pattern)
        deleted_count = 0

        for gpkg_path in gpkg_files:
            wal_path = f"{gpkg_path}-wal"
            shm_path = f"{gpkg_path}-shm"

            if os.path.exists(wal_path) or os.path.exists(shm_path):
                print(f"Skipping {os.path.basename(gpkg_path)}: File is currently BUSY (WAL/SHM present).")
                continue
            
            try:
                os.remove(gpkg_path)
                deleted_count += 1
                print(f"Successfully deleted: {os.path.basename(gpkg_path)}")
            except Exception as e:
                print(f"Error deleting {gpkg_path}: {e}")

        print(f"\nCleanup complete. Total files deleted: {deleted_count}")

    async def file_store_to_gpkg_async(self, file_store, project_temp_dir: str, file_name: str = "") -> str:
        """
        Copies a GeoPackage from a file_store object to a local path 
        using streaming to keep RAM usage low.
        """
        if not os.path.exists(project_temp_dir):
            os.makedirs(project_temp_dir, exist_ok=True)
            print(f"Created temporary directory: {project_temp_dir}")

        if file_name.strip():
            tmp_path = os.path.join(project_temp_dir, file_name.strip())
        else:
            with tempfile.NamedTemporaryFile(suffix=".gpkg", dir=project_temp_dir, delete=False) as tmp:
                tmp_path = tmp.name

        try:
            await file_store.seek(0)

            def _stream_copy_logic():
                with open(tmp_path, 'wb') as destination_file:
                    shutil.copyfileobj(file_store.file, destination_file)
                return tmp_path

            final_path = await to_thread.run_sync(_stream_copy_logic)
            return final_path
        except Exception as e:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            raise Exception(f"Failed to stream GPKG to disk: {str(e)}")
            
    async def file_path_to_gpkg_async(self, source_path: str, project_temp_dir: str, file_name: str = "") -> str:
        """
        Copies a GeoPackage from one path to another asynchronously.
        """
        if not os.path.exists(project_temp_dir):
            os.makedirs(project_temp_dir, exist_ok=True)
            print(f"Created temporary directory: {project_temp_dir}")
            
        if file_name.strip():
            dest_path = os.path.join(project_temp_dir, file_name.strip())
        else:
            with tempfile.NamedTemporaryFile(suffix=".gpkg", dir=project_temp_dir, delete=False) as tmp:
                dest_path = tmp.name

        def _copy_logic():
            os.makedirs(project_temp_dir, exist_ok=True)
            return shutil.copy2(source_path, dest_path)

        try:
            final_path = await to_thread.run_sync(_copy_logic)
            return final_path
        except Exception as e:
            raise Exception(f"Failed to copy GPKG from {source_path} to {dest_path}: {str(e)}")
        
    async def blob_to_gpkg_async(self, blob_data: bytes, project_temp_dir: str, file_name: str = "") -> str:
        tmp_path = file_name.strip()
        if tmp_path == "":
            with tempfile.NamedTemporaryFile(suffix=".gpkg", dir=project_temp_dir, delete=False) as tmp:
                tmp_path = tmp.name

        async with await open_file(tmp_path, mode='wb') as f:
            await f.write(blob_data)

        return tmp_path

    def blob_to_gpkg(self, blob_data: bytes) -> str:
        with tempfile.NamedTemporaryFile(suffix=".gpkg", delete=False) as tmp:
            tmp.write(blob_data)
            tmp_path = tmp.name
        return tmp_path

    async def gpkg_to_blob_async(self, temp_path: str) -> bytes:
        try:
            async with await open_file(temp_path, mode='rb') as f:
                blob_data = await f.read()
            return blob_data
        finally:
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except Exception as e:
                print(f"Cleanup error in gpkg_to_blob: {e}")

    def gpkg_to_blob(self, temp_path: str) -> bytes:
        try:
            with open(temp_path, "rb") as f:
                blob_data = f.read()
            return blob_data
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def read_gpkg_sync_tables_to_json(self, file_path: str, cls_name: str) -> Dict[str, Any]:
        sync_tables = {
            'changes': {}, 
            'metadata': {'download_time': None}
        }
        
        try:
            conn = sqlite3.connect(file_path)
            conn.row_factory = sqlite3.Row
            
            try:
                cursor = conn.execute(f"SELECT key, value FROM sync_metadata_{cls_name} WHERE key = 'download_time'")
                row = cursor.fetchone()
                if row:
                    sync_tables['metadata']['download_time'] = row['value']
            except sqlite3.OperationalError:
                pass

            try:
                cursor = conn.execute(f"SELECT timestamp, userid, changed_features FROM sync_changes_{cls_name} ORDER BY timestamp ASC")
                for row in cursor:
                    sync_tables['changes'][row['timestamp']] = {
                        'userid': row['userid'],
                        'changed_features': json.loads(row['changed_features'])
                    }
            except sqlite3.OperationalError:
                pass

            conn.close()
        except Exception as e:
            print(f"Error reading GPKG metadata: {e}")
            return {'changes': {}, 'metadata': {'download_time': None}}
            
        return sync_tables
    
    def write_sync_json_to_gpkg(self, sync_info: Dict[str, Any], temp_path: str, cls_name: str):
        conn = sqlite3.connect(temp_path)
        try:
            download_time = sync_info.get('metadata', {}).get('download_time')

            if download_time:
                conn.execute(f"CREATE TABLE IF NOT EXISTS sync_metadata_{cls_name} (key TEXT PRIMARY KEY, value TEXT)")
                conn.execute(f"INSERT OR REPLACE INTO sync_metadata_{cls_name} (key, value) VALUES (?, ?)", 
                            ('download_time', download_time))
            else:
                conn.execute(f"DROP TABLE IF EXISTS sync_metadata_{cls_name}")

            changes = sync_info.get('changes', {})
            if changes:
                conn.execute(f"""
                    CREATE TABLE IF NOT EXISTS sync_changes_{cls_name} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT,
                        userid TEXT,
                        changed_features TEXT
                    )
                """)

                for timestamp, content in changes.items():
                    userid = content.get('userid')
                    changed_features_json = json.dumps(content.get('changed_features', []))
                    
                    cursor = conn.execute(
                        f"SELECT id FROM sync_changes_{cls_name} WHERE timestamp = ? AND userid = ?", 
                        (timestamp, userid)
                    )
                    if not cursor.fetchone():
                        conn.execute(
                            f"INSERT INTO sync_changes_{cls_name} (timestamp, userid, changed_features) VALUES (?, ?, ?)",
                            (timestamp, userid, changed_features_json)
                        )
            else:
                conn.execute(f"DROP TABLE IF EXISTS sync_changes_{cls_name}")

            conn.commit()
        finally:
            conn.close()

    def gpkg_to_gdfjson(self, tmp_path: str, cls_name: str, read_gdf: bool = True) -> Dict[str, Any]:
        gdf = ""
        if read_gdf:
            gdf = gpd.read_file(tmp_path, layer=cls_name)

            if gdf is not None and not gdf.empty:
                gdf = gdf.reset_index()
                if 'index' in gdf.columns:
                    gdf = gdf.rename(columns={'index': self.row_guid})

                if self.row_guid not in gdf.columns:
                    self.drop_layer_completely(tmp_path, cls_name)
                    gdf.reset_index(drop=True, inplace=True)
                    gdf.index = gdf.index + 1
                    gdf.reset_index(inplace=True)
                    gdf.rename(columns={'index': self.row_guid}, inplace=True)

                    gdf.to_file(tmp_path, layer=cls_name, 
                                driver="GPKG", 
                                engine="pyogrio", 
                                mode='a', 
                                layer_options={'OVERWRITE': 'YES'})      
                else:
                    gdf.set_index(self.row_guid, inplace=True)
            else:
                print(f"Skipping layer '{cls_name}': GeoDataFrame is empty.")

        meta = self.read_gpkg_sync_tables_to_json(tmp_path, cls_name)
        return {
            "gdf": gdf,
            "metadata": meta.get('metadata'),
            "changes": meta.get('changes')
        }

    def drop_layer_completely(self, gpkg_path, layer_name):
        with sqlite3.connect(gpkg_path) as conn:
            conn.execute(f'DROP TABLE IF EXISTS "{layer_name}"')
            system_tables = ['gpkg_contents', 'gpkg_geometry_columns', 'gpkg_data_columns']
            for table in system_tables:
                check = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)).fetchone()
                if check:
                    conn.execute(f"DELETE FROM {table} WHERE table_name = ?", (layer_name,))
            conn.commit()
        print(f"Layer {layer_name} and its metadata fully removed.")

    def gdfjson_to_gpkg(self, gdf_json: Dict[str, Any], tmp_path: str, cls_name: str = "") -> str:
        gdf = gdf_json.get("gdf")

        if gdf is not None and not gdf.empty:
            if gdf.crs is None:
                gdf.set_crs(epsg=4326, inplace=True)
            self.drop_layer_completely(tmp_path, cls_name)
            gdf.to_file(tmp_path, layer=cls_name, driver="GPKG", engine="pyogrio", mode='a', layer_options={'OVERWRITE': 'YES'})
            self.write_sync_json_to_gpkg(gdf_json, tmp_path, cls_name)
        else:
            print(f"Skipping layer '{cls_name}': GeoDataFrame is empty.")
        
        return tmp_path

    def add_changed_features_to_gpkg(self, file_path: str, cls_name: str, comparison: Dict[str, Any], userid: str) -> str:
        changed_features = comparison.get('changed_features', [])
        
        if not changed_features:
            return False

        result_json = {
            'changes': {},
        }

        current_timestamp = datetime.now(timezone.utc).isoformat()
        changed_features_json = json.dumps(changed_features)

        try:
            with sqlite3.connect(file_path) as conn:
                conn.execute(f"""
                    CREATE TABLE IF NOT EXISTS sync_changes_{cls_name} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        userid TEXT NOT NULL,
                        changed_features TEXT NOT NULL
                    )
                """)
                
                conn.execute(
                    f"INSERT INTO sync_changes_{cls_name} (timestamp, userid, changed_features) VALUES (?, ?, ?)",
                    (current_timestamp, userid, changed_features_json)
                )
                
                conn.execute(f"""
                    CREATE TABLE IF NOT EXISTS sync_metadata_{cls_name} (
                        key TEXT PRIMARY KEY,
                        value TEXT
                    )
                """)
                conn.execute(
                    f"INSERT OR REPLACE INTO sync_metadata_{cls_name} (key, value) VALUES ('download_time', ?)",
                    (current_timestamp,)
                )
                conn.commit()

            result_json['changes'][current_timestamp] = {
                'userid': userid,
                'changed_features': changed_features
            }
            return result_json
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return result_json
        
    def add_update_download_time_to_gpkg(self, temp_path: str, cls_name: str, custom_time: str = None):
        download_time = custom_time or datetime.now(timezone.utc).isoformat()
        try:
            conn = sqlite3.connect(temp_path)
            conn.execute(f"CREATE TABLE IF NOT EXISTS sync_metadata_{cls_name} (key TEXT PRIMARY KEY, value TEXT)")
            conn.execute(f"DELETE FROM sync_metadata_{cls_name}")
            conn.execute(
                f"INSERT OR REPLACE INTO sync_metadata_{cls_name} (key, value) VALUES (?, ?)", 
                ('download_time', download_time)
            )
            conn.commit()
            conn.close()
            return temp_path
        except Exception as e:
            print(f"Failed to set download time in GPKG: {e}")
            return ""

    def add_update_download_time(self, geojson_data):
        current_time = datetime.now(timezone.utc).isoformat()
        if 'metadata' not in geojson_data:
            geojson_data['metadata'] = {}
        geojson_data['metadata']['download_time'] = current_time
        return geojson_data
      
    def extract_download_time_from_gpkg(self, file_path: str, cls_name: str) -> datetime:
        download_time_str = None
        try:
            with sqlite3.connect(file_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    f"SELECT value FROM sync_metadata_{cls_name} WHERE key = 'download_time'"
                )
                row = cursor.fetchone()
                if row:
                    download_time_str = row['value']
        except sqlite3.OperationalError:
            pass

        if download_time_str:
            dt = self.convert_download_time(download_time_str)
            if dt:
                return dt
        return None

    def get_geometry_hash(self, feature: Dict[str, Any]) -> str:
        geometry = feature.get('geometry')
        if not geometry:
            return "no_geometry"

        try:
            if hasattr(geometry, 'wkb'):
                geom_data = geometry.wkb
            elif isinstance(geometry, (bytes, bytearray)):
                geom_data = geometry
            else:
                geom_data = str(geometry).encode('utf-8')
            return hashlib.sha256(geom_data).hexdigest()
        except Exception:
            return "geometry_error"
        
    def get_properties_values(self, row: pd.Series, 
                            exclude_fields: List[str] = None) -> Dict[str, Any]:
        row_dict = row.to_dict()
        attribute_values = {
            k: v for k, v in row_dict.items() 
            if k not in exclude_fields
        }
        return attribute_values 

    def get_properties_hash(self, row: pd.Series, 
                            exclude_fields: List[str] = None) -> str:
        attribute_values = self.get_properties_values(row, exclude_fields)
        feature_str = json.dumps(attribute_values, sort_keys=True, separators=(',', ':'), default=str)
        return hashlib.sha256(feature_str.encode('utf-8')).hexdigest()

    def sort_by_date_keys(self, data_dict, reverse=False):
        return sorted(data_dict.items(), 
                    key=lambda x: self.convert_download_time(x[0]), 
                    reverse=reverse)
    
    def redo_conflict(self, gpkg_path: str, cls_name: str, conflicts_list: List[Dict[str, Any]]):
        conn = sqlite3.connect(gpkg_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT column_name 
                FROM gpkg_geometry_columns 
                WHERE table_name = ?
            """, (cls_name,))
            result = cursor.fetchone()
            real_geom_col = result[0] if result else "geom" 

            for conflict in conflicts_list:
                fid = conflict.get(self.row_guid) 
                if not fid: continue

                update_fields = []
                update_values = []

                properties = conflict.get('properties', {})
                for field_name, detail in properties.items():
                    server_val = detail.get('conflict_value')
                    update_fields.append(f"\"{field_name}\" = ?") 
                    update_values.append(server_val)

                geometries = conflict.get('geometry', {})
                for json_geom_key, detail in geometries.items():
                    hex_value = detail.get('conflict_value')
                    if hex_value:
                        binary_geom = binascii.unhexlify(hex_value)
                        update_fields.append(f"\"{real_geom_col}\" = ?")
                        update_values.append(sqlite3.Binary(binary_geom))

                if update_fields:
                    update_values.append(fid)
                    sql = f"UPDATE \"{cls_name}\" SET {', '.join(update_fields)} WHERE {self.row_guid} = ?"
                    cursor.execute(sql, update_values)

            conn.commit()
            print(f"Resolved conflicts for {cls_name} using column '{real_geom_col}'")
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def reconstruct_to_time_sql(self, gpkg_path: str, cls_name: str, 
                                gdf_json: Dict[str, Any], 
                                download_time: Any) -> Dict[str, Any]:
        if download_time is None:
            download_time = datetime.now(timezone.utc)
        elif isinstance(download_time, str):
            download_time = self.convert_download_time(download_time)

        changed_actions = gdf_json.get('changes', {})
        red_changes = {}

        conn = sqlite3.connect(gpkg_path)
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT column_name FROM gpkg_geometry_columns WHERE table_name = ?", (cls_name,))
            res = cursor.fetchone()
            geom_col = res[0] if res else "geom"

            sorted_changes = self.sort_by_date_keys(changed_actions)

            for timestamp_str, change_group in sorted_changes:
                upload_time = self.convert_download_time(timestamp_str)
                userid = change_group.get('userid')
                changed_features = change_group.get('changed_features', [])

                is_red_area = upload_time > download_time

                for change in changed_features:
                    guid = change.get(self.row_guid)
                    change_type = change.get('change_type')
                    geom_diff = change.get('geometry', {})
                    prop_diff = change.get('properties', {})

                    if is_red_area:
                        if guid not in red_changes:
                            red_changes[guid] = {
                                'change_type': change_type,
                                'geometry': {},
                                'properties': {},
                                'timestamp': upload_time,
                                'userid': userid
                            }
                        for key, val in geom_diff.items():
                            red_changes[guid]['geometry'][key] = val
                        for key, val in prop_diff.items():
                            red_changes[guid]['properties'][key] = val
                    else:
                        if change_type == 'insert':
                            cols = [self.row_guid]
                            placeholders = ["?"]
                            vals = [guid]

                            for attr, detail in prop_diff.items():
                                cols.append(f'"{attr}"')
                                placeholders.append("?")
                                vals.append(detail.get('new_value'))

                            geom_hex = geom_diff.get('wkb', {}).get('new_value')
                            if geom_hex:
                                cols.append(f'"{geom_col}"')
                                placeholders.append("?")
                                vals.append(sqlite3.Binary(binascii.unhexlify(geom_hex)))

                            sql = f"INSERT OR REPLACE INTO \"{cls_name}\" ({', '.join(cols)}) VALUES ({', '.join(placeholders)})"
                            cursor.execute(sql, vals)

                        elif change_type == 'update':
                            update_parts = []
                            vals = []

                            for attr, detail in prop_diff.items():
                                update_parts.append(f'"{attr}" = ?')
                                vals.append(detail.get('new_value'))

                            geom_hex = geom_diff.get('wkb', {}).get('new_value')
                            if geom_hex:
                                update_parts.append(f'"{geom_col}" = ?')
                                vals.append(sqlite3.Binary(binascii.unhexlify(geom_hex)))

                            if update_parts:
                                vals.append(guid)
                                sql = f"UPDATE \"{cls_name}\" SET {', '.join(update_parts)} WHERE {self.row_guid} = ?"
                                cursor.execute(sql, vals)

                        elif change_type == 'delete':
                            sql = f"DELETE FROM \"{cls_name}\" WHERE {self.row_guid} = ?"
                            cursor.execute(sql, (guid,))

            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Error in SQL reconstruction: {e}")
            raise e
        finally:
            conn.close()

        return red_changes

    def reconstruct_to_time(self, gdf_json: Dict[str, Any], 
                                download_time: datetime) -> Tuple[gpd.GeoDataFrame, Dict[str, Any]]:
        if download_time is None:
            download_time = datetime.now(timezone.utc)
        elif isinstance(download_time, str):
            download_time = self.convert_download_time(download_time)

        changed_actions = gdf_json.get('changes', {})
        recon_gdf = gdf_json.get("gdf")

        if recon_gdf is not None:
            if self.row_guid in recon_gdf.columns:
                recon_gdf.set_index(self.row_guid, inplace=True)
        
        red_changes = {}
        sorted_changes = self.sort_by_date_keys(changed_actions)

        for timestamp_str, change_group in sorted_changes:
            upload_time = self.convert_download_time(timestamp_str)
            userid = change_group.get('userid')
            changed_features = change_group.get('changed_features', [])

            is_red_area = upload_time > download_time

            for change in changed_features:
                guid = change.get(self.row_guid)
                change_type = change.get('change_type')
                geom_diff = change.get('geometry', {})
                prop_diff = change.get('properties', {})

                if is_red_area:
                    if guid not in red_changes:
                        red_changes[guid] = {
                            'change_type': change_type,
                            'geometry': {},
                            'properties': {},
                            'timestamp': upload_time,
                            'userid': userid
                        }
                    for key, val in geom_diff.items():
                        red_changes[guid]['geometry'][key] = val
                    for key, val in prop_diff.items():
                        red_changes[guid]['properties'][key] = val
                elif recon_gdf is not None:
                    for prop_name in prop_diff.keys():
                        if prop_name not in recon_gdf.columns:
                            recon_gdf[prop_name] = None
                    
                    for geom_field in geom_diff.keys():
                        if geom_field not in ['wkb'] and geom_field not in recon_gdf.columns:
                            recon_gdf[geom_field] = None
                    
                    if change_type == 'insert':
                        new_props = {k: v.get('new_value') for k, v in prop_diff.items()}
                        geom_hex = geom_diff.get('wkb', {}).get('new_value')
                        
                        if geom_hex:
                            new_props['geometry'] = wkb.loads(geom_hex, hex=True)
                        else:
                            new_props['geometry'] = None
                        
                        new_row = pd.DataFrame([new_props], index=[guid])
                        recon_gdf = pd.concat([recon_gdf, new_row])

                    elif change_type == 'update':
                        if guid in recon_gdf.index:
                            for attr, detail in prop_diff.items():
                                recon_gdf.at[guid, attr] = detail.get('new_value')
                            if 'wkb' in geom_diff:
                                geom_hex = geom_diff.get('wkb', {}).get('new_value')
                                recon_gdf.at[guid, 'geometry'] = wkb.loads(geom_hex, hex=True)

                    elif change_type == 'delete':
                        if guid in recon_gdf.index:
                            recon_gdf.drop(guid, inplace=True)

        if recon_gdf is not None:
            recon_gdf.reset_index(inplace=True)
            recon_gdf.rename(columns={'index': self.row_guid}, inplace=True)
        
        return recon_gdf, red_changes

    def get_attribute_values(self, feature: Union[Dict[str, Any], pd.Series], 
                            exclude_fields: List[str] = None) -> Optional[Dict[str, Any]]:
        if exclude_fields is None:
            exclude_fields = []
        exclude_fields.append('geometry')
        attribute_values = {}

        if isinstance(feature, pd.Series):
            full_dict = feature.to_dict()
            for key, value in full_dict.items():
                if key not in exclude_fields:
                    attribute_values[key] = value
        elif isinstance(feature, dict):
            if 'properties' in feature and isinstance(feature['properties'], dict):
                for attribute, value in feature['properties'].items():
                    if attribute not in exclude_fields:
                        attribute_values[attribute] = value
            else:
                for key, value in feature.items():
                    if key not in ['properties', 'geometry', 'type'] and key not in exclude_fields:
                        attribute_values[key] = value
        return attribute_values

    def setup_client_side_triggers(self, gpkg_path: str, layer_name: str, userid: str):
        conn = sqlite3.connect(gpkg_path)
        try:
            conn.execute(f"DROP TRIGGER IF EXISTS trg_track_insert_{layer_name}")
            conn.execute(f"DROP TRIGGER IF EXISTS trg_track_update_{layer_name}")
            conn.execute(f"DROP TRIGGER IF EXISTS trg_track_delete_{layer_name}")
            conn.execute(f"DROP TABLE IF EXISTS sync_changes_{layer_name}")

            def safe_ident(name):
                return name.replace('"', '""')
    
            cursor = conn.execute(f"PRAGMA table_info({layer_name})")
            table_info = cursor.fetchall()
            geom_col = next((row[1] for row in table_info if row[1].lower() in ['geom', 'geometry', 'shape']), 'geom')
            columns = [row[1] for row in table_info if row[1].lower() not in ['fid', geom_col.lower()]]

            update_parts = []
            for col in columns:
                col_ident = safe_ident(col)
                part = f"CASE WHEN OLD.\"{col_ident}\" IS NOT NEW.\"{col_ident}\" THEN json_object('{col}', json_object('old_value', OLD.\"{col_ident}\", 'new_value', NEW.\"{col_ident}\")) ELSE json_object() END"
                update_parts.append(part)
            
            update_props_sql = "json_object()"
            for part in update_parts:
                update_props_sql = f"json_patch({update_props_sql}, {part})"
            
            insert_props_json = ", ".join([
                f"'{col}', json_object('new_value', NEW.\"{safe_ident(col)}\")"
                for col in columns
            ])

            conn.execute(f"""
                CREATE TABLE IF NOT EXISTS sync_changes_{layer_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%f+00:00', 'now')),
                    userid TEXT,
                    changed_features TEXT
                )
            """)

            conn.execute(f"""
            CREATE TRIGGER IF NOT EXISTS trg_track_insert_{layer_name}
            AFTER INSERT ON "{layer_name}"
            BEGIN
                INSERT INTO sync_changes_{layer_name} (userid, changed_features)
                VALUES ('{userid}', json_array(json_object(
                    'fid', NEW.fid,
                    'change_type', 'insert',
                    'geometry', json_object('wkb', json_object('new_value', hex(NEW."{geom_col}"))),
                    'properties', json_object({insert_props_json})
                )));
            END;
            """)

            conn.execute(f"""
            CREATE TRIGGER IF NOT EXISTS trg_track_update_{layer_name}
            AFTER UPDATE ON "{layer_name}"
            BEGIN
                INSERT INTO sync_changes_{layer_name} (userid, changed_features)
                VALUES ('{userid}', json_array(json_object(
                    'fid', OLD.fid,
                    'change_type', 'update',
                    'geometry', CASE WHEN OLD."{geom_col}" IS NOT NEW."{geom_col}" THEN json_object('wkb',json_object('old_value', hex(OLD."{geom_col}"), 'new_value', hex(NEW."{geom_col}"))) ELSE json_object() END,
                    'properties', {update_props_sql}
                )));
            END;
            """)

            conn.execute(f"""
            CREATE TRIGGER IF NOT EXISTS trg_track_delete_{layer_name}
            AFTER DELETE ON "{layer_name}"
            BEGIN
                INSERT INTO sync_changes_{layer_name} (userid, changed_features)
                VALUES ('{userid}', json_array(json_object('fid', OLD.fid, 'change_type', 'delete')));
            END;
            """)

            conn.commit()
        finally:
            conn.close()

    def find_user_changes_with_conflicts(self, 
                                            user_changes: Dict[str, Any], 
                                            red_changes: Dict[str, Any]) -> Dict[str, Any]:
        result = {
            'changed_features': [],
            'conflicts': []
        }

        for timestamp in sorted(user_changes.keys()):
            payload = user_changes[timestamp]
            userid = payload.get('userid')
            actual_features = payload.get('changed_features', [])

            for change in actual_features:
                guid = change.get(self.row_guid)
                
                if guid not in red_changes:
                    result['changed_features'].append(change)
                    continue
                    
                red_entry = red_changes[guid]
                conflict_details = {
                    self.row_guid: guid,
                    'change_type': change.get('change_type'),
                    'geometry': {},
                    'properties': {}
                }

                user_props = change.get('properties', {})
                red_props = red_entry.get('properties', {})

                for user_key, user_val in user_props.items():
                    if user_key in red_props and user_val is not None:
                        conflict_details['properties'][user_key] = {
                            'current_value': user_val.get('new_value'),
                            'conflict_value': red_props[user_key].get('new_value'),
                            'conflict_type': red_entry['change_type'],
                            'conflict_time': red_entry.get('timestamp'),
                            'conflict_user': red_entry.get('userid')
                        }

                user_geoms = change.get('geometry', {})
                red_geoms = red_entry.get('geometry', {})

                for user_key, user_val in user_geoms.items():
                    if user_key in red_geoms and user_val is not None:
                        conflict_details['geometry'][user_key] = {
                            'current_value': user_val.get('new_value'),
                            'conflict_value': red_geoms[user_key].get('new_value'),
                            'conflict_type': red_entry['change_type'],
                            'conflict_time': red_entry.get('timestamp'),
                            'conflict_user': red_entry.get('userid')
                        }

                if conflict_details['properties'] or conflict_details['geometry']:
                    result['conflicts'].append(conflict_details)
                else:
                    result['changed_features'].append(change)

        return result
    
    def convert_to_list_structure(self, timestamp, user_id, red_list_features: dict) -> dict:
        changed_structure = {"changes": {}}
        converted_list = []
        
        for fid, change_data in red_list_features.items():
            item = change_data.copy()
            item['fid'] = fid
            item.pop('timestamp', None)
            item.pop('userid', None)
            converted_list.append(item)

        changed_structure["changes"][timestamp] = {
            'userid': user_id,
            'changed_features': converted_list
        }
        return changed_structure

    def find_changes_with_conflicts(self, 
                                    downloaded_features: gpd.GeoDataFrame,
                                    new_features: gpd.GeoDataFrame, 
                                    red_changes: Dict[str, Any]) -> Dict[str, Any]:
        result = {
            'unchanged_features': [],
            'changed_features': [],
            'conflicts': []
        }
        
        exclude_fields = self.exclude_fields
        old_df = downloaded_features.set_index(self.row_guid) if self.row_guid in downloaded_features.columns else downloaded_features
        new_df = new_features.set_index(self.row_guid) if self.row_guid in new_features.columns else new_features

        old_guids = set(old_df.index)
        new_guids = set(new_df.index)
        all_guids = old_guids | new_guids

        for guid in all_guids:
            if guid in old_guids and guid in new_guids:
                old_row = old_df.loc[guid]
                new_row = new_df.loc[guid]
                
                old_prop_hash = self.get_properties_hash(old_row, exclude_fields)
                new_prop_hash = self.get_properties_hash(new_row, exclude_fields)
                
                old_geom_wkb = old_row.geometry.wkb if old_row.geometry else None
                new_geom_wkb = new_row.geometry.wkb if new_row.geometry else None
                
                if old_prop_hash == new_prop_hash and old_geom_wkb == new_geom_wkb:
                    result['unchanged_features'].append(guid)
                    continue

                change_details = {self.row_guid: guid, 'change_type': 'update', 'geometry': {}, 'properties': {}}
                conflict_details = {self.row_guid: guid, 'change_type': 'update', 'geometry': {}, 'properties': {}}

                if old_prop_hash != new_prop_hash:
                    old_props = self.get_attribute_values(old_row, exclude_fields)
                    new_props = self.get_attribute_values(new_row, exclude_fields)
                    
                    for key in set(old_props.keys()) | set(new_props.keys()):
                        if old_props.get(key) != new_props.get(key):
                            if guid in red_changes:
                                red_entry = red_changes[guid]
                                if red_entry['change_type'] == 'delete' or key in red_entry['properties']:
                                    conflict_details['properties'][key] = {
                                        'current_value': new_props.get(key),
                                        'conflict_value': red_entry['properties'].get(key, {}).get('new_value', '-'),
                                        'conflict_type': red_entry['change_type'],
                                        'conflict_time': red_entry.get('timestamp'),
                                        'conflict_user': red_entry.get('userid')
                                    }
                                    continue
                            
                            change_details['properties'][key] = {
                                'old_value': old_props.get(key),
                                'new_value': new_props.get(key)
                            }

                if old_geom_wkb != new_geom_wkb:
                    if guid in red_changes and red_changes[guid].get('geometry'):
                        conflict_details['geometry']['wkb'] = {
                            'current_value': new_row.geometry.wkb_hex,
                            'conflict_value': red_changes[guid]['geometry'].get('wkb', {}).get('new_value', 'Modified'),
                            'conflict_type': red_changes[guid]['change_type'],
                            'conflict_time': red_changes[guid].get('timestamp'),
                            'conflict_user': red_changes[guid].get('userid')
                        }
                    else:
                        change_details['geometry']['wkb'] = {
                            'old_value': old_row.geometry.wkb_hex,
                            'new_value': new_row.geometry.wkb_hex
                        }

                if change_details['properties'] or change_details['geometry']:
                    result['changed_features'].append(change_details)
                if conflict_details['properties'] or conflict_details['geometry']:
                    result['conflicts'].append(conflict_details)

            elif guid in new_guids:
                if guid not in red_changes:
                    new_row = new_df.loc[guid]
                    change_details = {
                        self.row_guid: guid, 
                        'change_type': 'insert',
                        'properties': {k: {'new_value': v} for k, v in self.get_attribute_values(new_row, exclude_fields).items()},
                        'geometry': {'wkb': {'new_value': new_row.geometry.wkb_hex}}
                    }
                    result['changed_features'].append(change_details)

            elif guid in old_guids:
                if guid not in red_changes:
                    result['changed_features'].append({self.row_guid: guid, 'change_type': 'delete'})
                else:
                    result['conflicts'].append({
                        self.row_guid: guid,
                        'change_type': 'delete_conflict',
                        'properties': {'state': {'current_value': 'deleted', 'conflict_value': 'modified_by_other'}}
                    })

        return result

    def resolve_recursive_changes(self, 
                                previous_result: Dict[str, Any], 
                                red_changes: Dict[str, Any]) -> Dict[str, Any]:
        final_result = {
            'unchanged_features': previous_result.get('unchanged_features', []),
            'changed_features': [],
            'conflicts': previous_result.get('conflicts', []) 
        }

        for change in previous_result.get('changed_features', []):
            row_guid = change[self.row_guid]
            
            if row_guid not in red_changes:
                final_result['changed_features'].append(change)
                continue

            red_change = red_changes[row_guid]
            conflict_details = {
                self.row_guid: row_guid,
                'change_type': change.get('change_type'),
                'geometry': {},
                'properties': {}
            }

            if red_change.get('change_type') == "delete":
                conflict_details['geometry']['type'] = {
                    'current_value': change.get('geometry', {}).get('type', {}).get('new_value', 'unknown'),
                    'conflict_value': "-",
                    'conflict_type': "delete",
                    'conflict_time': red_change.get('timestamp'),
                    'conflict_user': red_change.get('userid')
                }
                final_result['conflicts'].append(conflict_details)
                continue 

            change_props = change.get('properties', {})
            red_props = red_change.get('properties', {})
            
            for key in list(change_props.keys()):
                if key in red_props:
                    conflict_details['properties'][key] = {
                        'current_value': change_props[key].get('new_value'),
                        'conflict_value': red_props[key].get('new_value'),
                        'conflict_type': red_change.get('change_type'),
                        'conflict_time': red_change.get('timestamp'),
                        'conflict_user': red_change.get('userid')
                    }
                    del change['properties'][key]

            if change.get('geometry') and red_change.get('geometry'):
                for geo_key in ['type', 'coordinates']:
                    if geo_key in change['geometry'] and geo_key in red_change['geometry']:
                        conflict_details['geometry'][geo_key] = {
                            'current_value': change['geometry'][geo_key].get('new_value'),
                            'conflict_value': red_change['geometry'][geo_key].get('new_value'),
                            'conflict_type': red_change.get('change_type'),
                            'conflict_time': red_change.get('timestamp'),
                            'conflict_user': red_change.get('userid')
                        }
                change['geometry'] = {}

            if conflict_details['properties'] or conflict_details['geometry']:
                final_result['conflicts'].append(conflict_details)
            
            if change.get('properties') or change.get('geometry'):
                final_result['changed_features'].append(change)

        return final_result
    
    def get_gpkg_feature_classes(self, file_path):
        if not os.path.exists(file_path):
            print(f"Error: File not found at {file_path}")
            return []

        feature_classes = []
        try:
            conn = sqlite3.connect(file_path)
            cursor = conn.cursor()
            query = "SELECT table_name FROM gpkg_contents WHERE data_type = 'features';"
            cursor.execute(query)
            rows = cursor.fetchall()
            feature_classes = [row[0] for row in rows]
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
        finally:
            if conn:
                conn.close()
        return feature_classes
