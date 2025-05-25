from fastapi import FastAPI
from contextlib import asynccontextmanager
import httpx
import asyncio
import subprocess
import os

from code_docs_loaders.settings import *

latest_tag_file = "code_docs_loaders/code_loader/latest_release.txt"


async def check_and_run_main():
    while True:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(API_URL)
                response.raise_for_status()
                release = response.json()
                latest_tag = release["tag_name"]

                if os.path.exists(latest_tag_file):
                    with open(latest_tag_file, "r") as f:
                        saved_tag = f.read().strip()
                else:
                    saved_tag = None

                if latest_tag != saved_tag:
                    print(f"[info] {latest_tag} - new release detected")
                    with open(latest_tag_file, "w") as f:
                        f.write(latest_tag)
                    run_main_py()
                else:
                    print(f"[info] No new release found {latest_tag}")

        except Exception as e:
            print(f"[error] Error checking release: {e}")

        await asyncio.sleep(3600)


def run_main_py():
    print("[info] Starting main.py")
    result = subprocess.run(["python", MAIN_PY_PATH], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("[error] Errors:", result.stderr)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(check_and_run_main())
    yield
    task.cancel()


app = FastAPI(lifespan=lifespan)
