import pytest
import subprocess
import time
import json
import os

from pdf_extractor import extract_all

package_dir = os.path.abspath(os.path.dirname(__file__))

SHELL_SCRIPT_PATH = os.path.normpath(os.path.join(package_dir, '../data/convert_pdf_to_txt.sh'))
COMPTE_RENDU_DIRECTORY_PATH = os.path.normpath(os.path.join(package_dir, '../data/text/'))
EXPECTED_OUTPUT_DIRECTORY_PATH = os.path.normpath(os.path.join(package_dir, './expected_output/'))
EXTRACTED_INFOS_DIRECTORY_PATH = os.path.normpath(os.path.join(package_dir, './jsons_extracted/'))

@pytest.fixture(scope="session", autouse=True)
def convert_pdf_to_txt():
    subprocess.run(SHELL_SCRIPT_PATH, shell=True)
    
    time.sleep(1)
    yield


def are_dicts_same(mdict:dict, expected_dict:dict):
    missing_keys = []
    extra_keys = []

    different_values = []

    for key in expected_dict.keys():
        if key not in mdict:
            missing_keys.append(key)
        elif mdict[key] != expected_dict[key]:
            different_values.append((key, mdict[key], expected_dict[key]))

    for key in mdict.keys():
        if key not in expected_dict:
            extra_keys.append(key)

    are_same = not (missing_keys or extra_keys or different_values)

    print("Dict:", mdict, "\n")
    print("Expected Dict:", expected_dict)

    diff_recap = "missing_keys: {}, extra_keys: {}, different values: {}".format(
        missing_keys, extra_keys, different_values)

    return are_same, diff_recap


def test_patient_8003166895():
    curr_patient_id = "8003166895"
    expected_output_file = os.path.normpath(os.path.join(EXPECTED_OUTPUT_DIRECTORY_PATH, 
                                        curr_patient_id+".json"))

    compte_rendu_path = os.path.normpath(os.path.join(COMPTE_RENDU_DIRECTORY_PATH, 
                                      curr_patient_id+".txt"))
    extracted_infos_file = os.path.normpath(os.path.join(EXTRACTED_INFOS_DIRECTORY_PATH, 
                                                         "extracted_" + curr_patient_id +".json"))
    with open(expected_output_file, "r") as file:  
        reference_dict = json.load(file)

    mydict = json.loads(extract_all(compte_rendu_path = compte_rendu_path, 
                                    to_file=extracted_infos_file,
                         variables_per_request=3))

    dicts_equals, diff_recap = are_dicts_same(mydict, reference_dict)
    assert dicts_equals, diff_recap
