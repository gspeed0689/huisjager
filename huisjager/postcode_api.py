from furl import furl
import requests
import pandas as pd
from shapely import from_wkt
from typing import Optional
from pprint import pprint

base_url = furl("https://api.pdok.nl/bzk/locatieserver/search/v3_1")

free_search = base_url / "free"
lookup_search = base_url / "lookup"
reverse_search = base_url / "reverse"
suggest_search = base_url / "suggest"


def search_postcode_huisnummer(postcode: str, 
                               huisnummer: int, 
                               toevoeging: Optional[str]=None):
    free_search_event = free_search
    free_search_event.args["q"] = f"{postcode} {huisnummer}"
    free_search_event.args["fq"] = f"postcode:{postcode}"
    free_search_event.args["rows"] = str(99)
    # print(free_search_event)
    r = requests.get(free_search_event)
    j = r.json()
    if "response" in j.keys():
        results = j["response"]["docs"]
        # pprint(results)
        # for result in results:
        #     pprint(result)
        type_postcode = [x for x in results if x["type"] == "postcode"]
        type_adres = [x for x in results if x["type"] == "adres"]
        if len(type_postcode) >= 1:
            postcode_centroid = type_postcode[0]["centroide_ll"]
        # else: 
        #     postcode_only_search = free_search
        #     postcode_only_search.args["q"] = postcode
        #     postcode_only_search.args["rows"] = 100
        #     postcode_only_request = requests.get(postcode_only_search)
        #     postcode_only_json = postcode_only_request.json()["response"]["docs"]
        #     print(postcode_only_json)
        #     type_postcode = [x for x in postcode_only_json if x["type"] == "postcode" and x["postcode"] == postcode]
        #     postcode_centroid = type_postcode[0]["centroide_ll"]
        # postcode_df = pd.DataFrame(type_postcode)
        adres_df = pd.DataFrame(type_adres)
        return (adres_df, from_wkt(postcode_centroid), j["response"]["docs"])