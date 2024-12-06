# Shaimae Elhajjajy
# August 20, 2024
# Determine (programatically) the number of papers citing the ENCODE3 paper, 
# and the extent of their reference to the Registry.

# Import libraries
import fitz # ( from PyMuPDF, for PDF parsing )
import itertools
import os # for basename
import re # for regex
import sys

# Read from command line
if len(sys.argv) != 2:
    sys.exit("Enter the path to the PDF file for parsing.")
             
path_to_pdf = sys.argv[1]

# Regex matching
# keywords = ["SCREEN", "Registry", "rDHS", "cCRE", "CCRE", \
#             "PLS", "pELS", "dELS", "promoter-like", "enhancer-like", \
#             "proximal enhancers", "distal enhancers", "EH38E", \
#             r"screen\.encodeproject\.org", r"screen\.encodeproject\.", r"screen\."]
keywords = ["SCREEN", "Registry of candidate cis-regulatory elements", "Registry of cCREs", "rDHS", "cCRE", \
            "PLS", "pELS", "dELS", \
            "EH38E", r"screen\.encodeproject\.org", r"screen\.encodeproject\."]

# Create a hierarchy of keywords: For example, if ENCODE appear in a sentence, check if "cCREs" or "cis-regulatory" appears in the same sentence


figures = [r'\(Figure \d+', r'\(Figures \d+', \
            r'\(Fig. \d+', r'\(Figs. \d+', \
            r'\(fig. \d+', r'\(figs. \d+']
suppl_figures = [r'\(Figure S\d+', r'\(Figures S\d+', \
                r'\(Fig. S\d+', r'\(Figs. S\d+', \
                r'\(fig. S\d+', r'\(figs. S\d+', \
                r'\(Supplementary Figure \d+', r'\(Supplementary Figures \d+', \
                r'\(Supplementary Fig. \d+', r'\(Supplementary Figs. \d+', \
                r'\(Supplementary Figure S\d+', r'\(Supplementary Figures S\d+', \
                r'\(Supplementary Fig. S\d+', r'\(Supplementary Figs. S\d+']
ext_figures = [r'\(Extended Data Figure \d+', r'\(Extended Data Figures \d+', \
                r'\(Extended Data Fig. \d+', r'\(Extended Data Figs. \d+']
tables = [r'\(Table \d+', r'\(Tables \d+', \
            r'\(table \d+', r'\(tables \d+']
suppl_tables = [r'\(Table S\d+', r'\(Tables S\d+', \
                r'\(table S\d+', r'\(tables S\d+', \
                r'\(Supplementary Table \d+', r'\(Supplementary Tables \d+', \
                r'\(Supplementary Table S\d+', r'\(Supplementary Tables S\d+', \
                r'\(S\d+ Table', r'\(S\d+ Tables']

features = figures + suppl_figures + ext_figures + tables + suppl_tables

# ------------------------------------------------ FUNCTIONS ------------------------------------------------

def extract_sentences_blocks(chunk_as_string):
    # Split chunk into sentences (need to account for multiple delimiters based on PDF formatting)
    sentences = re.split(r'(?<!Fig)(?<!Figs)(\. )', chunk_as_string)
    sentences = [re.split(r'\.\n', x) for x in sentences]
    sentences = list(itertools.chain.from_iterable(sentences))
    # Remove delimiters that are present as individual list elements
    sentences = [x for x in sentences if (x != ". ") and (x != " \n")]
    # Stitch words that were hyphenated on syllables b/c of a newline
    sentences = [x.replace("-\n", "") for x in sentences]
    # Remove newlines in the middle of a sentence
    sentences = [x.replace(" \n", " ") for x in sentences]
    # Remove ASCII characters
    sentences = [x.replace(u'\xa0', ' ') for x in sentences]
    # # Remove citation numbers (superscripts from PDF appended as digits to preceding word)
    # sentences = [re.sub(r"(?<![^a-zA-Z])\d+", "", x) for x in sentences]
    return(sentences)

def extract_paragraphs_blocks(chunk_as_string):
    # Split chunk into paragraphs based on ".\n" delimiter (note: this doesn't account for cases where a paragraph
    # is already split across columns or pages)
    paragraphs = re.split(r'\.\n', chunk_as_string)
    # Remove any empty elements in the split list (occurs if the paragraph is the last element in the chunk)
    paragraphs = [x for x in paragraphs if (x != "")]
    # Stitch words that were hyphenated on syllables b/c of a newline
    paragraphs = [x.replace("-\n", "") for x in paragraphs]
    # Remove newlines in the middle of a sentence
    paragraphs = [x.replace(" \n", " ") for x in paragraphs]
    # Remove ASCII characters
    paragraphs = [x.replace(u'\xa0', ' ') for x in paragraphs]
    # # Remove citation numbers (superscripts from PDF appended as digits to preceding word)
    # paragraphs = [re.sub("(?<![^a-zA-Z])\d+", "", x) for x in paragraphs]
    return(paragraphs)

# Parse text from a single page into (1) sentences and (2) paragraphs
# Note: does not differentiate between main text and figure captions
def parse_page_blocks(page):
    text = page.get_text("blocks")
    all_sentences = []
    # all_paragraphs = []
    for chunk in text:
        # Remove any floating points at the beginning or end of the chunk
        chunk_as_list = [x for x in chunk if isinstance(x, str)]
        # Collapse list of strings into one full string for parsing
        chunk_as_string = "".join(list(chunk_as_list))
        # Extract sentences from this chunk
        sentences = extract_sentences_blocks(chunk_as_string)
        all_sentences += sentences
        # # Extract paragraphs from this chunk
        # paragraphs = extract_paragraphs_blocks(chunk_as_string)
        # # print(paragraphs)
        # all_paragraphs += paragraphs
    # return(all_sentences, all_paragraphs)
    return(all_sentences)

def extract_sentences_text(chunk_as_string):
    # Split sentences based on a period + space, but not when it precedes a Figure abbreviation
    sentences = re.split(r'(?<!Fig)(?<!Figs)(\. )', chunk_as_string)
    # # Remove citation numbers (superscripts from PDF appended as digits to preceding word)
    sentences = [re.split(r'\.\d+', x) for x in sentences]
    sentences = list(itertools.chain.from_iterable(sentences))
    # Remove delimiters that are present in the list as individual elements
    sentences = [x for x in sentences if (x != ". ")]
    # Stitch words that were hyphenated on syllables b/c of a newline
    sentences = [x.replace("-\n", "") for x in sentences]
    # Remove newlines in the middle of a sentence
    sentences = [x.replace(" \n", " ") for x in sentences]
    # Remove newlines at the beginning of a sentence
    sentences = [x.lstrip("\n") for x in sentences]
    # Remove ASCII characters (occurs for some papers)
    sentences = [x.replace(u'\xa0', ' ') for x in sentences]
    return(sentences)

def parse_page_text(page):
    text = page.get_text("text")
    # Split paragraphs based on a period + newline
    text_split = text.split(".\n")
    all_sentences = []
    for chunk in text_split:
        all_sentences += extract_sentences_text(chunk)
    return(all_sentences)

# Based on detected keywords and features, classify the document into a category based on 
# the priority order (high amount of usage to low amount of usage)
def classify_document(doc_class_list):
    # Feature
    if ("main_figure" in doc_class_list):
        pred_doc_class = "main_figure"
        return(pred_doc_class)
    elif ("suppl_figure" in doc_class_list):
        pred_doc_class = "suppl_figure"
        return(pred_doc_class)
    elif ("ext_data_figure" in doc_class_list):
        pred_doc_class = "ext_data_figure"
        return(pred_doc_class)
    elif ("table" in doc_class_list):
        pred_doc_class = "table"
        return(pred_doc_class)
    elif ("suppl_table" in doc_class_list):
        pred_doc_class = "suppl_table"
        return(pred_doc_class)

    # Text-only
    elif ("screen" in doc_class_list):
        pred_doc_class = "screen"
        return(pred_doc_class)
    elif ("text" in doc_class_list):
        pred_doc_class = "text"
        return(pred_doc_class)
    elif ("citation" in doc_class_list):
        pred_doc_class = "citation"
        return(pred_doc_class)

# -------------------------------------------------- MAIN --------------------------------------------------

doc = fitz.open(path_to_pdf)
num_pages = len(doc)

# Extract metadata for the paper
pdf = os.path.basename(path_to_pdf)
# author = pdf.split("_")[0]
# journal = pdf.split("_")[1]
# year = pdf.split("_")[2]
# true_doc_class = pdf.split("_")[3].split(".")[0]
# citation = author + "_" + journal + "_" + year
title = doc.metadata["title"]

sentence_hits_per_page = {i : [] for i in range(0, num_pages)}
single_keyword_hits_per_page = {i : [] for i in range(0, num_pages)}

citation_detected = False

for page_num in range(0, num_pages):
    page = doc[page_num]
    # Organize text on this page into sentences or paragraphs
    # sentences = parse_page_blocks(page)
    sentences = parse_page_text(page)
    # print(sentences)
    # First, check whether pairs occur in the same sentence (greater resolution)
    num_hits_sentences = 0
    num_hits_single_keywords = 0
    for s in range(0, len(sentences)):
        sentence = sentences[s]
        # First pass: check if ANY combination occurs (instead of exhaustively checking every possible combination)
        keyword_hits = [x for x in keywords if re.search(x, sentence)]
        feature_hits = [x for x in features if re.search(x, sentence)]
        if ((len(keyword_hits) != 0) and (len(feature_hits) != 0)):
            sentence_hits_per_page[page_num].append({"index" : s, "sentence" : sentence, \
                                                        "keywords": keyword_hits, "features" : feature_hits})
            num_hits_sentences += 1
    # print(sentence_hits_per_page[page_num])
    # If no pairs, check for single occurrences of keywords (for text only category)
    # Note: use paragraphs instead of sentences, b/c resolution is not important here
    if (num_hits_sentences == 0):
        for s in range(0, len(sentences)):
            sentence = sentences[s]
            keyword_hits = [x for x in keywords if re.search(x, sentence)]
            if (len(keyword_hits) != 0):
                single_keyword_hits_per_page[page_num].append({"index" : s, "sentence" : sentence, \
                                                                "keywords": keyword_hits})
                num_hits_single_keywords += 1
    # Check for citation-only (in the case when no keywords occur)
    if (num_hits_single_keywords == 0):
        citation_detected = True
        # for s in range(0, len(sentences)):
        #     sentence = sentences[s]
        #     if ((re.search("Expanded\nencyclopaedias", sentence)) or \
        #         (re.search("Expanded encyclopaedias", sentence)) or \
        #         (re.search("Expanded encyclopaedi-", sentence)) or \
        #         (re.search("Expanded encyclopae-", sentence)) or \
        #         (re.search("Expanded encyclo-", sentence)) or \
        #         (re.search("Expanded ency-", sentence)) or \
        #         (re.search("Expanded en-", sentence)) or \
        #         (re.search("Expan-", sentence)) or \
        #         (re.search("Ex-", sentence))):
        #         citation_detected = True

# If pairs detected in the text, classify into the appropriate category
# Categories (in order of precedence):
# - keyword + Fig(s) : Main figure
# - keyword + Supplementary/Suppl Fig(s) : Supplementary figure
# - keyword + Table(s) : Table
# - keyword + Supplementary/Suppl Table(s) : Supplementary table
# - keyword + Supplementary/Suppl Note(s) : Notes

doc_class_list = []

for page_num in sentence_hits_per_page.keys():
    if (len(sentence_hits_per_page[page_num]) != 0):
        for hit in sentence_hits_per_page[page_num]:
            figure_hits = [x for x in figures if x in hit["features"]]
            if (len(figure_hits) != 0):
                doc_class_list.append("main_figure")
            suppl_figure_hits = [x for x in suppl_figures if x in hit["features"]]
            if (len(suppl_figure_hits) != 0):
                doc_class_list.append("suppl_figure")
            ext_figure_hits = [x for x in ext_figures if x in hit["features"]]
            if (len(ext_figure_hits) != 0):
                doc_class_list.append("ext_data_figure")
            table_hits = [x for x in tables if x in hit["features"]]
            if (len(table_hits) != 0):
                doc_class_list.append("table")
            suppl_table_hits = [x for x in suppl_tables if x in hit["features"]]
            if (len(suppl_table_hits) != 0):
                doc_class_list.append("suppl_table")

# If no pairs detected in the text, but single keywords are, classify into the appropriate category
# Categories (in order of precedence):
# - hit for SCREEN : SCREEN-only
# - hit for other keywords : Text-only
# - no keyword hits but hit for citation : Citation-only
if (len(doc_class_list) == 0):
    for page_num in single_keyword_hits_per_page.keys():
        if (len(single_keyword_hits_per_page[page_num]) != 0):
            for hit in single_keyword_hits_per_page[page_num]:
                screen_hits = [x for x in hit["keywords"] if re.search("SCREEN", x)]
                screen_hits += [x for x in hit["keywords"] if re.search("screen", x)]
                if (len(screen_hits) != 0):
                    doc_class_list.append("screen")
                elif (len(screen_hits) == 0):
                    doc_class_list.append("text")

if (len(doc_class_list) == 0):
    if (citation_detected):
        doc_class_list.append("citation")

if (len(doc_class_list) != 0):
    doc_class_unique = list(set(doc_class_list))
    pred_doc_class = classify_document(doc_class_unique)
    print(pdf +  "\t" + pred_doc_class)
    # print(journal, true_doc_class, pred_doc_class)



