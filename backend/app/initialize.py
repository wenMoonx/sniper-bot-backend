import subprocess

subprocess.call("echo Running script", shell=True)

subprocess.call("echo Running database setup", shell=True)
subprocess.call("cd ./app ; python db/database.py", shell=True)

subprocess.call("echo Running alembic", shell=True)
subprocess.call("cd ./app ; alembic upgrade head", shell=True)

subprocess.call("echo Start server", shell=True)
subprocess.call("uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --loop asyncio", shell=True)