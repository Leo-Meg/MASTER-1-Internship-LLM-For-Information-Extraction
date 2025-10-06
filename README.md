# MASTER-1-Internship-LLM-For-Information-Extraction

## Table of Contents
1. [Project Overview](#overview)
2. [Folder Layout](#layout)
3. [Prerequisites](#prereq)
4. [Execution Pipeline](#pipeline)  
   - [Step 0 – PDF Parsing & Text Extraction](#step0)  
   - [Step 1 – Report Structuring](#step1)  
   - [Step 2 – Variable Definition & Target Sections](#step2)  
   - [Step 3 – Information Extraction via LLM](#step3)  
   - [Step 4 – Post-Processing & JSON Export](#step4)  
5. [Generated Artefacts](#artefacts)
6. [Testing & Validation](#tests)

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

pip install joblib

pip install -U pytest
```

<a name="pipeline"></a>
## 4. Execution Pipeline

Launch the full extraction process:

```sh
python pdf_extractor.py
```

This will parse all the pdfs in **data/pdfs/**, make calls to the llm on http://bigpu:8000/generate and extract the variables found in **data/data_to_extract.txt** into **tests/jsons_extracted/**

Below is a step-by-step explanation of the pipeline:

---

### **Step 0 – PDF Parsing & Text Extraction**

**Scripts:** utils/utils_parsing.py:get_pdf_content()`

**Input:** PDF files from `data/pdfs/`
**Output:** Cleaned text files stored in `data/text/`

**Process:**
1. Each PDF is parsed using `pypdf.PdfReader`.
2. Tables and numeric data are reformatted for readability.
3. Redundant newlines and footers are removed.
4. Clean text is saved as `{patient_id}.txt`.

---

### **Step 1 – Report Structuring**

**Scripts:** `utils/utils_parsing.py:clip_report()` & `utils/utils_parsing.py:extract_one_part_from_report()`
**Input:** Text reports (`data/text/*.txt`) & Section titles (`data/report_titles.txt`)
**Output:** Clipped report segments corresponding to key sections (e.g., *Examen clinique*, *Antécédents médicaux*).
**Process:** Report titles are used to delimit report sections, ensuring that LLM queries are restricted to relevant context only.

---

### **Step 2 – Variable Definition & Target Sections**

**File:** `data/data_to_extract.txt`
**Purpose:** Defines the variables to extract and their associated report sections. 
**Format Example:**
```text
- "asa_score" (int) the ASA score of the patient.
# Start, Stratégie anesthésique - Conclusion
```
This mapping guides the pipeline in identifying which sections to pass to the LLM for each variable.

---

### **Step 3 – Information Extraction via LLM**

**Scripts:** `pdf_extractor.py:make_big_requests()` & `utils/utils_llm.py:request_llm()`
**Input:** Clipped text segment & Variable definition (name, type, nullability, description)
**Output:** Intermediate JSON files with variable-value pairs
**Process:**
1. Build a JSON-formatted prompt for each variable.
2. Send it to the local LLM endpoint via HTTP POST.
3. Parse and validate the LLM's JSON response.
4. Store the result temporarily.
5. Run multiple extractions in parallel using `joblib.Parallel`.

**Example request:**

```bash
POST http://bigpu:8000/generate
{
  "prompt": "<anesthesia report extract...>",
  "max_tokens": 2048
}
```

---

### **Step 4 – Post-Processing & JSON Export**

**Scripts:**

* `utils/utils_json.py:combine_jsons()`
* `utils/utils_json.py:post_extraction()`
* `utils/utils_IO.py:write_jsonstr_to_file()`

**Output:**

* Final structured JSON files stored in `tests/jsons_extracted/`

**Process:**

1. Merge regex-based and LLM-based variables.
2. Compute derived values:

   * `IMC_calc` (BMI)
   * `PAM_calc` (Mean Arterial Pressure)
   * Boolean indicators (`insuffisance_cardiaque`, `insuffisance_renale_chronique`, `is_obese_calc`)
3. Write formatted JSON for each patient.


<a name="artefacts"></a>
## 5. Generated Artefacts
```
| File                                        | Description                                          |
| ------------------------------------------- | ---------------------------------------------------- |
| `data/text/{id}.txt`                        | Cleaned textual report extracted from PDF            |
| `tests/jsons_extracted/extracted_{id}.json` | Final JSON output with all extracted variables       |
| `tests/expected_output/{id}.json`           | Reference output for validation                      |
| `logs/` (optional)                          | Console logs during extraction (if `print_log=True`) |
```
Each JSON file contains structured key/value pairs ready for downstream analysis.

<a name="tests"></a>
## 6. Testing & Validation

You can validate extraction accuracy using the included test suite:
```
pytest tests/test_suite.py
```
This script compares each generated JSON against a reference file in tests/expected_output/ and reports: *missing or extra keys* and *value mismatches*.


```text
Megret L., 2025. Information extraction from anesthesia reports using a Large Language Model. Département de recherche en anesthésie, Hôpital Laribroisière
```
