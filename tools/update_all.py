import asyncio
import pathlib
import sys
from typing import Any, Dict

async def run_cmd(label: str, cmd: str, work_dir: pathlib.Path) -> int | None:
    """Verilen komutu verilen dizinde çalıştırır"""

    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=work_dir
    )
    msg = await proc.stdout.readline()
    while msg != b"":
        msg = await proc.stdout.readline()
        print(f"{label} -- {msg.decode('utf-8')}")

    return await proc.wait()
        
async def main():
    """Main Function"""
    # Tüm lock dosyaları temizlenir.
    cmd = "find . -name '*.lock' -exec rm {} \\;"
    
    delete_result = await run_cmd("Delete lock files", cmd, pathlib.Path("."))

    cmd = ". .venv/bin/activate && poetry update"
    lib_list = [
        "core", "test", "app", "manage", "sso", "gateway", "application", "spatial"
    ]
    app_list = [
        "application", "gateway", "spatial", "manage", "mock_app", "service", "sso"
    ]
    # Kütüphaneler sırayla çalıştırılır
    for lib in lib_list:
        lib_path = pathlib.Path(".").joinpath("libs", lib)
        ret_val = await run_cmd(lib, cmd, lib_path.absolute())
        if ret_val != 0:
            print("Uygulamada hata oluştu")
            sys.exit()
    
    # Uygulamalar paralel çalıştırılır
    result_list = await asyncio.gather(*[
        run_cmd(
            app,
            cmd,
            pathlib.Path(".").joinpath("apps", app)) for app in app_list
    ])
    
    app_result_list = list(zip(app_list, result_list))
    for app, result in app_result_list:
        print(f"{app} = {'Başarılı' if result == 0 else 'Hatalı'}")

asyncio.run(main())
