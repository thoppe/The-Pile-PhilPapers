import json
import pandas as pd
from dspipe import Pipe


def read(f0):
    with open(f0) as FIN:
        js = json.load(FIN)
    return js


data = Pipe("data/language_detection/")(read, -1)
df = pd.DataFrame(data)
n_org = len(df)

print(f"Total number of PDFs downloaded {n_org}")

df = df[df.n_text > 1000]
n_text = len(df)
print(f"Number of PDFs with text > 1000 chars {n_text}, {n_text/n_org:0.3f}")

# print(df.value_counts('most_common_language'))
df = df[df.most_common_language == "en"]
n_english = len(df)
print(f"Number of English language text {n_english}, {n_english/n_org:0.3f}")
