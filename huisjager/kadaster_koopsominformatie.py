# pip libraries
from pypdf import PdfReader
import pandas as pd
# builtins
from datetime import datetime

def process_pdf(pdf_file):
    # Read the PDF file
    pdf = PdfReader(pdf_file)
    
    # Define the data frame
    fields = ["Koopsom", "Huisnummer", "Kadastrale_grotte", "Post_code", "Omschrijving", "Date"]
    field_types = ["int", "str", "int", "str", "str", "datetime64[ns]"]
    df = pd.DataFrame(columns={x:pd.Series(dtype=y) for x, y in zip(fields, field_types)})
    
    # Create a data frame index for easier inserts
    df_index = 0

    # iterate through the pages
    for page in pdf.pages:
        # Use the extract text mode and format via layout
        et = page.extract_text(extraction_mode="layout")
        # Split based on lines the layout into a list
        s = [z.strip() for z in [x for x in et.split("\n")] if z != ""]
        # postcode is on every page 
        # TODO check entire document for postcode being the same
        postcode = s[1].split(" ")[0]
        # Split index
        spi = 0
        # Iterate through the each item in the split list
        for sp in s:
            # This is the starting point of every record
            if sp.startswith("Datum overdracht"):
                # first segment: retrieve sale date, house number
                segments = [y for y in [x for x in sp.split(" ")] if y != ""]
                sale_date = datetime.strptime(segments[2], "%d-%m-%Y")
                huisnummer = segments[-1]
                # second segment: retrieve koopsom, size if exists
                segments = [y for y in [x for x in s[spi + 1].split(" ")] if y != ""]
                koopsom = int(segments[2].replace(".",""))
                if "Kadastrale" in segments:
                    kadastrale_grotte = int(segments[-2])
                else:
                    kadastrale_grotte = None
                # thirt segment: retrieve type of house
                segments = [y for y in [x for x in s[spi + 2].split(" ")] if y != ""]
                omschrijving = segments[-1].replace("(", "").replace(")", "")
                # Add to data frame
                df.loc[df_index] = [koopsom, huisnummer, kadastrale_grotte, postcode, omschrijving, sale_date]
                df_index += 1 #iterate index
            spi += 1 #iterate index of list
    # Write to CSV
    # df.to_csv(f"Kadaster_{postcode}.csv", columns=fields)
    return df