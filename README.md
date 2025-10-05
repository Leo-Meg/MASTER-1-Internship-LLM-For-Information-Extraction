# MASTER-1-Internship-LLM-For-Information-Extraction

# Download the necessary tools

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
