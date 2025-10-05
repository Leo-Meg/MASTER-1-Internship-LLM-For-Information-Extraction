import re
import os
from pypdf import PdfReader
import json

def extract_one_part_from_report(titles_path:str, report:str, part_to_extract:str)->str:

    with open(titles_path, 'r') as file:
        titles = [line.strip().replace("(", "").replace(")", "").strip() for line in file if "Start" not in line]


    index_start = report.find(part_to_extract)
    if index_start == -1:
        if (part_to_extract == "Start"):
            index_start = 0
        else:
            return "" 

    index_end = len(report)

    for title in titles:
        index = report.find(title)
        if index != -1 and index < index_end and index>index_start:
            index_end = index

    return report[index_start:index_end]


def clip_report(titles_path:str, report:str, parts_to_keep:list[str]) -> str:
    res = ""

    for part in parts_to_keep:
        res += (extract_one_part_from_report(titles_path, report, part) + "\n\n\n")

    if (not res.strip()):
        res = report

    return res

def parse_variable_line(curr_line:str) -> tuple[str, str]:

    el_nullability = "[NULLABLE]" in curr_line

    curr_line_clean = (curr_line.replace("[NULLABLE]", "")).replace("\"temp_", "\"")

    el_key = (re.search(r'"([^"]+)"', curr_line_clean)).group(1)
    el_type = (re.search(r'\(([^)]+)\)', curr_line_clean)).group(1)

    return el_key, el_type, el_nullability, curr_line_clean


def parse_comment_line(curr_line:str) -> list[str]:
    curr_line = curr_line.replace("?", "")
    curr_line = (curr_line[1:]).strip()
    titles = curr_line.split(',')

    for i in range (len(titles)):
        titles[i] = titles[i].strip()

    return titles


def extract_regex_variables(report:str) -> str:
    # for now, we extract only MET_superior_to_4 through regex

    MET_superior_to_4 = None

    MET_line = (re.search(r'Echelle de Duke :([^\n]+)\n', report))

    if (MET_line):
        MET_line = MET_line.group(1)

        two_numbers = (re.search(r'(\d+)\D+(\d+)', MET_line))
        one_number = (re.search(r'(\d+)', MET_line))

        if (two_numbers):
            nb1 = int(two_numbers.group(1))
            nb2 = int(two_numbers.group(2))

            MET_superior_to_4 = min(nb1, nb2)>=4

        elif (one_number):

            inferior = MET_line.find('<')
            superior = MET_line.find('>')

            if (inferior != -1 or superior != -1):
                MET_superior_to_4 = (superior != -1)


    mjson = {"MET_superior_to_4" : MET_superior_to_4}

    return json.dumps(mjson)


def get_pdf_content(text_directory_path:str, patient_id:str, pdf_file_path:str, print_chart_line=False)->str:

    reader = PdfReader(pdf_file_path)
    fulltxt = ""

    for i in range (len(reader.pages)):
        fulltxt += reader.pages[i].extract_text(extraction_mode="layout")
    

    # 1. improves chart readibility

    fulltxt2 = ""
    lines = fulltxt.split('\n')
    
    for line in lines:
        columns = line.split('¦')
        # '¦' is different than '|'
        # Therefore, this method targets only lines with 4 '¦'
        
        if (len(columns) == 5):
            if (print_chart_line):

                print("an interesting line : ")
                print(line)

            content1 = columns[-3].strip()
            content2 = columns[-2].strip()
        
            name = columns[0].rstrip()

            content1_clean = (re.search(r'([\-\+]{0,1}[ ]*?[\d\.]+)', content1))
            content2_clean = (re.search(r'([\-\+]{0,1}[ ]*?[\d\.]+)', content2))

            full_content = ""
            
            if (content1_clean):
                full_content = content1_clean.group(1)
            if (content2_clean):
                if full_content:
                    full_content += " | "
                full_content += content2_clean.group(1)

            fulltxt2 += (name+ " : "+ full_content + "\n")

            if (print_chart_line):
                print("new line : ")
                print(name+ " : "+ full_content + "\n")
        else:
            fulltxt2 += line+ "\n"
    fulltxt = fulltxt2

    # 2. removes useless \n
    fulltxt = re.sub(r'\n{3,}', '\n\n', fulltxt)

    # 3. This regex removes footers
    fulltxt = re.sub(r'Pat\.: [\s\S]+?(\d/\d)(?=\D|$)', "", fulltxt)

    fulltxt = fulltxt.strip()

    #for logs
    with open(os.path.join(text_directory_path,patient_id+".txt"), "w") as file:
        file.write(fulltxt)

    return fulltxt
