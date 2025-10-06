# MASTER-1-Internship-LLM-For-Information-Extraction

## Table of Contents
1. [Project Overview](#overview)
2. [Folder Layout](#layout)
3. [Prerequisites](#prereq)
4. [Installation](#install)
5. [Execution Pipeline](#pipeline)  
   - [Step 0 – PDF Parsing & Text Extraction](#step0)  
   - [Step 1 – Report Structuring](#step1)  
   - [Step 2 – Variable Definition & Target Sections](#step2)  
   - [Step 3 – Information Extraction via LLM](#step3)  
   - [Step 4 – Post-Processing & JSON Export](#step4)  
6. [Generated Artefacts](#artefacts)
7. [Testing & Validation](#tests)

---

<a name="overview"></a>
## 1. Project Overview

This project automates **information extraction from anesthesia reports** using a **Large Language Model (LLM)** deployed locally (endpoint: `http://bigpu:8000/generate`).  
It processes raw PDF reports, segments them into structured sections, and extracts predefined clinical variables (e.g., ASA score, hypertension, BMI, biological measures).  

The system:
- Converts PDFs to text.
- Uses section titles to delimit report parts (e.g., “Examen clinique”, “Antécédents médicaux”).
- Extracts variables defined in `data/data_to_extract.txt`.
- Sends targeted prompts to the LLM for each variable.
- Validates and combines results into structured JSON files per patient.

---

<a name="layout"></a>
## 2. Folder Layout

```
MASTER-1-Internship-LLM-For-Information-Extraction/
│
├── data/
│   ├── pdfs/                 # Input PDFs (raw anesthesia reports)
│   ├── text/                 # Text extracted from PDFs
│   ├── report_titles.txt     # Section titles used to clip reports
│   ├── data_to_extract.txt   # Variables to extract (definitions + section mapping)
│
├── tests/
│   ├── test_suite.py         # Pytest suite comparing extracted vs expected outputs
│   ├── expected_output/      # Reference JSONs (expected results)
│   └── jsons_extracted/      # Generated JSONs after extraction
│
├── utils/
│   ├── utils_IO.py           # File I/O helpers (read/write JSON/text)
│   ├── utils_json.py         # JSON merging and post-processing (BMI, PAM, etc.)
│   ├── utils_llm.py          # LLM request formatting, validation, retries
│   └── utils_parsing.py      # PDF parsing, section clipping, regex-based pre-extraction
│
└── pdf_extractor.py          # Main pipeline launcher
```

---

<a name="prereq"></a>
## 3. Prerequisites

System dependencies:
```bash
sudo dnf install poppler-utils
```


Python dependencies:

```sh
sudo dnf install poppler-utils

pip install joblib

pip install -U pytest
```


# Launch extraction

```sh
python pdf_extractor.py
```

This will parse all the pdfs in **data/pdfs/**, make calls to the llm on http://bigpu:8000/generate and extract the variables found in **data/data_to_extract.txt** into **tests/jsons_extracted/**


# Project structure

- **data/**
    - **data/pdfs**
        - contains the raw anesthesia report pdfs
    - **data/text**
        - contains the text extracted from the pdfs
    - **data/report_titles.txt**
        - all the titles possible in the anesthesia report
        - this file is used by the extractor to delimit the parts of the report
    - **data/data_to_extract.txt**
        - contains the variables that we want to extract from the reports

- **tests**
    - **tests/test_suite.py**
        - the test suite
    - **tests/expected_output/**
        - the expected jsons after the pdf extraction
    - **tests/jsons_extracted/**
        - the actual jsons extracted

- **utils/**
    - contains the functions necessary to pdf_extractor.py

- **pdf_extractor.py**
    - the root script
    - launch it to extract all data from all patients
