import json
from pathlib import Path

from aiohttp import web

import sherlock_runner
from auth import validate_init_data
from config import BOT_TOKEN

WEBAPP_DIR = Path(__file__).parent / "webapp"


async def index(_: web.Request) -> web.FileResponse:
    return web.FileResponse(WEBAPP_DIR / "index.html")


async def health(_: web.Request) -> web.Response:
    return web.Response(text="ok")


async def search_stream(request: web.Request) -> web.StreamResponse:
    """SSE: natijalarni topilishi bilan mini app'ga yuboradi.
    GET /api/search?username=...&initData=..."""
    user = validate_init_data(request.query.get("initData", ""), BOT_TOKEN)
    if not user:
        raise web.HTTPUnauthorized(text="Telegram orqali oching")

    username = request.query.get("username", "").strip().lstrip("@")
    if not sherlock_runner.is_valid_username(username):
        raise web.HTTPBadRequest(text="Username noto'g'ri")

    resp = web.StreamResponse(headers={
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",
    })
    await resp.prepare(request)

    async def send(event: str, data: dict):
        await resp.write(f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n".encode())

    count = 0
    try:
        async for item in sherlock_runner.search(username, int(user["id"])):
            count += 1
            await send("found", item)
        await send("done", {"count": count})
    except sherlock_runner.SearchBusy as e:
        await send("fail", {"error": str(e)})
    except ConnectionResetError:
        pass  # foydalanuvchi mini app'ni yopdi — sherlock jarayoni to'xtatiladi
    except Exception as e:  # noqa: BLE001
        await send("fail", {"error": str(e)})
    return resp


def create_app() -> web.Application:
    app = web.Application()
    app.router.add_get("/", index)
    app.router.add_get("/health", health)
    app.router.add_get("/api/search", search_stream)
    app.router.add_static("/static", WEBAPP_DIR)
    return app
