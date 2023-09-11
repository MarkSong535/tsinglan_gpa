from fastapi import BackgroundTasks, FastAPI, Header
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from pydantic import BaseModel
import request
import manipulate
import fetch
import json
from typing import Annotated
from ua_parser import user_agent_parser
import pprint
import config

HOST = config.settings["server_host"]
pp = pprint.PrettyPrinter(indent=4)

app = FastAPI(docs_url="/documentation", redoc_url=None)


class new(BaseModel):
    username: str
    password: str
    sid: int
    per: bool


class uuid(BaseModel):
    uuid: str


class fetch_st(BaseModel):
    password: str
    uuid: str


@app.get("/")
async def root(
    host: Annotated[str | None, Header()] = None,
    accept_language: Annotated[str | None, Header()] = None,
):
    if host != HOST:
        return RedirectResponse("http://" + HOST)
    if "zh" in accept_language:
        return RedirectResponse("/zh/")
    return RedirectResponse("/en/")


@app.get("/zh/")
async def root(host: Annotated[str | None, Header()] = None):
    if host != HOST:
        return RedirectResponse("http://" + HOST)
    f = open("index.html", "r")
    data = f.read()
    return HTMLResponse(content=data, status_code=200)


@app.get("/en/")
async def root(host: Annotated[str | None, Header()] = None):
    if host != HOST:
        return RedirectResponse("http://" + HOST)
    f = open("index_en.html", "r")
    data = f.read()
    return HTMLResponse(content=data, status_code=200)


@app.get("/assets/bootstrap/css/bootstrap.min.css")
async def root(host: Annotated[str | None, Header()] = None):
    if host != HOST:
        return RedirectResponse("http://" + HOST)
    return FileResponse("html_assets/bootstrap.min.css")


@app.get("/assets/bootstrap/css/bootstrap.min.js")
async def root(host: Annotated[str | None, Header()] = None):
    if host != HOST:
        return RedirectResponse("http://" + HOST)
    return FileResponse("html_assets/bootstrap.min.js")


@app.get("/assets/css/Login-Form-Basic-icons.css")
async def root(host: Annotated[str | None, Header()] = None):
    if host != HOST:
        return RedirectResponse("http://" + HOST)
    return FileResponse("html_assets/Login-Form-Basic-icons.css")


@app.get("/assets/js/jquery.min.js")
async def root(host: Annotated[str | None, Header()] = None):
    if host != HOST:
        return RedirectResponse("http://" + HOST)
    return FileResponse("html_assets/jquery.min.js")


@app.get("/assets/bootstrap/js/bootstrap.min.js")
async def root(host: Annotated[str | None, Header()] = None):
    if host != HOST:
        return RedirectResponse("http://" + HOST)
    return FileResponse("html_assets/styles.css")


@app.get("/tsinglan.png")
async def root(host: Annotated[str | None, Header()] = None):
    if host != HOST:
        return RedirectResponse("http://" + HOST)
    return FileResponse("ico/tsinglan.png")


@app.get("/favicon.ico")
async def root(host: Annotated[str | None, Header()] = None):
    if host != HOST:
        return RedirectResponse("http://" + HOST)
    return FileResponse("ico/favicon.ico")


@app.get("/favicon-32x32.png")
async def root(host: Annotated[str | None, Header()] = None):
    if host != HOST:
        return RedirectResponse("http://" + HOST)
    return FileResponse("ico/favicon-32x32.png")


@app.get("/favicon-16x16.png")
async def root(host: Annotated[str | None, Header()] = None):
    if host != HOST:
        return RedirectResponse("http://" + HOST)
    return FileResponse("ico/favicon-16x16.png")


@app.get("/apple-touch-icon.png")
async def root(host: Annotated[str | None, Header()] = None):
    if host != HOST:
        return RedirectResponse("http://" + HOST)
    return FileResponse("ico/apple-touch-icon.png")


@app.get("/android-chrome-512x512.png")
async def root(host: Annotated[str | None, Header()] = None):
    if host != HOST:
        return RedirectResponse("http://" + HOST)
    return FileResponse("ico/android-chrome-512x512.png")


@app.get("/android-chrome-192x192.png")
async def root(host: Annotated[str | None, Header()] = None):
    if host != HOST:
        return RedirectResponse("http://" + HOST)
    return FileResponse("ico/android-chrome-192x192.png")


@app.get("/site.webmanifest")
async def root(host: Annotated[str | None, Header()] = None):
    if host != HOST:
        return RedirectResponse("http://" + HOST)
    return FileResponse("ico/site.webmanifest")


@app.get("/terms.html")
async def root(host: Annotated[str | None, Header()] = None):
    if host != HOST:
        return RedirectResponse("http://" + HOST)
    return FileResponse("terms.html")


@app.get("/data.json")
async def root(host: Annotated[str | None, Header()] = None):
    if host != HOST:
        return RedirectResponse("http://" + HOST)
    f = open("data.json")
    s = json.load(f)
    f.close()
    return s


@app.post("/new/")
async def create_item(
    new_itm: new,
    user_agent: Annotated[str | None, Header()] = None,
    host: Annotated[str | None, Header()] = None,
):
    if host != HOST:
        return RedirectResponse("http://" + HOST)
    u_brand = user_agent_parser.Parse(user_agent)["device"]["brand"]
    if u_brand != "Spider" and u_brand != "Other" and u_brand != "" and u_brand != None:
        r_data = {}
        r_data["state"] = "success"
        r_data["uuid"] = request.call(
            new_itm.username, new_itm.password, new_itm.sid, new_itm.per, user_agent
        )
    else:
        r_data = {}
        r_data["state"] = "false ua"
        r_data["uuid"] = "false ua"
    return r_data


@app.post("/calculate/")
async def create_item(
    new_itm: uuid,
    background_tasks: BackgroundTasks,
    user_agent: Annotated[str | None, Header()] = None,
    host: Annotated[str | None, Header()] = None,
):
    if host != HOST:
        return RedirectResponse("http://" + HOST)
    u_brand = user_agent_parser.Parse(user_agent)["device"]["brand"]
    if u_brand != "Spider" and u_brand != "Other" and u_brand != "" and u_brand != None:
        background_tasks.add_task(manipulate.mancall, new_itm.uuid, user_agent)
        r_data = {}
        r_data["state"] = "success"
    else:
        r_data = {}
        r_data["state"] = "false ua"
    return r_data


@app.post("/fetch/")
async def create_item(
    new_itm: fetch_st,
    user_agent: Annotated[str | None, Header()] = None,
    host: Annotated[str | None, Header()] = None,
):
    if host != HOST:
        return RedirectResponse("http://" + HOST)
    u_brand = user_agent_parser.Parse(user_agent)["device"]["brand"]
    if u_brand != "Spider" and u_brand != "Other" and u_brand != "" and u_brand != None:
        r_data = fetch.fetch(new_itm.uuid, new_itm.password, user_agent)
    else:
        r_data = {}
        r_data["err"] = True
        r_data[
            "error_en"
        ] = "Illegal Access. If you believe you have been marked as illegal access by mistake, please contact the administrator."
        r_data["error_zh"] = "非法访问。如果您认为您被错误地标记为非法访问，请联系管理员。"
        r_data["rstatus"] = True
        r_data["status"] = True
    return r_data


@app.get("/ua_test/")
async def read_items(
    user_agent: Annotated[str | None, Header()] = None,
    host: Annotated[str | None, Header()] = None,
):
    if host != HOST:
        return RedirectResponse("http://" + HOST)
    parsed_string = user_agent_parser.Parse(user_agent)["device"]["brand"] == "Spider"
    return parsed_string


@app.get("/hn/")
async def read_items(host: Annotated[str | None, Header()] = None):
    print(host)
    return {"Host": host}
