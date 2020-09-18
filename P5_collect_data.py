import pandas as pd
import jsonlines
import json
from tqdm import tqdm
from pathlib import Path
from dspipe import Pipe
from pdf_filter import pdf_filter


def read(f0):
    with open(f0) as FIN:
        js = json.load(FIN)
    return js


meta_df = pd.read_csv("data/processed_xml.csv").set_index("archive_key")

data = Pipe("data/language_detection/", limit=None)(read, -1)
df = pd.DataFrame(data)

df = df[df.n_text > 1000]
# df = df[df.most_common_language == 'en']


def compute(f0):
    f0 = Path(f0)

    with open(Path("data/text") / f0.name) as FIN:
        text = FIN.read()

    text = pdf_filter(text)
    key = f0.name.split(".")[0]

    # ===== Skip this filtering step for now =====
    # Further filter only languages 'en' or 'zz'
    # if meta_df.loc[key].language not in ['en', 'zz']:
    #    return None
    # ===== Skip this filtering step for now =====

    return key, text


f_save = "data/PhilArchive.jsonl"
FOUT = jsonlines.open(f_save, "w")

for item in Pipe(df.f_text)(compute, -1):
    key, text = item

    row = {"meta": meta_df.loc[key].to_dict(), "text": text}

    if row is not None:
        FOUT.write(row)
