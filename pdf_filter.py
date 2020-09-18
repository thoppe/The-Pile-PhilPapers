"""aggressive-ish pdf cleaning script for language models.
    Based off: https://gist.github.com/leogao2/8d4662dfb8e58e8c58ef94df5d46413d by Leo Gao"""

import os
import re
import unicodedata


lone_accent_dict = {
    "a´": "á",
    "e´": "é",
    "i´": "í",
    "o´": "ó",
    "u´": "ú",
    "a¨": "ä",
    "e¨": "ë",
    "i¨": "ï",
    "o¨": "ö",
    "u¨": "ü",
    "a^": "â",
    "e^": "ê",
    "i^": "î",
    "o^": "ô",
    "u^": "û",
    "a`": "à",
    "e`": "è",
    "i`": "ì",
    "o`": "ò",
    "u`": "ù",
    "a~": "ã",
    "o~": "õ",
    "n~": "ñ",
}

lone_accent_dict.update({k.upper(): v.upper() for k, v in lone_accent_dict.items()})


def ditch_combining_diacritics(text):
    for orig, repl in lone_accent_dict.items():
        text = text.replace(orig, repl)
    text = re.sub(r"[\u0300-\u036F]", "", text)
    return re.sub(r"(?:\xa8|[\u02C0-\u02DF])", "", text)


def listdir(x):
    return [x + "/" + fn for fn in os.listdir(x)]


def id(x):
    return x


def average_word_length(text):
    """
    get average word length of a given text file

    :param txt: string
    :return: float of avg word length
    """
    n_words = len(text.split())
    n_chars = len(text)
    avgw = n_chars / (n_words + 1)
    return avgw


def mean(x):
    x = list(x)
    if not x:
        return 0
    return sum(x) / len(x)


def nonzero(x):
    return filter(id, x)


def is_letter(x):
    return x in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def is_date(x):
    res = re.match(r".*([1-3][0-9]{3})", x)
    if res is not None:
        return True
    else:
        return False


def header_footer_filter(para):
    """if para is short & begins with ©, r {date}, copyright {date}, remove para"""
    try:
        if len(para) < 50:
            if para.strip()[0] == "©":
                return ""
            elif para.strip()[0] == "r":
                para_words = para.strip().split(" ")
                if len(para_words) >= 2:
                    second_word = para_words[1]
                    if is_date(second_word):
                        return ""
            elif para.strip().split(" ")[0] == "copyright":
                second_word = para.strip().split(" ")[1]
                if is_date(second_word):
                    return ""
    except:
        return para
    return para


def all_equal(x):
    return all([n == x[0] for n in x])


def replace_hyphenated(text):
    text = re.sub(r"-[?\s]\n{1,2}(\w+ *)", r"\1\n", text)
    return re.sub(r"-\s{1,2}(\w+ *)", r"\1", text)


def remove_leading_and_trailing_nums(text):
    # remove leading and trailing numbers (i.e page nums)
    text = text.strip()
    text = re.sub(r"^(\d+)", "", text)
    text = re.sub(r"(\d+)$", "", text)
    return text.strip()


def cid_percentage(text):
    """
    detects the amount of cid numbers (an artefact from missing custom fonts) found in a converted pdf.
    Example:

        "which maintained contacts not least in  the  South  East  Asian  extreme  right.  To  some  extent  during  the
        (cid:38)(cid:82)(cid:79)(cid:71)(cid:3) (cid:58)(cid:68)(cid:85)(cid:15)"

    :param text: string
    :return: float between 0 and 1 representing density of cid nos in string
    """
    n_matches = len(re.findall("\(cid:[0-9]+\)", text))
    if text:
        return (n_matches * 8) / len(text)
    else:
        return 0.0


def remove_cid(text):
    return re.sub("\(cid:[0-9]+\)", "", text)


def filter_double_whitespace(text):
    return re.sub("\s\s+", " ", text)


def filter_newlines(text):
    return re.sub("\n", " ", text)


def pdf_filter(text):
    # cid_perc = cid_percentage(text)
    # if cid_perc is larger than threshold, it's probably a latex / alt font heavy document. delete the whole thing.
    # if cid_perc > 0.03:
    #    print("ERROR: too many font errors - skipping {}.".format(fn))
    #    return ""
    # if mean line len is too short, it's probably garbled, not useful, or overly latex-y
    # whole_doc_mean_line_len = mean(nonzero(map(len, text.split("\n"))))
    # if whole_doc_mean_line_len < 15:
    #    print("ERROR: avg mean line length too short - skipping {}.".format(fn))
    #    return ""
    # word_length = average_word_length(text)
    # if average word length is too big or small, document is not worth keeping
    # if word_length > 45:
    #    print("ERROR: avg word length too large - skipping {}.".format(fn))
    #    return ""
    # elif word_length < 2:
    #    print("ERROR: avg word length too short - skipping {}.".format(fn))
    #    return ""
    # replace hyphens at end of lines and paragraphs

    text = replace_hyphenated(text)
    paras = text.split("\n\n")
    out = []
    for para in paras:

        # filter out new lines in the middle of paragraphs,
        # remove headers
        # and remove double whitespaces
        para = filter_newlines(para)
        para = header_footer_filter(para)
        para = filter_double_whitespace(para)

        # if mean line len is too short, it's probably garbled or not useful
        mean_line_len = mean(nonzero(map(len, para.split("\n"))))
        if mean_line_len < 2.0:
            continue

        # if cid_percentage is higher than 10%, it's likely a latex heavy para and won't make sense without it
        # delete the whole para
        if cid_percentage(para) > 0.1:
            continue
        # not enough letters (i.e math, tables, etc)
        letterness = mean(map(is_letter, para))
        if letterness < 0.40:
            continue

        #   final cleaning steps:
        #   remove leading and trailing numbers (usually pagenos)
        #   remove any remaining cid strings
        #   fix any unicode / ligature related errors
        #   combine letter -> accent strings from bad decoding to combined letter/accent
        #   e.g a´ gets converted to á
        para = ditch_combining_diacritics(
            fix_unicode(remove_cid(remove_leading_and_trailing_nums(para)))
        )
        if para != "":
            # only append if not empty
            out.append(para)

        # remove empty strings from prev step
        for i in out:
            if not i:
                out.remove(i)

    return "\n\n".join(out)


"""
from: https://github.com/mattbierbaum/arxiv-public-datasets/blob/f0b8a4fd17e7aeed38465ec00a63eb219fe1672e/arxiv_public_data/fixunicode.py#L92

List of ligatures: https://en.wikipedia.org/wiki/Typographic_ligature
MKB removed the following elements from the list:
      - et	🙰	U+1F670	&#x1F670;
      - ſs, ſz	ẞ, ß	U+00DF	&szlig;

Additional notes:
* Some classes of characters were listed in the original utf8 fixes but I'm not
  sure they don't belong elsewhere (end user processing). In these cases, pass
  through unidecode should normalize them to proper ascii. They are listed here
  with reasoning:

  - Ditch combining diacritics http://unicode.org/charts/PDF/U0300.pdf
    r'[\u0300-\u036F]': ''

  - Ditch chars that sometimes (incorrectly?) appear as combining diacritics
    r'(?:\xa8|[\u02C0-\u02DF])': ''

* Should we run ftfy?
"""

ligature_table = """
AA, aa	Ꜳ, ꜳ	U+A732, U+A733	&#xA732; &#xA733;
AE, ae	Æ, æ	U+00C6, U+00E6	&AElig; &aelig;
AO, ao	Ꜵ, ꜵ	U+A734, U+A735	&#xA734; &#xA735;
AU, au	Ꜷ, ꜷ	U+A736, U+A737	&#xA736; &#xA737;
AV, av	Ꜹ, ꜹ	U+A738, U+A739	&#xA738; &#xA739;
AV, av 	Ꜻ, ꜻ	U+A73A, U+A73B	&#xA73A; &#xA73B;
AY, ay	Ꜽ, ꜽ	U+A73C, U+A73D	&#xA73C; &#xA73D;
ff	ﬀ	U+FB00	&#xFB00;
ffi	ﬃ	U+FB03	&#xFB03;
ffl	ﬄ	U+FB04	&#xFB04;
fi	ﬁ	U+FB01	&#xFB01;
fl	ﬂ	U+FB02	&#xFB02;
OE, oe	Œ, œ	U+0152, U+0153	&OElig; &oelig;
OO, oo	Ꝏ, ꝏ	U+A74E, U+A74F	&#xA74E; &#xA74F;
st	ﬆ	U+FB06	&#xFB06;
ſt	ﬅ	U+FB05	&#xFB05;
TZ, tz	Ꜩ, ꜩ	U+A728, U+A729	&#xA728; &#xA729;
ue	ᵫ	U+1D6B	&#x1D6B;
VY, vy	Ꝡ, ꝡ	U+A760, U+A761	&#xA760; &#xA761;
db	ȸ	U+0238	&#x238;
dz	ʣ	U+02A3	&#x2A3;
dʑ 	ʥ	U+02A5	&#x2A5;
dʒ 	ʤ	U+02A4	&#x2A4;
fŋ 	ʩ	U+02A9	&#x2A9;
IJ, ij	Ĳ, ĳ	U+0132, U+0133	&#x132; &#x133;
ls	ʪ	U+02AA	&#x2AA;
lz	ʫ	U+02AB	&#x2AB;
lʒ 	ɮ	U+026E	&#x26E;
qp	ȹ	U+0239	&#x239;
tɕ 	ʨ	U+02A8	&#x2A8;
ts	ʦ	U+02A6	&#x2A6;
tʃ 	ʧ	U+02A7	&#x2A7;
ui	ꭐ	U+AB50	&#xAB50;
ui	ꭑ	U+AB51	&#xAB50;
"""

unicode_mapping = {}

for row in ligature_table.split("\n"):
    if row.count("\t") <= 1:
        continue

    unicode_mapping.update(
        {
            u.strip(): unicodedata.normalize("NFKC", a.strip())
            for a, u in zip(*[c.split(",") for c in row.split("\t")[:2]])
        }
    )

unicode_mapping.update(
    {
        # 'ẞ, ß': careful, some use this for \beta
        r"(\B)\u00DF": r"\1ss",
        # Additions (manual normalization that we feel is important)
        # unicode space  u'\xa0'  (not \x{0c} = ^L keep!)
        "\xa0": " ",
        # single + double quotes, dash, and asterisk
        r"[\u2018\u2019]": r"'",
        r"[\u201C\u201D]": r'"',
        r"[\xad\u2014]": r"-",
        r"\xb7": r"*",
    }
)


def fix_unicode(txt: str) -> str:
    """
    Given UTF-8 encoded text, remove typographical ligatures (normalize to true
    non-display character set) and do a general normalization of the unicode
    so that possible redundant characters and simplified to a single set.

    Parameters
    ----------
    txt : unicode string

    Returns
    -------
    output : unicode string
    """
    for search, replace in unicode_mapping.items():
        txt = re.subn(search, replace, txt)[0]
    return unicodedata.normalize("NFKC", txt)
