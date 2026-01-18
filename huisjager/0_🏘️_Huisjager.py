from postcode_api import search_postcode_huisnummer
from kadaster_koopsominformatie import process_pdf
from huisjager_db import insert_funda_aanbod
from huisjager_db import insert_kadaster_koopsom
from huisjager_db import adres_cache_pull
from huisjager_db import woz_cache_pull_by_pht
import streamlit as st
from streamlit_folium import st_folium
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from shapely import from_wkt
from datetime import datetime
import hashlib
from io import StringIO, BytesIO

st.set_page_config(layout="wide", page_icon="🏘️")

st.header("Kadaster Koopsominformatie")

koopsom_files = st.file_uploader("Upload your Kadaster Koopsom documents", 
                                 type=["pdf"], 
                                 accept_multiple_files=True)

if koopsom_files:
    # st.write(koopsom_files)
    extracts = None
    for file in koopsom_files:
        # st.write(fidle)
        if type(extracts) == type(None):
            extracts = process_pdf(file)
        else:
            extracts = pd.concat([extracts, process_pdf(file)])
    adrezen = []
    for ix, row in extracts.iterrows():
        adres = adres_cache_pull(postcode=row.Post_code, huisnummer=row.Huisnummer)
        adres_n = (adres.postcode, adres.huis_nlt, adres.centroid_lat, adres.centroid_lon)
        adrezen.append(adres_n)
        insert_kadaster_koopsom(row.Koopsom, row.Post_code, row.Huisnummer, row.Date, row.Kadastrale_grotte)
    with st.expander(label="Map of Extracted Units", expanded=True):
        adrezen_lats = [x[2] for x in adrezen]
        adrezen_lons = [x[3] for x in adrezen]
        mean_lats = sum(adrezen_lats) / len(adrezen_lats)
        mean_lons = sum(adrezen_lons) / len(adrezen_lons)
        koopsomkaart = folium.Map([mean_lats, mean_lons], zoom_start=15, width="100%", height="100%")
        for adrez in adrezen:
            folium.Marker([adrez[2], adrez[3]], icon=folium.Icon(color="green", icon="home")).add_to(koopsomkaart)
        st_folium(koopsomkaart, width=1200, height=700)
    extracts["cost per sq m"] = extracts["Koopsom"] / extracts["Kadastrale_grotte"]
    extracts["DateLabel"] = extracts["Date"]
    extracts["Date"] = [(x - datetime(1970, 1, 1)).total_seconds() for x in extracts["Date"]]
    
    with st.expander(label="Extracted tables", expanded=True):
        st.dataframe(extracts)

    with st.container(border=True):
        st.header("Koopsominformatie Graph")
        options = ["Date", "Koopsom", "Kadastrale_grotte", "cost per sq m"]
        x_choice = st.pills("x-axis variable", options=options, default=options[0])
        default_y_index = 1
        if x_choice == options[1]:
            default_y_index = 0
        y_choice = st.pills("y-axis variable", options=options, default=options[default_y_index])
        color_choice = [x for x in options if x not in [x_choice, y_choice]][0]

        fig = px.scatter(extracts, x=x_choice, y=y_choice,
                        color=color_choice,
                        color_continuous_scale="bluyl",
                        height=800)
        fig.update_traces(marker=dict(size=12))
        tickjaren = [datetime(x, 1, 1) for x in range(2003, datetime.now().year + 1)]
        ticktext = [str(x.year) for x in tickjaren]
        tickvals = [(x - datetime(1970, 1, 1)).total_seconds() for x in tickjaren]
        if x_choice == "Date":
            fig.update_xaxes(tickmode="array", tickvals=tickvals, ticktext=ticktext)
        if color_choice == "Date":
            
            fig.update_coloraxes(colorbar_tickmode="array", colorbar_tickvals=tickvals, colorbar_ticktext=ticktext)
        st.plotly_chart(fig)

if "extracts" in dir():
    st.text("Download Koopsominformatie as a table here:")

    ksi_1, ksi_2, ksi_3, ksi_4, ksi_5 = st.columns(5)

    csv_file = BytesIO()
    extracts.to_csv(csv_file)
    excel_file = BytesIO()
    extracts.to_excel(excel_file)

    ksi_1.download_button("Download as CSV", data=csv_file, file_name=f"Koopsominformatie_{datetime.now().isoformat()}.csv")
    ksi_2.download_button("Download as Excel", data=excel_file, file_name=f"Koopsominformatie_{datetime.now().isoformat()}.xlsx")

st.header("Funda")

if "fundadf" not in st.session_state.keys():
    funda_df = pd.DataFrame(columns=["submission_id",
                                     "Postcode", 
                                    "Huisnummer", 
                                    "Toevoeging", 
                                    "Vraagprijs", 
                                    "Huisgrotte", 
                                    "Percelgrotte", 
                                    "Kamerkount", 
                                    "EnergyLabel", 
                                    "Bouwjaar",
                                    "AangebodenSinds"])

    st.session_state["fundadf"] = funda_df

def add_row_fundadf(df, postcode, huisnummer, toevoeging, vraagprijs, huisgrotte, percelgrotte, kamerkount, energylabel, bouwjaar, aangeboden):
    hasher = hashlib.md5()
    for parameter in [str(x).encode("utf8") for x in (postcode, huisnummer, toevoeging, vraagprijs, huisgrotte, percelgrotte, kamerkount, energylabel, bouwjaar, aangeboden)]:
        hasher.update(parameter)
    submission_id = str(hasher.hexdigest())
    if submission_id not in list(df["submission_id"]):
        if len(postcode) == 6:
            insert_funda_aanbod(postcode, huisnummer, toevoeging, vraagprijs, huisgrotte, percelgrotte, kamerkount, energylabel, bouwjaar, aangeboden)
            new_line = (submission_id, postcode, huisnummer, toevoeging, vraagprijs, huisgrotte, percelgrotte, kamerkount, energylabel, bouwjaar, aangeboden)
            try: 
                df.loc[max(df.index) + 1] = new_line
            except ValueError:
                df.loc[0] = new_line
            return df


with st.form("funda-data", clear_on_submit=True):
    # submission_id = st.text_input(label="SubmissionID (not editable): ", value=str(uuid4()), disabled=True)
    fk0, fk1, fk2 = st.columns(3) # Funda Kadastral
    new_funda_postcode = fk0.text_input("Postcode: ", max_chars=6, )
    new_funda_huisnummer = fk1.number_input("Huisnummer: ", min_value=0)
    new_funda_toevoeging = fk2.text_input("Toevoeging: ", max_chars=3)
    new_funda_vraagprijs = st.number_input("Vraagprijs", min_value=0, icon="💶")
    fm0, fm1, fm2 = st.columns(3) # Funda meting
    new_funda_huisgrotte = fm0.number_input("Thuisgrotte: ", min_value=0)
    new_funda_percelgrotte = fm1.number_input("Percelgrotte: ", min_value=0)
    new_funda_kamerkount = fm2.number_input("Aantal kamers: ", min_value=0)
    fe0, fe1, fe2 = st.columns(3) # Funda extra
    new_funda_energylabel = fe0.select_slider("Energylabel: ", options=["A+++", "A++", "A+", "A", "B", "C", "D", "E", "F", "G"])
    new_funda_bouwjaar = fe1.number_input("Bouwjaar: ", min_value=1000, max_value=datetime.now().year+1, value=1980)
    new_funda_aangeboden = fe2.date_input("Aangeboden sinds:")
    st.form_submit_button("Toevoeg naar tabel", )

funda_df = add_row_fundadf(st.session_state["fundadf"], new_funda_postcode, new_funda_huisnummer, new_funda_toevoeging,
                           new_funda_vraagprijs, new_funda_huisgrotte, new_funda_percelgrotte, 
                           new_funda_kamerkount, new_funda_energylabel, new_funda_bouwjaar,
                           new_funda_aangeboden)

# st.write(st.session_state)
# st.session_state["fundadf"] = st.session_state["fundadf"][st.session_state["fundadf"].duplicated(keep=False)]
st.dataframe(st.session_state["fundadf"])
funda_adrezen = []

woz_y_choices = ["Prijs", "Prijs/sqm Huisgrotte", "Prijs/sqm Perceelgrotte"]
woz_y_options = ["waarde", "ppmh", "ppmp"]
woz_y_choice = st.pills("WOZ Graph Y Axis: ", options=woz_y_choices, default=woz_y_choices[0])

woz_fig = go.Figure()
for ix, row in st.session_state["fundadf"].iterrows():
    adres = adres_cache_pull(postcode=row.Postcode, huisnummer=row.Huisnummer, toevoeging=row.Toevoeging)
    adres_f = (adres.postcode, adres.huis_nlt, adres.centroid_lat, adres.centroid_lon)
    funda_adrezen.append(adres_f)
    color = f"#{row.submission_id[:6]}"
    woz = woz_cache_pull_by_pht(postcode=row.Postcode, huisnummer=row.Huisnummer, toevoeging=row.Toevoeging)
    woz["ppmh"] = [(x/row.Huisgrotte) for x in woz["waarde"]] # prijs per meter huis
    woz["ppmp"] = [(x/row.Percelgrotte) for x in woz["waarde"]] # prijs per meter perceel
    peiltrace = woz_fig.add_trace(go.Scatter(x=woz["peildatum"], 
                                             y=woz[woz_y_options[woz_y_choices.index(woz_y_choice)]], 
                                             name=f"{row.Postcode} {row.Huisnummer} - WOZ",
                                             marker={"color": color,
                                                     "size": 15},
                                             line={"color": color,
                                                   "width": 4}))
    funda_vraagprijs_y_choice = [row.Vraagprijs, (row.Vraagprijs/row.Huisgrotte), (row.Vraagprijs/row.Percelgrotte)]
    woz_fig.add_trace(go.Scatter(x=pd.Series(row.AangebodenSinds), 
                                y=pd.Series(funda_vraagprijs_y_choice[woz_y_choices.index(woz_y_choice)]), 
                                name=f"{row.Postcode} {row.Huisnummer} - Funda",
                                marker={"color": color, 
                                        "size": 15,
                                        "line": {"width": 1.5,
                                                 "color": "#ff9b21"}},
                                line={"width": 0}))
# woz_fig.update_xaxes()
woz_fig.update_layout(height=800, 
                      title="WOZ Waarden en Funda Vraagprijs",
                      xaxis={"title": "Datum"},
                      yaxis={"title": "Prijs"})
st.plotly_chart(woz_fig)

try:
    funda_mean_lat = sum([x[2] for x in funda_adrezen]) / len(funda_adrezen)
    funda_mean_lon = sum([x[3] for x in funda_adrezen]) / len(funda_adrezen)
except ZeroDivisionError:
    funda_mean_lat = 52
    funda_mean_lon = 4.5

funda_kaart = folium.Map([funda_mean_lat, funda_mean_lon], zoom_start=15)
for adres in funda_adrezen:
    folium.Marker([adres[2], adres[3]], icon=folium.Icon(color="orange", icon="home")).add_to(funda_kaart)
st_folium(funda_kaart, width=1200, height=600)

if "fundadf" in st.session_state:
    if "woz" in dir():
        st.text("Download Funda and WOZ data as a table here:")

        fwi_1, fwi_2, fwi_3, fwi_4, fwi_5 = st.columns(5)

        funda_csv_file = BytesIO()
        st.session_state["fundadf"].to_csv(funda_csv_file)
        funda_excel_file = BytesIO()
        st.session_state["fundadf"].to_excel(funda_excel_file)
        woz_csv_file = BytesIO()
        woz.to_csv(woz_csv_file)
        woz_excel_file = BytesIO()
        woz.to_excel(woz_excel_file)

        fwi_1.download_button("Download Funda as CSV", data=funda_csv_file, file_name=f"Funda_{datetime.now().isoformat()}.csv")
        fwi_2.download_button("Download Funda as Excel", data=funda_excel_file, file_name=f"Funda_{datetime.now().isoformat()}.xlsx")
        fwi_3.download_button("Download WOZ as CSV", data=woz_csv_file, file_name=f"WOZ_{datetime.now().isoformat()}.csv")
        fwi_4.download_button("Download WOZ as Excel", data=woz_excel_file, file_name=f"WOZ_{datetime.now().isoformat()}.xlsx")