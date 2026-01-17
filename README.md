# Huisjager

House hunting tool made with Streamlit for aggregating real estate information in the Netherlands


***

## What's this?

This Streamlit tool is made for aggregating real estate market information in the Netherlands. 

The tool does several things:

1. Converts Kadaster Koopsominformatie PDFs into a table of home sale information. 
2. Has a form for adding Funda real estate listings with basic metadata
3. Scrapes WOZ Waarde data for address valuations

The tool also includes a very basic mapping function by requesting geocoding information from the Kadaster Adres API. It will also display WOZ Waarde data over time. 

## How to use

Start the tool with `streamlit run 0_🏘️_Huisjager.py`. 

Upload your Koopsominformatie PDFs to the dashboard and see them magically appear. Download a table for use in other software later. 

Manually copy information from Funda into the form to aggregate listings. 
