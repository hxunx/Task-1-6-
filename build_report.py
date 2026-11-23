"""Build the 2-3 page Task 1 PDF report from the results computed in data_exploration.ipynb.

Every number in the PDF comes from outputs/results.json (written by the notebook from the
actual Kaggle records). Only the team/config fields in the notebook's CONFIG cell are typed by hand.

Usage:
    python build_report.py            # reads outputs/results.json and outputs/eda_figure.png
"""
import json
import os
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle)

NAVY = colors.HexColor("#1f3a5f")
GREY = colors.HexColor("#f0f2f5")
LINE = colors.HexColor("#b8c0cc")

BODY = ParagraphStyle("body", fontName="Helvetica", fontSize=8.2, leading=10.2, spaceAfter=2.5)
SMALL = ParagraphStyle("small", parent=BODY, fontSize=7.2, leading=8.8, spaceAfter=1)
CELL = ParagraphStyle("cell", parent=BODY, fontSize=7.1, leading=8.5, spaceAfter=0)
CELLB = ParagraphStyle("cellb", parent=CELL, fontName="Helvetica-Bold")
TITLE = ParagraphStyle("title", parent=BODY, fontName="Helvetica-Bold", fontSize=13.5,
                       leading=16, textColor=NAVY, spaceAfter=1)
SUB = ParagraphStyle("sub", parent=BODY, fontSize=8, textColor=colors.HexColor("#444444"))
H1 = ParagraphStyle("h1", parent=BODY, fontName="Helvetica-Bold", fontSize=9.6, leading=12,
                    textColor=NAVY, spaceBefore=5, spaceAfter=2)
BUL = ParagraphStyle("bul", parent=BODY, leftIndent=9, bulletIndent=0, spaceAfter=1.2)

# Korean team-member names need a font with Hangul glyphs; look for one on this computer.
_KR_CANDIDATES = [
    ("C:/Windows/Fonts/malgun.ttf", 0),
    ("/System/Library/Fonts/Supplemental/AppleGothic.ttf", 0),
    ("/Library/Fonts/NanumGothic.ttf", 0),
    ("/usr/share/fonts/truetype/nanum/NanumGothic.ttf", 0),
    ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 1),
    ("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc", 1),
]
KR_OK = False
for _p, _i in _KR_CANDIDATES:
    if os.path.exists(_p):
        try:
            pdfmetrics.registerFont(TTFont("KR", _p, subfontIndex=_i))
            KR_OK = True
            break
        except Exception:
            continue
if not KR_OK:
    # Built-in Korean CID font: needs no font file (the PDF viewer supplies the glyphs).
    try:
        from reportlab.pdfbase.cidfonts import UnicodeCIDFont
        pdfmetrics.registerFont(UnicodeCIDFont("HYSMyeongJo-Medium"))
        pdfmetrics.registerFontFamily("HYSMyeongJo-Medium", normal="HYSMyeongJo-Medium")
        KR_FONT = "HYSMyeongJo-Medium"
        KR_OK = True
    except Exception:
        KR_FONT = None
else:
    KR_FONT = "KR"


def esc(x):
    return escape(str(x))


def has_hangul(s):
    return any("\uac00" <= ch <= "\ud7a3" for ch in str(s))


def person(entry):
    """Team entry [name, id, optional romanized name] -> markup that renders safely."""
    name, sid = entry[0], entry[1]
    roman = entry[2] if len(entry) > 2 and entry[2] else None
    if has_hangul(name):
        if KR_OK:
            return f'<font name="{KR_FONT}">{esc(name)}</font> ({esc(sid)})'
        if roman:
            return f"{esc(roman)} ({esc(sid)})"
        print("WARNING: no Korean font found; add a romanized name as a 3rd item in CONFIG['team'] "
              f"for {name}, otherwise it will not display in the PDF.")
    return f"{esc(name)} ({esc(sid)})"


def num(x, nd=0):
    try:
        return f"{float(x):,.{nd}f}"
    except (TypeError, ValueError):
        return "-"


def show(v, maxlen=40):
    if v is None:
        return "-"
    if isinstance(v, float):
        if v != v:
            return "-"
        return str(int(v)) if v.is_integer() else f"{v:,.2f}"
    s = str(v)
    return esc(s if len(s) <= maxlen else s[: maxlen - 1] + "...")


def table(rows, widths, header=True, first_col_bold=False):
    data = []
    for i, r in enumerate(rows):
        row = []
        for j, c in enumerate(r):
            st = CELLB if (header and i == 0) or (first_col_bold and j == 0) else CELL
            row.append(c if not isinstance(c, str) else Paragraph(c, st))
        data.append(row)
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    style = [
        ("GRID", (0, 0), (-1, -1), 0.4, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 1.6), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.6),
    ]
    if header:
        style.append(("BACKGROUND", (0, 0), (-1, 0), GREY))
    if first_col_bold:
        style.append(("BACKGROUND", (0, 0), (0, -1), GREY))
    t.setStyle(TableStyle(style))
    return t


def bullets(items):
    return [Paragraph(t, BUL, bulletText="\u2022") for t in items]


def build_report(R, fig_path, out_pdf):
    cfg = R["config"]
    A, B = cfg["dataset_a"], cfg["dataset_b"]
    M, Q, D, C = R["meta"], R["quality"], R["dups"], R["clean"]
    W = A4[0] - 3.0 * cm
    story = []

    # ------------------------------------------------------------------ header
    story.append(Paragraph("Final Project - Task 1: Data Exploration &amp; Service Idea", TITLE))
    story.append(Paragraph(
        f"Data Literacy Foundations, 2026 Fall &nbsp;|&nbsp; {esc(cfg['team_name'])}", SUB))
    story.append(Paragraph("Members: " + "; ".join(person(p) for p in cfg["team"]), SUB))
    story.append(Paragraph(f"Code repository (notebook + README): {esc(cfg['github_url'])}", SUB))

    # ------------------------------------------------------------------ 1. candidates
    story.append(Paragraph("1. Candidate Dataset Comparison", H1))
    bs = R.get("b_stats")
    size_b = (f"{bs['n_rows']:,} rows x {bs['n_cols']} columns (counted from the downloaded file)"
              if bs else esc(B["size"]))
    fields_a = ", ".join(esc(c) for c in M["columns"])
    rows = [
        ["", "Candidate A (selected)", "Candidate B"],
        ["Dataset", esc(A["name"]), esc(B["name"])],
        ["Source", esc(A["url"]), esc(B["url"])],
        ["One record is", "One cosmetics product with its ingredient list", esc(B["record"])],
        ["Size / fields", f"{M['n_rows']:,} rows x {M['n_cols']} columns (counted): {fields_a}", size_b],
        ["Possible service",
         "Ingredient finder and comparer: filter by skin type, ingredients to include or avoid and "
         "price; compare the ingredient lists of two products", esc(B["service"])],
        ["Access / license", "Free download from Kaggle (kagglehub). License: " + esc(A["license"]),
         esc(B["access"])],
        ["Limitations",
         "Small catalog (strict filters may leave few products); ingredient list is one text value that "
         "needs parsing; price currency and rating scale are not documented; a one-time snapshot.",
         esc(B["limitations"])],
    ]
    story.append(table(rows, [2.3 * cm, (W - 2.3 * cm) * 0.56, (W - 2.3 * cm) * 0.44], first_col_bold=True))
    story.append(Spacer(1, 3))
    skin_txt = (" and skin-type flag columns" if any("flag" in str(r[1]).lower() for r in R["key_fields"])
                else "")
    story.append(Paragraph(
        "<b>Selection rationale.</b> We select Candidate A because it combines the three things the service "
        f"needs in one table: the full ingredient list, the price and category{skin_txt}. These allow "
        "filtering by user choices and comparing products directly, whereas Candidate B offers fewer "
        "attributes to filter on. Both need the ingredient text to be parsed first; we accept this because "
        "the parsing is the core data operation of the service.", BODY))

    # ------------------------------------------------------------------ 2. profile
    story.append(Paragraph("2. Selected Dataset Profile", H1))
    dt = ", ".join(f"{v} {esc(k)}" for k, v in M["dtype_counts"].items())
    story.append(Paragraph(
        f"<b>Record meaning:</b> one cosmetics product. <b>Dimensions:</b> {M['n_rows']:,} rows x "
        f"{M['n_cols']} columns (types: {dt}); {M['n_categories']} product categories, {M['n_brands']} brands. "
        f"<b>Provenance:</b> Kaggle dataset {esc(A['url'])}. {esc(A['provenance'])}. Currency of "
        "<i>price</i> and the scale of the rating column are not documented; we treat them as given.", BODY))
    kf = [["Field", "Meaning", "Missing %", "Distinct"]] + [
        [esc(c), esc(m), f"{p:.1f}", f"{n:,}"] for c, m, p, n in R["key_fields"]]
    story.append(table(kf, [2.4 * cm, W - 2.4 * cm - 3.4 * cm, 1.6 * cm, 1.8 * cm]))
    story.append(Spacer(1, 3))
    sc = R["sample"]
    srows = [[esc(c) for c in sc["columns"]]] + [[show(v, 46) for v in r] for r in sc["rows"]]
    widths = [W * 0.17, W * 0.12, W * 0.11, W * 0.07, W * 0.07, W * 0.46]
    widths = widths[:len(sc["columns"])] if len(sc["columns"]) <= 6 else [W / len(sc["columns"])] * len(sc["columns"])
    scale = W / sum(widths)
    story.append(Paragraph("Sample records (first rows of the file; ingredient text shortened):", SMALL))
    story.append(table(srows, [w * scale for w in widths]))

    # ------------------------------------------------------------------ 3. quality
    story.append(Paragraph("3. Data Quality", H1))
    ds = R["describe"]
    cols = list(ds["data"].keys())
    drows = [["stat"] + [esc(c) for c in cols]]
    for k, stat in enumerate(ds["index"]):
        if stat in ("count", "mean", "50%", "min", "max"):
            drows.append([esc(stat)] + [num(ds["data"][c][k], 2) for c in cols])
    miss = [["Column", "Missing", "Missing %"]] + [[esc(c), f"{n:,}", f"{p:.1f}"] for c, n, p in R["missing_top"]]
    side = Table([[table(miss, [2.6 * cm, 1.6 * cm, 1.8 * cm]),
                   table(drows, [1.4 * cm] + [(W * 0.60 - 1.4 * cm) / len(cols)] * len(cols))]],
                 colWidths=[W * 0.40, W * 0.60])
    side.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    bn = D.get("brand_name")
    story.append(Paragraph(
        "<b>Missing and duplicate data.</b> Columns with the most missing values are on the left, "
        f"descriptive statistics on the right. Exact duplicate rows: {D['full']:,}"
        + (f"; rows repeating the same brand and product name: {bn:,}" if bn is not None else "")
        + "." + (f" Entirely empty columns: {esc(', '.join(R['all_null_cols']))}." if R["all_null_cols"] else ""),
        BODY))
    story.append(side)
    story.append(Spacer(1, 3))
    story.append(Paragraph(
        "<b>Issue that matters for the service - unusable ingredient lists.</b> "
        f"{Q['ingr_empty']:,} products have no parsable ingredient list and {Q['ingr_short']:,} more have fewer "
        f"than 3 items; {Q['ingr_placeholder']:,} ingredient texts contain placeholder-like wording "
        "(e.g., 'visit', 'no info', 'n/a'). The service answers 'does this product contain X?'; a product "
        "with an empty list would pass every 'avoid X' filter and be shown as if it were free of X, which "
        "is misleading. There are also "
        f"{Q['price_zero']:,} products with price 0 and {Q['price_missing']:,} with missing price. "
        f"For the exploration we exclude rows with price &lt;= 0 or fewer than {C['min_ingr']} parsed "
        f"ingredients: {C['n_removed']:,} rows ({C['pct_removed']:.1f}%) are removed, leaving "
        f"{C['n_clean']:,}. Final rules (and whether to flag instead of drop) are Task 2 work.", BODY))
    story.append(Paragraph(
        "<b>Other issues.</b> Ingredient names are inconsistent (spelling, brackets, synonyms; see "
        "Observation 3), so exact matching would miss products; they will be normalized in Task 2. "
        "Repeated brand/product rows should be de-duplicated, and units (currency, rating scale) are "
        "undocumented, so the service will show values as given.", BODY))

    # ------------------------------------------------------------------ 4. EDA
    story.append(Paragraph("4. Preliminary EDA (on the filtered rows)", H1))
    has_rating = any("median_rating" in r for r in R["category_table"])
    ct = [["Category", "Products", "Median price", "Median no. of ingredients"] + (["Median rating"] if has_rating else [])]
    for r in R["category_table"]:
        ct.append([esc(r["category"]), f"{int(r['products']):,}", num(r["median_price"], 2),
                   num(r["median_n_ingredients"], 0)] + ([num(r["median_rating"], 2)] if has_rating else []))
    n = len(ct[0])
    story.append(table(ct, [W * 0.28] + [W * 0.72 / (n - 1)] * (n - 1)))
    story.append(Spacer(1, 3))
    if os.path.exists(fig_path):
        story.append(Image(fig_path, width=W * 0.92, height=W * 0.92 * (3.4 / 9)))
    story.append(Paragraph("Figure 1. Ingredients found in the most usable products (left) and median price "
                           "by product category (right), computed from the filtered records.", SMALL))
    story.extend(bullets([f"<b>Observation 1.</b> {esc(R['obs'][0])}",
                          f"<b>Observation 2.</b> {esc(R['obs'][1])}",
                          f"<b>Observation 3.</b> {esc(R['obs'][2])}"]))

    # ------------------------------------------------------------------ 5. questions
    story.append(Paragraph("5. Analytical Questions", H1))
    qrows = [
        ["#", "Question", "Fields", "Operation", "Use on the website"],
        ["Q1", "Which ingredients appear most often in each product category?",
         "category, ingredients", "Split ingredient text; count products containing each ingredient; groupby category",
         "Show typical ingredients of a category so users can spot unusual or missing ones."],
        ["Q2", "Within a category, how do prices differ between products that contain a chosen ingredient and "
               "those that do not?", "price, category, ingredients",
         "Filter by ingredient; groupby; compare medians",
         "Give price context for the ingredients a user wants to include."],
        ["Q3", "For a given product, which products in the same category have the most similar ingredient "
               "list and a lower price?", "name, category, ingredients, price",
         "Jaccard similarity of ingredient sets; filter price lower; sort",
         "'Similar but cheaper' suggestions with shared and different ingredients."],
    ]
    story.append(table(qrows, [0.7 * cm, 5.0 * cm, 2.9 * cm, 4.0 * cm, W - 12.6 * cm]))

    # ------------------------------------------------------------------ 6. concept
    story.append(Paragraph("6. Service Concept", H1))
    story.append(Paragraph(
        "<b>Target users and need.</b> People who choose skincare by ingredients (wanting some, avoiding "
        "others) but must read long ingredient lists product by product. <b>Core interaction:</b> "
        "<i>User input</i> (skin type, ingredients to include or avoid, maximum price) -&gt; "
        "<i>Data operation</i> (parse and normalize the ingredient text; filter products by skin-type flag, "
        "price and ingredient matches; sort by rating) -&gt; <i>Useful result</i> (matching products with "
        "the ingredients that matched). A second interaction compares two products' ingredient lists "
        "(shared and different ingredients). The service will not label ingredients as harmful: users choose "
        "what to avoid; any safety notes would cite a public source.", BODY))
    P = R["prototype"]
    qd = P["query"]
    inc = ", ".join(esc(x) for x in qd["include"]) or "-"
    avd = ", ".join(esc(x) for x in qd["avoid"]) or "-"
    story.append(Paragraph(
        f"<b>Prototype 1 on the real data</b> (skin type: {esc(qd['skin'])}; include: {inc}; avoid: {avd}; "
        f"price &lt;= {num(qd['max_price'])}): {P['n_matches']:,} matching products; top rows:", SMALL))
    if P["rows"]:
        hdr = [esc(c) for c in P["columns"]]
        prow = [hdr] + [[show(v, 34) for v in r] for r in P["rows"]]
        story.append(table(prow, [W / len(hdr)] * len(hdr)))
    else:
        story.append(Paragraph("No product matched all criteria in this example.", SMALL))
    Cp = R["compare"]
    story.append(Spacer(1, 2))
    story.append(Paragraph(
        f"<b>Prototype 2:</b> reference product (highest price in category '{esc(Cp['category'])}'): "
        f"{show(Cp['ref'][0], 50)} ({show(Cp['ref'][1], 20)}, price {num(Cp['ref'][2], 2)}, "
        f"{Cp['ref'][3]} ingredients). Cheaper products in the same category with the most similar "
        f"ingredient lists ({Cp['n_candidates']:,} candidates):", SMALL))
    if Cp["rows"]:
        crow = [["Product", "Brand", "Price", "Jaccard similarity", "Shared ingredients"]]
        for r in Cp["rows"]:
            crow.append([show(r[0], 48), show(r[1], 20), num(r[2], 2), f"{float(r[3]):.2f}", f"{int(r[4])}"])
        story.append(table(crow, [W * 0.40, W * 0.20, W * 0.10, W * 0.15, W * 0.15]))
    story.append(Spacer(1, 2))
    miss_req = R["missing_required"]
    feas = [
        "<b>Fields available:</b> " + ("all required fields (name, category, price, ingredients) are present."
                                       if not miss_req else "MISSING: " + esc(", ".join(miss_req))),
        f"<b>Size and variety:</b> {C['n_clean']:,} usable products; {R['vocab_ge20']:,} distinct ingredient "
        "strings occur in at least 20 products, enough for common-ingredient filters. Rare ingredients "
        "will return few or no products, so the result page must say so.",
        "<b>Redistribution:</b> the CSV is not committed to GitHub; the README explains how to download it "
        "with kagglehub. License: " + esc(A["license"]) + ".",
        "<b>Data freshness:</b> a static snapshot is enough for the first feature; no API or user-generated "
        "records are needed.",
        "<b>Task 2 work:</b> normalize ingredient names (synonyms, brackets), decide how to treat products "
        "with missing lists, remove duplicates, and define matching rules (exact vs. contains).",
        "<b>First feature to implement:</b> skin type + include/avoid ingredients + price limit -&gt; "
        "filtered product list showing which ingredients matched.",
    ]
    story.extend(bullets(feas))
    story.append(Paragraph("All numbers above were computed by data_exploration.ipynb from the downloaded "
                           "Kaggle file; no record was edited by hand.", SMALL))

    doc = SimpleDocTemplate(out_pdf, pagesize=A4, leftMargin=1.5 * cm, rightMargin=1.5 * cm,
                            topMargin=1.3 * cm, bottomMargin=1.2 * cm,
                            title="Final Project Task 1 - Data Exploration & Service Idea",
                            author="; ".join(str(p[0]) for p in cfg["team"]))
    doc.build(story)
    return out_pdf


if __name__ == "__main__":
    out = "outputs"
    with open(os.path.join(out, "results.json"), encoding="utf-8") as f:
        results = json.load(f)
    print(build_report(results, os.path.join(out, "eda_figure.png"), os.path.join(out, "Task1_Report.pdf")))
