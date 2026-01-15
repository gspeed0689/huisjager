import requests
from furl import furl

woz_waarde_api = furl("https://api.kadaster.nl/lvwoz/wozwaardeloket-api/v1/wozwaarde/wozobjectnummer")
suggest_api = furl("https://api.kadaster.nl/lvwoz/wozwaardeloket-api/v1/suggest")

def get_wozobjectnummer(adres_object):
    stage_1_url = suggest_api
    stage_1_url.args["aotids"] = adres_object
    stage_1_r = requests.get(stage_1_url)
    stage_1_json = stage_1_r.json()
    # print(stage_1_json)
    if "docs" in stage_1_json.keys():
        stage_1_json = stage_1_json["docs"][0]
        wozobjectnummer = str(stage_1_json["wozobjectnummer"])
        return stage_1_json
    
def get_wozwaarde(wozobjectnummer):
        stage_2_url = woz_waarde_api
        stage_2_url = stage_2_url / str(wozobjectnummer)
        stage_2_r = requests.get(stage_2_url)
        stage_2_json = stage_2_r.json()
        return stage_2_json