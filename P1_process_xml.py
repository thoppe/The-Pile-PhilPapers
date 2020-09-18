import bs4
import pandas as pd
from tqdm import tqdm

f_xml = "data/phil_meta.xml"
f_save = "data/processed_xml.csv"

with open(f_xml) as FIN:
    soup = bs4.BeautifulSoup(FIN.read(), "lxml")

data = []
for record in tqdm(soup.find_all("record")):

    # Extract the oai_dc meta information
    meta = record.find("metadata")
    if meta is None:
        continue

    meta = meta.find("oai_dc:dc")

    row = {}
    for block in meta.findChildren():
        name = block.name.split(":")[-1]
        row[name] = block.text.strip()

    # Extract the date published

    datestamp = record.find("datestamp")
    if datestamp is None:
        continue
    row["datestamp"] = datestamp.text

    # Extract the unique identifier
    # PDF if exists should be at https://philarchive.org/archive/NAME

    iden = record.find("identifier")
    if iden is None:
        continue
    row["identifier"] = iden.text
    row["archive_key"] = row["identifier"].split("/")[-1]

    data.append(row)

df = pd.DataFrame(data).set_index("archive_key")
print(df)
df.to_csv(f_save)
