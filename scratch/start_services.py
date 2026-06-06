import subprocess
import os
import sys

apps = [
    {"name": "sso", "port": "33100", "module": "sso.main:app"},
    {"name": "manage", "port": "33101", "module": "manage.main:app"},
    {"name": "service", "port": "33102", "module": "service.main:app"},
    {"name": "application", "port": "33103", "module": "application.main:app"},
    {"name": "gateway", "port": "33104", "module": "gateway.main:app"},
    {"name": "messaging", "port": "33105", "module": "messaging.main:app"},
    {"name": "spatial", "port": "33107", "module": "spatial.main:app"},
    {"name": "desktop_mobile", "port": "33108", "module": "desktop_mobile.main:app"},
]

workspace = "/workspace"

for app in apps:
    name = app["name"]
    port = app["port"]
    module = app["module"]
    
    app_dir = f"{workspace}/apps/{name}"
    venv_python = f"{app_dir}/.venv/bin/python3"
    log_file = f"{app_dir}/uvicorn.log"
    
    print(f"Starting {name} on port {port}...")
    
    env = os.environ.copy()
    env["PYTHONPATH"] = workspace
    env["MAPA_ENV"] = "DEVELOPMENT"
    
    cmd = [
        venv_python, "-u", "-m", "uvicorn", module,
        "--port", port,
        "--host", "0.0.0.0",
        "--reload"
    ]
    
    with open(log_file, "w") as log:
        subprocess.Popen(
            cmd,
            cwd=app_dir,
            env=env,
            stdout=log,
            stderr=log,
            preexec_fn=os.setsid if hasattr(os, "setsid") else None
        )

print("All services started in background.")
