import requests
import json
import time


def build_prompt(data_to_extract : list, key_name:str, key_type:str, mreport : str) -> str:

    full_prompt = mreport
    type_explanation = "either \"true\" or \"false\"."
    null_txt = " Should be false if not found."
    if ("int" in key_type):
        type_explanation = "a number."
        null_txt = " Should be null if not found."

    if ("float" in key_type):
        type_explanation = "a number, potentially decimal, but not necessarily."
        null_txt = " Should be null if not found."

    full_prompt +="--------------------------------------------------------------------------\n\n"
    full_prompt += "From this anesthesia report extract, return the following variable :\n\n"

    full_prompt += '\n' + data_to_extract
    full_prompt += "\n\n"

    full_prompt += ("Your should reply ONLY with a VALID RAW JSON containing ONLY ONE element, its key being : \"" + key_name + "\".\n")

    full_prompt += "The corresponding value should be of type "+key_type+", so it should be "+type_explanation+ null_txt
    return full_prompt


def request_llm(report : str, key : str, mtype : str, nullable:bool, variable_explanation:str, print_log :bool = False) -> dict:

    system_message = "Your are a virtual assistant, expert in alaysing anesthesia reports. You reply to user queries only with VALID JSON"
    prompt = build_prompt(variable_explanation, key, mtype, report)

    full_prompt = f'<|im_start|>system{system_message}<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant'

    if (print_log):
        print(full_prompt+"\n\n")


    payload = {
        "prompt": full_prompt,
        "max_tokens": 2048,
    }

    for _ in range(50):
        try:
            is_output_valid = False
            i = 0
            while (not is_output_valid and i < 3):
                response = requests.post("http://bigpu:8000/generate", json=payload)
                response.raise_for_status()
                output = response.json()['text'][0].replace(full_prompt, '')

                message_content_json, is_output_valid = make_json_valid(output, key, mtype, nullable)
                i+=1
            
                if (print_log):
                    print("\nRESPONSE : ", output)

            return message_content_json
                
        except Exception as e:
            print(e)
            time.sleep(10)

        raise Exception("giving up, too many request.")


def make_json_valid(json_txt:str, key_expected:str, type_expected:str, nullable:bool) -> dict:
   
    start_index = json_txt.find('{')
    end_index = json_txt.rfind('}')
    
    valid_json = json_txt[start_index:end_index+1]
    valid_json = valid_json.replace("False", "false")
    valid_json = valid_json.replace("True", "true")
    valid_json = valid_json.replace("None", "null")

    valid_json = valid_json.replace("'", '"')

    try:
        json_loaded = json.loads(valid_json)

        if (key_expected in json_loaded):

            bool_validated = isinstance(json_loaded[key_expected], bool) and "bool" in type_expected
            int_validated = isinstance(json_loaded[key_expected], int) and "int" in type_expected
            float_validated = (isinstance(json_loaded[key_expected], float) or isinstance(json_loaded[key_expected], int)) and "float" in type_expected
            none_validated = json_loaded[key_expected] is None and ((not "bool" in type_expected) or (nullable))

            if bool_validated or int_validated or float_validated or none_validated:
                return json_loaded, True
        
    except json.JSONDecodeError as e:
        print(e)
        print("JSON can't be made valid, initial JSON : " + json_txt + ", final JSON : " + valid_json)

    if ("bool" in type_expected and not nullable):
        return {key_expected:False}, False 
    
    return {key_expected:None}, False 
