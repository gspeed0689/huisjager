from postcode_api import search_postcode_huisnummer
from woz_api import get_wozobjectnummer
from woz_api import get_wozwaarde
from sqlalchemy import create_engine
from sqlalchemy import String, Text
from sqlalchemy import Integer, BigInteger
from sqlalchemy import Double
from sqlalchemy import Date
from sqlalchemy import select, insert
from sqlalchemy import ForeignKey
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import mapped_column, Mapped
from shapely import from_wkt
import pandas as pd
from typing import Optional, List, Any
from datetime import date, datetime
from hashlib import md5

class huisjager_base(DeclarativeBase):
    pass

class pdok_api_adres(huisjager_base):
    __tablename__ = "pdok_api_adres"
    pk_pdok_api_adres: Mapped[int] = mapped_column(Integer, primary_key=True)
    unique_id: Mapped[str] = mapped_column(String(40), unique=True)
    bron: Mapped[str] = mapped_column(Text)
    postcode: Mapped[str] = mapped_column(String(6))
    huisnummer: Mapped[int] = mapped_column(Integer)
    huisletter: Mapped[str] = mapped_column(String(3), nullable=True)
    huis_nlt: Mapped[str] = mapped_column(String(10))
    straatnaam: Mapped[str] = mapped_column(Text)
    buurtnaam: Mapped[str] = mapped_column(Text)
    wijknaam: Mapped[str] = mapped_column(Text)
    weergavenaam: Mapped[str] = mapped_column(Text)
    gemeentenaam: Mapped[str] = mapped_column(Text)
    woonplaatsnaam: Mapped[str] = mapped_column(Text)
    provincie_afkorting: Mapped[str] = mapped_column(String(2))
    adresseerbaarobject_id: Mapped[str] = mapped_column(Text)
    centroid_lat: Mapped[float] = mapped_column(Double)
    centroid_lon: Mapped[float] = mapped_column(Double)
    centroid_rd_x: Mapped[float] = mapped_column(Double)
    centroid_rd_y: Mapped[float] = mapped_column(Double)

class pdok_api_postcode(huisjager_base):
    __tablename__ = "pdok_api_postcode"
    pk_pdok_api_adres: Mapped[int] = mapped_column(Integer, primary_key=True)
    unique_id: Mapped[str] = mapped_column(String(40), unique=True)
    bron: Mapped[str] = mapped_column(Text)
    postcode: Mapped[str] = mapped_column(String(6))
    straatnaam: Mapped[str] = mapped_column(Text)
    gemeentenaam: Mapped[str] = mapped_column(Text)
    woonplaatsnaam: Mapped[str] = mapped_column(Text)
    provincie_afkorting: Mapped[str] = mapped_column(String(2))
    centroid_lat: Mapped[float] = mapped_column(Double)
    centroid_lon: Mapped[float] = mapped_column(Double)
    centroid_rd_x: Mapped[float] = mapped_column(Double)
    centroid_rd_y: Mapped[float] = mapped_column(Double)

class kadaster_koopsom(huisjager_base):
    __tablename__ = "kadaster_koopsom"
    pk_kadaster_koopsom: Mapped[int] = mapped_column(Integer, primary_key=True)
    unique_id: Mapped[str] = mapped_column(String(40), unique=True)
    koopsom: Mapped[int] = mapped_column(BigInteger)
    postcode: Mapped[str] = mapped_column(String(6))
    huisnummer: Mapped[str] = mapped_column(String(10))
    sale_date: Mapped[date] = mapped_column(Date)
    kadastral_grotte: Mapped[int] = mapped_column(Integer)

class funda_aanbod(huisjager_base):
    __tablename__ = "funda_aanbod"
    pk_funda_aangebood: Mapped[int] = mapped_column(Integer, primary_key=True)
    unique_id: Mapped[str] = mapped_column(String(40), unique=True)
    postcode: Mapped[str] = mapped_column(String(6))
    huisnummer: Mapped[str] = mapped_column(String(10))
    toevoeging: Mapped[str] = mapped_column(String(3), nullable=True)
    vraagprijs: Mapped[int] = mapped_column(BigInteger)
    huisgrotte: Mapped[int] = mapped_column(Integer)
    percelgrotte: Mapped[int] = mapped_column(Integer, nullable=True)
    kamerkount: Mapped[int] = mapped_column(Integer, nullable=True)
    energylabel: Mapped[str] = mapped_column(String(10), nullable=True)
    bouwjaar: Mapped[int] = mapped_column(Integer, nullable=True)
    aangebodesinds: Mapped[date] = mapped_column(Date, nullable=True)

class kadaster_woz_objectlookup_api(huisjager_base):
    __tablename__ = "kadaster_woz_api"
    pk_kadaster_woz_objlookup: Mapped[int] = mapped_column(Integer, primary_key=True)
    unique_id: Mapped[str] = mapped_column(String(40), unique=True)
    adresseerbaarobject_id: Mapped[str] = mapped_column(Text)
    wozobjectnummer: Mapped[str] = mapped_column(Text, unique=True)
    postcode: Mapped[str] = mapped_column(String(6))
    huisnummer: Mapped[int] = mapped_column(Integer)
    huisletter: Mapped[str] = mapped_column(String(3), nullable=True)

class kadaster_woz_object_metadata(huisjager_base):
    __tablename__ = "kadaster_woz_obj_metadata"
    pk_kadaster_woz_obj_metadata: Mapped[int] = mapped_column(Integer, primary_key=True)
    unique_id: Mapped[str] = mapped_column(String(40), unique=True)
    wozobjectnummer: Mapped[str] = mapped_column(Text, unique=True)
    postcode: Mapped[str] = mapped_column(String(6))
    huisnummer: Mapped[int] = mapped_column(Integer)
    huisletter: Mapped[str] = mapped_column(String(3), nullable=True)

class kadaster_woz_waarden(huisjager_base):
    __tablename__ = "kadaster_woz_waarden"
    pk_kadaster_woz_waarden: Mapped[int] = mapped_column(Integer, primary_key=True)
    unique_id: Mapped[str] = mapped_column(String(40), unique=True)
    fk_wozobjectnummer: Mapped[str] = mapped_column(ForeignKey("kadaster_woz_obj_metadata.wozobjectnummer"))
    peildatum: Mapped[date] = mapped_column(Date)
    waarde: Mapped[int] = mapped_column(BigInteger)

conn_string = "sqlite:///huisjager.db"
engine = create_engine(conn_string)

huisjager_base.metadata.create_all(engine)

def unique_hash(items: List[Any]):
    items = [str(x).encode("utf8") for x in items]
    hasher = md5()
    for item in items:
        hasher.update(item)
    return str(hasher.hexdigest())

def insert_api_adres(source_json):
    wgs84 = from_wkt(source_json["centroide_ll"])
    rdnew = from_wkt(source_json["centroide_rd"])
    huisletter = None
    # print(source_json)
    if "huisletter" in source_json.keys():
        huisletter = source_json["huisletter"]
    insert_values = dict(bron=source_json["bron"],
            postcode=source_json["postcode"],
            huisnummer=source_json["huisnummer"],
            huisletter=huisletter,
            huis_nlt=source_json["huis_nlt"],
            straatnaam=source_json["straatnaam"],
            buurtnaam=source_json["buurtnaam"],
            wijknaam=source_json["wijknaam"],
            weergavenaam=source_json["weergavenaam"],
            gemeentenaam=source_json["gemeentenaam"],
            woonplaatsnaam=source_json["woonplaatsnaam"],
            provincie_afkorting=source_json["provincieafkorting"],
            adresseerbaarobject_id=source_json["adresseerbaarobject_id"],
            centroid_lat=wgs84.y,
            centroid_lon=wgs84.x,
            centroid_rd_x=rdnew.x,
            centroid_rd_y=rdnew.y)
    unique_id = unique_hash(list(insert_values.values()))
    insert_values["unique_id"] = unique_id
    try:
        with Session(engine) as session:
            stmt = insert(pdok_api_adres)
            stmt = stmt.values(**insert_values)
            session.execute(stmt)
            session.commit()
    except IntegrityError:
        inserted = None

def insert_api_postcode(source_json):
    wgs84 = from_wkt(source_json["centroide_ll"])
    rdnew = from_wkt(source_json["centroide_rd"])
    insert_values = dict(
            bron=source_json["bron"],
            postcode=source_json["postcode"],
            straatnaam=source_json["straatnaam"],
            gemeentenaam=source_json["gemeentenaam"],
            woonplaatsnaam=source_json["woonplaatsnaam"],
            provincie_afkorting=source_json["provincieafkorting"],
            centroid_lat=wgs84.y,
            centroid_lon=wgs84.x, 
            centroid_rd_x=rdnew.x,
            centroid_rd_y=rdnew.y)
    unique_id = unique_hash(list(insert_values.values()))
    insert_values["unique_id"] = unique_id
    try:
        with Session(engine) as session:
            stmt = insert(pdok_api_postcode)
            stmt = stmt.values(**insert_values)
            session.execute(stmt)
            session.commit()
    except IntegrityError:
        inserted = None

def insert_kadaster_koopsom(koopsom, postcode, huisnummer, sale_date, kadastral_grotte):
    insert_values = dict(
            koopsom=koopsom,
            postcode=postcode,
            huisnummer=huisnummer, 
            sale_date=sale_date,
            kadastral_grotte=kadastral_grotte)
    unique_id = unique_hash(list(insert_values.values()))
    insert_values["unique_id"] = unique_id
    try:
        with Session(engine) as session:
            stmt = insert(kadaster_koopsom)
            stmt = stmt.values(**insert_values)
            session.execute(stmt)
            session.commit()
    except IntegrityError:
        inserted = None

def insert_funda_aanbod(postcode, huisnummer, toevoeging, vraagprijs, huisgrotte, percelgrotte, kamerkount, energylabel, bouwjaar, aangebodesinds):
    insert_values = dict(
            postcode=postcode, 
            huisnummer=huisnummer, 
            toevoeging=toevoeging,
            vraagprijs=vraagprijs,
            huisgrotte=huisgrotte,
            percelgrotte=percelgrotte, 
            kamerkount=kamerkount,
            energylabel=energylabel, 
            bouwjaar=bouwjaar, 
            aangebodesinds=aangebodesinds)
    unique_id = unique_hash(list(insert_values.values()))
    insert_values["unique_id"] = unique_id
    try:
        with Session(engine) as session:
            stmt = insert(funda_aanbod)
            stmt = stmt.values(**insert_values)
            session.execute(stmt)
            session.commit()
    except IntegrityError:
        inserted = None

def insert_woz_objlookup(adresseerbaarobject_id, wozobjectnummer, postcode, huisnummer, huisletter):
    insert_values = dict(
            adresseerbaarobject_id=adresseerbaarobject_id,
            wozobjectnummer=wozobjectnummer,
            postcode=postcode,
            huisnummer=huisnummer,
            huisletter=huisletter,
    )
    unique_id = unique_hash(list(insert_values.values()))
    insert_values["unique_id"] = unique_id
    try:
        with Session(engine) as session:
            stmt = insert(kadaster_woz_objectlookup_api)
            stmt = stmt.values(**insert_values)
            session.execute(stmt)
            session.commit()
    except IntegrityError:
        inserted = None

def insert_woz_waarde(source_json):
    metadata = source_json["wozObject"]
    waarden = source_json["wozWaarden"]
    insert_values = dict(
            wozobjectnummer=metadata["wozobjectnummer"],
            postcode=metadata["postcode"],
            huisnummer=metadata["huisnummer"],
            huisletter=metadata["huisletter"])
    unique_id = unique_hash(list(insert_values.values()))
    insert_values["unique_id"] = unique_id
    try:
        with Session(engine) as session:
            stmt = insert(kadaster_woz_object_metadata)
            stmt = stmt.values(**insert_values)
            session.execute(stmt)
            session.commit()
    except IntegrityError:
        inserted = None
    for waarde in waarden:
        sub_insert_values = dict(
            fk_wozobjectnummer=metadata["wozobjectnummer"],
            peildatum=datetime.strptime(waarde["peildatum"], "%Y-%m-%d").date(),
            waarde=waarde['vastgesteldeWaarde']
        )
        unique_id = unique_hash(list(sub_insert_values.values()))
        sub_insert_values["unique_id"] = unique_id
        try:
            with Session(engine) as session:
                stmt = insert(kadaster_woz_waarden)
                stmt = stmt.values(**sub_insert_values)
                session.execute(stmt)
                session.commit()
        except IntegrityError:
            inserted = None

def get_api_adres(postcode: str, 
                  huisnummer: int, 
                  toevoeging: Optional[str]=None,
                  format: Optional[str]="point"):
    with Session(engine) as session:
        stmt = select(pdok_api_adres)
        stmt = stmt.where(pdok_api_adres.postcode==postcode)
        stmt = stmt.where(pdok_api_adres.huisnummer==huisnummer)
        if toevoeging:
            stmt = stmt.where(pdok_api_adres.huisletter==toevoeging)
        result = session.execute(stmt).first()
    if result:
        return result[0]
    else:
        return None

def get_woz_by_adres_object(adres_object):
    with Session(engine) as session:
        stmt = select(kadaster_woz_objectlookup_api)
        stmt = stmt.where(kadaster_woz_objectlookup_api.adresseerbaarobject_id==adres_object)
        result = session.execute(stmt).first()
    if type(result) != type(None):
        result = result[0]
        wozobjectnummer = result.wozobjectnummer
        return get_wozwaarde_by_wozobjnum(wozobjectnummer=wozobjectnummer)
    else:
        return None
        
def get_woz_by_pht(postcode, huisnummer, toevoeging: Optional[str]=None):
    with Session(engine) as session:
        stmt = select(kadaster_woz_object_metadata)
        stmt = stmt.where(kadaster_woz_object_metadata.postcode==postcode)
        stmt = stmt.where(kadaster_woz_object_metadata.huisnummer==huisnummer)
        if toevoeging:
            stmt = stmt.where(kadaster_woz_object_metadata.huisletter==toevoeging)
        result = session.execute(stmt).first()
    if result:
        result = result[0]
        wozobjectnummer = result.wozobjectnummer
        return get_wozwaarde_by_wozobjnum(wozobjectnummer=wozobjectnummer)
    else:
        return None

def get_wozwaarde_by_wozobjnum(wozobjectnummer):
    with Session(engine) as session:
        stmt = select(kadaster_woz_waarden)
        stmt = stmt.where(kadaster_woz_waarden.fk_wozobjectnummer == wozobjectnummer)
        df = pd.read_sql(stmt, con=engine)
        return df


def adres_cache_pull(postcode: str, 
                     huisnummer: int, 
                     toevoeging: Optional[str]=None):
    cache = get_api_adres(postcode=postcode,
                          huisnummer=huisnummer,
                          toevoeging=toevoeging)
    if cache:
        return cache
    else:
        api = search_postcode_huisnummer(postcode=postcode, huisnummer=huisnummer, toevoeging=toevoeging)
        for result in api[2]:
            # print(result)
            if result["type"] == "adres":
                if "postcode" in result.keys():
                    insert_api_adres(result)
            elif result["type"] == "postcode":
                insert_api_postcode(result)
    cache = get_api_adres(postcode=postcode,
                          huisnummer=huisnummer,
                          toevoeging=toevoeging)
    if cache:
        return cache
    
def woz_cache_pull_by_adres_object(adres_object):
    cache = get_woz_by_adres_object(adres_object=adres_object)
    if type(cache) != type(None):
        return cache
    else:
        api = get_wozobjectnummer(adres_object=adres_object)
        insert_woz_objlookup(adresseerbaarobject_id=adres_object, 
                             wozobjectnummer=api["wozobjectnummer"],
                             postcode=api["postcode"],
                             huisnummer=api["huisnummer"],
                             huisletter=api["huisletter"])
        waarde = get_wozwaarde(str(api["wozobjectnummer"]))
        insert_woz_waarde(source_json=waarde)
    cache = get_woz_by_adres_object(adres_object=adres_object)
    return cache

def woz_cache_pull_by_pht(postcode, huisnummer, toevoeging: Optional[str]=None):
    adres = adres_cache_pull(postcode=postcode, huisnummer=huisnummer, toevoeging=toevoeging)
    # print(adres)
    return woz_cache_pull_by_adres_object(adres.adresseerbaarobject_id)