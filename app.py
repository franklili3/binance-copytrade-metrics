import asyncio
import time
from typing import Optional, Dict, Any

from fastapi import FastAPI, Body, HTTPException
from filelock import FileLock, Timeout as LockTimeout

from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from twisted.internet.asyncioreactor import AsyncioSelectorReactor
from twisted.internet import asyncioreactor

try:
    asyncioreactor.install(AsyncioSelectorReactor())
except Exception:
    pass

app = FastAPI()

LOCK_PATH = "/tmp/spider.lock"
JOBDIR_PATH = "/tmp/scrapy-job"


def build_settings(extra: Optional[Dict[str, Any]] = None):
    settings = get_project_settings()
    settings.set("JOBDIR", JOBDIR_PATH, priority="cmdline")
    if extra:
        for key, value in extra.items():
            settings.set(key, value, priority="cmdline")
    return settings


async def run_spider(spider_name: str, **kwargs):
    runner = CrawlerRunner(build_settings(kwargs.pop("_settings_override_", None)))
    return await runner.crawl(spider_name, **kwargs)


@app.post("/invoke")
async def invoke(payload: Dict[str, Any] = Body(default={})):  # type: ignore[assignment]
    settings_override = payload.get("_settings_override_", {})
    max_seconds = int(payload.get("max_seconds", 0))

    lock = FileLock(LOCK_PATH)
    try:
        lock.acquire(timeout=1)
    except LockTimeout as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=409, detail="Previous run still in progress") from exc

    start = time.time()
    try:
        task = asyncio.create_task(
            run_spider("copy_trade", _settings_override_=settings_override)
        )
        while True:
            done, _ = await asyncio.wait({task}, timeout=0.5)
            if task in done:
                break
            if max_seconds and (time.time() - start) > max_seconds:
                raise HTTPException(
                    status_code=504, detail="Run exceeded max_seconds limit"
                )
        return {"status": "ok"}
    finally:
        try:
            lock.release()
        except Exception:
            pass


@app.get("/healthz")
async def healthz():
    return {"ok": True}
