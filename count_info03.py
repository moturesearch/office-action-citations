'''
Count number of citations with each piece of info.

This code loops through the files (and the citations within the files). These files are from Grobid (not consolidated).
The code creates a csv file (where one line = one citation) for each Grobid input file. 
This csv file contains a binary variable for each piece of info (1=present, 0=not present).
'''

from bs4 import BeautifulSoup
from hashlib import md5
from openalex_functions_v6 import get_title, get_author_id, get_year, get_journal_id, get_extra_info
from pathlib import Path
import glob
import os
import pandas as pd
import re

script_name = Path(__file__).stem

path_base = "R:/Personal/Hannah/research_projects/ml"
path_xml = os.path.join(path_base, "from_py/grobid_output_v2")  # From run_grobid_no_cons_v2.py
path_output = os.path.join(path_base, f"from_py/{script_name}")
os.makedirs(path_output, exist_ok=True)

file_pattern = os.path.join(path_xml, "oa_citations_*.tei.xml")
file_paths = glob.glob(file_pattern, recursive=False)
file_paths = sorted(file_paths)  # alphabetical

for j, file_path in enumerate(file_paths):

    stem = os.path.basename(file_path).split('.')[0]

    # FILTER (From ml_02/classify02.py)
    df_filter = pd.read_csv(os.path.join(path_base, f'from_py/classify02/{stem}.csv'))
    biblio_li = df_filter['md5_id'].tolist()
    if len(biblio_li) == 0:
        continue

    # LOOP THROUGH CITATIONS
    xml_content = open(file_path, 'r', encoding='utf-8').read()
    soup = BeautifulSoup(xml_content, 'xml')
    bibl_structs = soup.find_all("biblStruct")
    cits_j = []

    for i, bibl_struct in enumerate(bibl_structs):

        xml_id = bibl_struct["xml:id"]
        raw_ref = bibl_struct.find("note", {"type": "raw_reference"}).get_text()
        raw_ref = re.sub(r'\n$', '', raw_ref.strip())

        # FILTER
        md5_id = md5(raw_ref.lower().encode("utf-8")).hexdigest()
        if md5_id not in biblio_li:
            continue

        # INFO
        metadata = get_extra_info(bibl_struct)  # [volume, issue, first_page, last_page]

        dict_j = {'title': get_title(bibl_struct),
                  'author_id': get_author_id(bibl_struct),
                  'journal_id': get_journal_id(bibl_struct),
                  'year': get_year(bibl_struct),
                  'volume': metadata[0],
                  'issue': metadata[1],
                  'first_page': metadata[2],
                  'last_page': metadata[3]}

        for key, val in dict_j.items():
            if val == None:
                dict_j[key] = 0
            else:
                dict_j[key] = 1

        # APPEND xml_id, md5_id
        dict_id = {'xml_id': xml_id, 'md5_id': md5_id}
        dict_j = dict_id | dict_j

        cits_j.append(dict_j)

    # SAVE
    while None in cits_j:
        cits_j.remove(None)

    df_j = pd.DataFrame(cits_j)
    df_j.to_csv(os.path.join(path_output, f'{j}_{stem}.csv'), index=False)

print("end")
