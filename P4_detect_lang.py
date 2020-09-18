from dspipe import Pipe
import json
from langdetect import detect


def compute(f0, f1):
    with open(f0) as FIN:
        text = FIN.read().strip()

    try:
        lang = detect(text)
    except:
        lang = ""

    item = {"most_common_language": lang, "n_text": len(text), "f_text": str(f0)}

    js = json.dumps(item, indent=2)

    with open(f1, "w") as FOUT:
        FOUT.write(js)


Pipe(
    "data/text/",
    "data/language_detection",
    input_suffix=".txt",
    output_suffix=".json",
    shuffle=True,
)(compute, 1)
