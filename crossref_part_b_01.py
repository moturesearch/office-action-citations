'''
This code searches openlex using the DOI (if present) from the grobid output files.

Run this after crossref_03.py
'''

from bs4 import BeautifulSoup
from hashlib import md5
from pathlib import Path
import glob
import json
import os
import pandas as pd
import re
import requests


def search_with_doi(doi):

    try:
        r = requests.get(f"https://api.openalex.org/works/https://doi.org/{doi}")
        result = r.json()
    except:
        result = {}

    return result  # dict (if match found), otherwise {}


script_name = Path(__file__).stem

path_base = 'R:/Personal/Hannah/research_projects/ml'
path_xml = os.path.join(path_base, f'from_py/crossref_03/xml_files_from_grobid')
path_output = os.path.join(path_base, f'from_openalex/{script_name}/results')
os.makedirs(path_output, exist_ok=True)

# LOOP OVER FILES
filepaths = glob.glob(f'{path_xml}/*.tei.xml', recursive=False)
filepaths = sorted(filepaths)
for j, filepath in enumerate(filepaths):

    stem = os.path.basename(filepath).split('.')[0]

    xml_content = open(filepath, 'r', encoding='utf-8').read()
    soup = BeautifulSoup(xml_content, 'xml')
    bibl_structs = soup.find_all("biblStruct")

    doi_y_match_y_j = []
    doi_y_match_n_j = []
    doi_n_j = []

    # LOOP OVER CITATIONS
    for i, bibl_struct in enumerate(bibl_structs):

        raw_ref = bibl_struct.find("note", {"type": "raw_reference"}).get_text()
        raw_ref = re.sub(r'\n$', '', raw_ref.strip())
        md5_id = md5(raw_ref.lower().encode("utf-8")).hexdigest()

        info_i = {'raw_ref': raw_ref, 'md5_id': md5_id}

        try:
            doi = bibl_struct.find("idno", {"type": "DOI"}).get_text()
        except:
            doi = None
            doi_n_j.append(info_i)

        if doi != None:
            openalex_result = search_with_doi(doi)
            if len(openalex_result) != 0:

                keep = ['id', 'doi', 'title', 'publication_year', 'publication_date', 'language', 'is_oa', 'type', 'type_crossref', 'authorships', 'cited_by_count',
                        'cited_by_percentile_year', 'biblio', 'is_retracted', 'referenced_works_count', 'relevance_score', 'primary_location']

                res_i = {key: openalex_result[key] for key in keep if key in openalex_result}

                res_i = info_i | res_i
                doi_y_match_y_j.append(res_i)

            else:
                doi_y_match_n_j.append(info_i)

    # SAVE (FOR EACH FILE)
    with open(os.path.join(path_output, f'doi_y_match_y_{stem}.json'), 'w') as file:
        json.dump(doi_y_match_y_j, file, indent=4)

    df_unmatched = pd.DataFrame(doi_y_match_n_j)
    df_unmatched.to_csv(os.path.join(path_output, f'doi_y_match_n_{stem}.csv'))

    df_no_doi = pd.DataFrame(doi_n_j)
    df_no_doi.to_csv(os.path.join(path_output, f'doi_n_{stem}.csv'))

print("end")
