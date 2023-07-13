import obspython as obs

import os
import threading
import json
import uvicorn
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


auto_start = False
source_name = ""
server_port = 8000
# ------------------------------------------------------------
file_path = os.path.dirname(__file__)
sys.path.insert(0, file_path)
sys.stdout.isatty = lambda: False

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

content = "wait for content."

@app.get("/")
async def root():
    return content

@app.post("/input")
async def input_data(data: str):
    global content
    data = json.loads(data)
    # print(data)
    # {"blueRingCount":0,"cbCount":0,"cbFfj":0,"count":0,"ffjCount":0,"grandeBlueRingCount":0,"grandeCount":0,"grandeFfjCount":0,"grandeRedRingCount":0,"grandeUnHitCount":0,"grandeWhiteRingCount":0,"historyHitArray":[],"noBlueChestCount":0,"redRingCount":0,"unHitCount":0,"whiteRingCount":0}
    template = """大巴蓝箱：{0:<5}落空：{1:<5}    金砖：{2:<5}
白戒：{3:<5}    蓝戒：{4:<5}    红戒：{5:<5}
蓝箱率：{6:<5}%
距离上次出金打了 {7:<5} 蓝。
"""
    
    if int(data["count"])+int(data["noBlueChestCount"]) != 0:
        blue_percent = str(int(data["count"])/(int(data["count"])+int(data["noBlueChestCount"]))*100)[:4]
        # print(blue_percent)
    else:
        blue_percent = "N/A"
    content = template.format(data["count"], data["noBlueChestCount"], data["ffjCount"], data["whiteRingCount"], data["blueRingCount"], data["redRingCount"], blue_percent, data["unHitCount"])
    update_text()
    return {"message": f"ok"}


class Server(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True
        config = uvicorn.Config("gbf:app", port=server_port, access_log=False, log_level="critical")
        self.server = uvicorn.Server(config=config)
        self.started = False

    def run(self):
        self.started = True
        self.server.run()

    def stop(self):
        self.server.should_exit = True
        self.join()
        self.started = False


server = None

def start_server(props=None, prop=None):
    global server
    if server is None or not server.started:
        print("监听启动.")
        server = Server()
        server.start()

def stop_server(props=None, prop=None):
    global server
    if server is not None and server.started:
        print("监听关闭.")
        server.stop()


def update_text():
    global url
    global source_name

    source = obs.obs_get_source_by_name(source_name)
    if source is not None:
        settings = obs.obs_data_create()
        obs.obs_data_set_string(settings, "text", content)
        obs.obs_source_update(source, settings)
        obs.obs_data_release(settings)
        obs.obs_source_release(source)


# ------------------------------------------------------------
def script_load(settings):
    global auto_start
    global server_port
    global source_name 
    auto_start = obs.obs_data_get_bool(settings, "auto_start")
    server_port = obs.obs_data_get_int(settings, "server_port")
    source_name = obs.obs_data_get_string(settings, "source")
    if auto_start:
        start_server()


def script_description():
    return "TODO\n\nBy Kl1nge5"


def script_update(settings):
    global auto_start
    global source_name
    global server_port

    auto_start = obs.obs_data_get_bool(settings, "auto_start")
    server_port = obs.obs_data_get_int(settings, "server_port")
    source_name = obs.obs_data_get_string(settings, "source")



def script_defaults(settings):
    obs.obs_data_set_default_bool(settings, "auto_start", False)
    obs.obs_data_set_default_int(settings, "server_port", 8000)
    

def script_properties():
    props = obs.obs_properties_create()

    obs.obs_properties_add_int(props, "server_port", "监听端口", 1000, 65535, 1)

    p = obs.obs_properties_add_list(
        props,
        "source",
        "Text Source",
        obs.OBS_COMBO_TYPE_EDITABLE,
        obs.OBS_COMBO_FORMAT_STRING,
    )
    sources = obs.obs_enum_sources()
    if sources is not None:
        for source in sources:
            source_id = obs.obs_source_get_unversioned_id(source)
            if source_id == "text_gdiplus" or source_id == "text_ft2_source":
                name = obs.obs_source_get_name(source)
                obs.obs_property_list_add_string(p, name, name)

        obs.source_list_release(sources)

    obs.obs_properties_add_bool(props, "auto_start", "自启动")
    obs.obs_properties_add_button(props, "start_button", "启动监听", start_server)
    obs.obs_properties_add_button(props, "stop_button", "结束监听", stop_server)
    return props


def script_unload():
    stop_server()