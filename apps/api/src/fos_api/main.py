from os import getenv

from fastapi import FastAPI

from fos_api import __version__

app = FastAPI(title="FOS API")


@app.get("/health")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "version": getenv("FOS_VERSION", __version__),
        "packs": [],
    }


def main() -> None:
    import uvicorn

    uvicorn.run("fos_api.main:app", host="0.0.0.0", port=8000, reload=True)
