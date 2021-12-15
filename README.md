# The-Pile-PhilPapers

Download, parse, and filter an open access collection of philosophy publications [PhilPapers](https://philpapers.org/), data-ready for [The-Pile](https://github.com/EleutherAI/The-Pile).

The PhilPapers (PP) are indexed using [OAI-MPH](https://www.openarchives.org/pmh/), the Open Archives Initiative Protocol for Metadata Harvesting. As such, the first step to collect the data is to get the XML for all links. This was done using a harvester modified from [here](https://raw.githubusercontent.com/vphill/pyoaiharvester/master/pyoaiharvest.py):

    python pyoaiharvest.py -l https://philarchive.org/oai.pl -o data/phil_meta.xml

From that, each publication is downloaded. Some entries do not exist, or have been removed by the authors. Papers with text are extracted using pdfbox, but papers with non-machine readable text are ignored. Non-English language publications are kept, and the metadata reflects the language reported by the OAI-MPH XML. The text is filtered with pdf_filter.py from [PDFextract](https://github.com/sdtblck/PDFextract)

### Pile-V2 Statistics

    ✔ Saved to PhilArchive.jsonl.zst
    ℹ Collection completed 12/15/2021
    ℹ 42,464 publications (8,474 added, 24.9% growth)
    ℹ Uncompressed filesize 3,270,636,340
    ℹ Compressed filesize     985,311,313
    ℹ sha256sum 9311a57fcbde8dd832e954821bdf0e1f3e2899d9567f6c3b5d7a2d1161fa3e7d

### Pile-V1 Statistics

    ✔ Saved to PhilArchive.jsonl.zst
    ℹ 33,990 publications
    ℹ Uncompressed filesize 2,610,566,629
    ℹ Compressed filesize     797,708,027
    ℹ sha256sum e90529b9b3961328d1e34b60534a8e0f73d5ad1f104e22a217de53cd53c41fea

[**Stat Sheet**](docs/v1/PhilArchive.jsonl.md) created for The-Pile V1.

