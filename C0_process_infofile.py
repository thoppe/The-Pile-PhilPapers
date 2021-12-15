import jsonlines
import json
import configparser
from tqdm import tqdm
from pathlib import Path
import hashlib
import datetime

"""
Update dataset_info.ini for corpus-specific information.
"""

config = configparser.ConfigParser()
config.read("dataset_info.ini")
info = dict(config["corpus"])


f_dataset = "data/PhilArchive.jsonl"
f_compressed = "data/PhilArchive.jsonl.zst"

# This is the specific line to show the sample, adjust for a good example
sample_row_n = 10010


def compute_hash(f, blocksize=4096):
    print(f"Computing hash for {f}")

    sha256_hash = hashlib.sha256()
    with open(f, "rb") as FIN:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: FIN.read(blocksize), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def measure_file(f):
    f = Path(f)
    assert f.exists()

    return {
        "filename": str(f),
        "size": f.stat().st_size,
        "last_modified_UTC": int(f.stat().st_mtime),
        "sha256_hash": compute_hash(f),
    }


# Create an infofile if it doesn't exist, otherwise read prior values
save_dest = Path("docs")
save_dest.mkdir(exist_ok=True)

f_info = save_dest / "dataset_information.json"
f_markdown = save_dest / (Path(f_dataset).name + ".md")

if Path(f_info).exists():
    with open(f_info) as FIN:
        info.update(json.load(FIN))

if "file_information" not in info:
    info["file_information"] = {
        "uncompressed": measure_file(f_dataset),
        "compressed": measure_file(f_compressed),
    }


if (
    "corpus_statistics" not in info
    or int(info["sample_data"]["sample_row_n"]) != sample_row_n
):

    print(f"Computing statistics for {f_dataset}")

    stats = {
        "total_documents": 0,
        "total_character_count": 0,
        "total_word_count": 0,
        "max_character_count": 0,
        "min_character_count": 10 ** 20,
        "max_word_count": 0,
        "min_word_count": 10 ** 20,
    }

    sample = {}

    with jsonlines.open(f_dataset) as FIN:
        for n, row in enumerate(tqdm(FIN)):
            text = row["text"]
            words = text.split()

            stats["total_documents"] += 1
            stats["total_character_count"] += len(text)
            stats["total_word_count"] += len(words)

            stats["max_character_count"] = max(len(text), stats["max_character_count"])
            stats["min_character_count"] = min(len(text), stats["min_character_count"])

            stats["max_word_count"] = max(len(words), stats["max_word_count"])
            stats["min_word_count"] = min(len(words), stats["min_word_count"])

            if n == sample_row_n:
                sample["text"] = row["text"]
                sample["meta"] = row["meta"]
                sample["sample_row_n"] = sample_row_n

                print(text)

    info["corpus_statistics"] = stats
    info["sample_data"] = sample


js = json.dumps(info, indent=2)

with open(f_info, "w") as FOUT:
    FOUT.write(js)


meta_pp = json.dumps(info["sample_data"]["meta"], indent=2)

print(js)
text = info["sample_data"]["text"].strip()

# Now build a nice markdown version of the datafile

MD = f"""
# {info['title']}

| {info["short_title"]}  |  |
| ---             | ---:   |
| Reference URL   | {info["url"]} |
| Replication URL | {info["replication_url"]} |
| Uncompressed file size | {info["file_information"]["uncompressed"]["size"]:,} |
| Year range | {info["min_year"]} - {info["max_year"]} |
| Primary language | {info["language"]} |
| Document count  | {info["corpus_statistics"]["total_documents"]:,} |
| Word count      | {info["corpus_statistics"]["total_word_count"]:,} |
| Character count | {info["corpus_statistics"]["total_character_count"]:,} |

### Sample Text (found at row {sample_row_n})

```text
{text}
```

### Sample meta information (found at row {sample_row_n})

```json
{meta_pp}
```

### SHA256 checksums

| Filename             | Checksum |
| ---             | :---   |
| Compressed | `{info["file_information"]["compressed"]["sha256_hash"]}` |
| Uncompressed | `{info["file_information"]["uncompressed"]["sha256_hash"]}` |
"""

with open(f_markdown, "w") as FOUT:
    FOUT.write(MD)
