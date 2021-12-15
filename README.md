# The-Pile-PhilPapers

Download, parse, and filter an open access collection of philosophy publications [PhilPapers](https://philpapers.org/), data-ready for [The-Pile](https://github.com/EleutherAI/The-Pile).

The PhilPapers (PP) are indexed using [OAI-MPH](https://www.openarchives.org/pmh/), the Open Archives Initiative Protocol for Metadata Harvesting. As such, the first step to collect the data is to get the XML for all links. This was done using a harvester modified from [here](https://raw.githubusercontent.com/vphill/pyoaiharvester/master/pyoaiharvest.py):

    python pyoaiharvest.py -l https://philarchive.org/oai.pl -o data/phil_meta.xml

From that, each publication is downloaded. Some entries do not exist, or have been removed by the authors. Papers with text are extracted using pdfbox, but papers with non-machine readable text are ignored. Non-English language publications are kept, and the metadata reflects the language reported by the OAI-MPH XML. The text is filtered with pdf_filter.py from [PDFextract](https://github.com/sdtblck/PDFextract)

[**Stat Sheet**](docs/PhilArchive.jsonl.md) for The-Pile V1