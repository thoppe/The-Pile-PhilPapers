# The-Pile-PhilPapers

Download, parse, and filter [PhilPapers](https://philpapers.org/), data-ready for [The-Pile](https://github.com/EleutherAI/The-Pile). PhilPapers are an open access collection of philosophy publications.

The PhilPapers (PP) are index using the [OAI-MPH](https://www.openarchives.org/pmh/), which is the Open Archives Initiative Protocol for Metadata Harvesting. As such, the first step to collect the data is to get the XML for all links:

    python2 pyoaiharvest.py -l https://philarchive.org/oai.pl -o data/phil_meta.xml

From that, each publication is downloaded if it exists. Papers with text are extracted using pdfbox, but papers with non-machine readable text are ignored. Non-English language publications are kept, and the metadata reflects the language reported by the OAI-MPH XML. The text is filtered with pdf_filter.py from [PDFextract](https://github.com/sdtblck/PDFextract)

     ✔ Saved to data/PhilArchive.jsonl
     ℹ Saved 33,990 articles
     ℹ Uncompressed filesize 2,610,566,629
     ℹ Compressed filesize     79,7708,027

Data souce temporary hosted at https://drive.google.com/file/d/1u01vkBNAS8jtu0AZeQW56bzf-6QbeSRB/view?usp=sharing

     > sha256sum PhilArchive.jsonl.zst 
     e90529b9b3961328d1e34b60534a8e0f73d5ad1f104e22a217de53cd53c41fea  PhilArchive.jsonl.zst