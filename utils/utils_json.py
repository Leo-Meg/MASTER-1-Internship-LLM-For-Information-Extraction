import re
import json


def combine_jsons(json_str1:str, json_str2:str)-> str:

    if (not json_str2):
        return json_str1
    if (not json_str1):
        return json_str2
    
    json_dict1 = json.loads(json_str1)
    json_dict2 = json.loads(json_str2)

    combined_dict = json_dict2.copy()
    combined_dict.update(json_dict1)

    combined_json_str = json.dumps(combined_dict)

    return combined_json_str


def post_extraction(json_str:str):

    mjson = json.loads(json_str)

    #Calculate BMI

    if "height_cm" in mjson and "weight_kg" in mjson:
        if mjson["weight_kg"] is not None and mjson["height_cm"] is not None:
            imc_calculated = (mjson["weight_kg"]) / ((mjson["height_cm"])/100)**2

            mjson["IMC_calc"] = (int(imc_calculated * 10))/10

    # calculate PAM
                
    if "PAS" in mjson and "PAD" in mjson:
        if mjson["PAS"] is not None and mjson["PAD"] is not None:
            pam_calculated = ((mjson["PAS"]) +  2 * (mjson["PAD"]))/3
            mjson["PAM_calc"] = (int(pam_calculated * 10))/10
 

    # If "FEVG" < 50% then "insuffisance_cardiaque" = true

    if "FEVG" in mjson and mjson["FEVG"] is not None:
        if mjson["FEVG"] < 50:
            mjson["insuffisance_cardiaque"] = True

    # if "DFG" < 60 then "insuffisance_renale_chronique" = true
                
    if "DFG" in mjson and mjson["DFG"] is not None:
        if mjson["DFG"] < 60:
            mjson["insuffisance_renale_chronique"] = True

    if ("IMC_calc" in mjson and mjson["IMC_calc"] is not None):
        mjson["is_obese_calc"] = mjson["IMC_calc"] > 30

    return json.dumps(mjson)
