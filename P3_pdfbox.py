from dspipe import Pipe
import os
import tempfile


def compute(f0, f1):

    with tempfile.NamedTemporaryFile(suffix=".txt") as FOUT:
        cmd = f"java -jar pdfbox-app-2.0.21.jar ExtractText {f0} {FOUT.name}"
        os.system(cmd)

        with open(FOUT.name, "r") as FIN:
            text = FIN.read()

    with open(f1, "w") as FOUT:
        FOUT.write(text)

    print(f0, len(text))


P = Pipe(
    "data/download/",
    "data/text",
    output_suffix=".txt",
    input_suffix=".pdf",
    shuffle=True,
)
P(compute, 8)
