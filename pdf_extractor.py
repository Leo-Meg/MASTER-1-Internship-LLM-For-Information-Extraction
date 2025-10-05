import json
import os
from joblib import Parallel, delayed

from utils.utils_parsing import parse_variable_line, parse_comment_line, get_pdf_content, clip_report, extract_regex_variables
from utils.utils_llm import request_llm
from utils.utils_IO import write_jsonstr_to_file
from utils.utils_json import combine_jsons, post_extraction


package_dir = os.path.abspath(os.path.dirname(__file__))
VARIABLES_TO_EXTRACT_PATH = os.path.normpath(os.path.join(package_dir, './data/data_to_extract.txt'))
PDFS_DIRECTORY_PATH = os.path.normpath(os.path.join(package_dir, './data/pdfs'))
TITLES_PATH = os.path.normpath(os.path.join(package_dir, './data/report_titles.txt'))
TEXT_DIRECTORY_PATH = os.path.normpath(os.path.join(package_dir, './data/text/'))
JSONS_EXTRACTED_DIRECTORY_PATH = os.path.normpath(os.path.join(package_dir, './tests/jsons_extracted/'))


def make_big_requests(line:list, report:str, print_log:bool, verif_count:int=1) -> str:

    mjsons = []
    
    key_name, key_type, nullable, variable_explanation = parse_variable_line(line)
    
    for _ in range (verif_count):

        result = request_llm(report, key_name, key_type, nullable, variable_explanation, print_log)
        mjsons.append(result)

    possible_values = []
    possible_values_count = []

    for mjson in mjsons:
        curr_value = mjson[key_name]
        found= False
        i = 0
        while (not found) and i < (len(possible_values)):
            if possible_values[i] == curr_value:
                possible_values_count[i]+=1
                found = True
            i+=1
        if not found:
            possible_values.append(curr_value)
            possible_values_count.append(1)

    max_id = 0
    curr_max = 0
    for u in range (len(possible_values)):
        if possible_values_count[u]>curr_max:
            max_id = u
            curr_max = possible_values_count[u]

    return json.dumps({key_name:possible_values[max_id]})


def extract_info_patient(patient_id:str, parallelize_request:bool,
                         print_log:bool) -> str:
    
    report = get_pdf_content(TEXT_DIRECTORY_PATH, patient_id, os.path.join(PDFS_DIRECTORY_PATH, patient_id + ".pdf"))

    json_extracted_path = os.path.join(JSONS_EXTRACTED_DIRECTORY_PATH, "extracted_" + patient_id + ".json")

    var_lines = []
    reports_clipped = []

    with open(VARIABLES_TO_EXTRACT_PATH, "r") as file:
        for line in file:
            if (not line.strip() or line[0] == "/"):
                continue
            if line[0] == "#":
                repport_clipped = clip_report(TITLES_PATH, report, parse_comment_line(line))
                reports_clipped.append(repport_clipped)
            else:
                var_lines.append(line)
                
    if (len(var_lines) != len(reports_clipped)):
        raise Exception("There should be as many comments_lines as variable_lines")

    full_json = combine_jsons(extract_regex_variables(report), "")

    if (parallelize_request):
        jsons = Parallel(n_jobs=len(var_lines))(delayed(make_big_requests)(var_lines[i], reports_clipped[i], print_log) for i in range(len(var_lines)))

        for curr_json in jsons:
            full_json = combine_jsons(curr_json, full_json)

        full_json = post_extraction(full_json)
        write_jsonstr_to_file(json_extracted_path, full_json)
    else :
        for i in range (len(var_lines)):
            full_json = combine_jsons(make_big_requests(var_lines[i], reports_clipped[i], print_log), full_json)

            full_json = post_extraction(full_json)
            write_jsonstr_to_file(json_extracted_path, full_json)

    return full_json


def extract_info_all_patients():

    patients_ids = []
    cohort_size = 8

    for filename in os.listdir(PDFS_DIRECTORY_PATH):
        if (".pdf" in filename):
            name, extension = os.path.splitext(filename)
            patients_ids.append(name)

    patients_ids_arrays = []
    for i in range(0, len(patients_ids), cohort_size):
        patients_ids_arrays.append(patients_ids[i:i+cohort_size])

    for patient_id_array in patients_ids_arrays:
        Parallel(n_jobs=len(patient_id_array))(delayed(extract_info_patient)(patient_id_array[i], True, False) for i in range (len(patient_id_array)))
    



# extract_info_all_patients()
# extract_info_patient("8003166895", False, True)
