'''
Functions.
For each file, I loop through bibl_structs (each bibl_struct is one citation) & search (using title or author/year/journal/etc.) in OpenAlex.

Note - this code saves the output even if the title-match threshold is below 600. I drop these matches later on in the pipeline.
'''


def run_openalex(script_name, full, rel_thres, n_for_val):

    '''
    full - 'yes' (run for full sample), 'no' (run for validation - only run for citations with a title)
    rel_thres - relevance threshold (if title match is below threshold we search using author/yr/journal/etc). This param is ignored when full='no'
    n_for_val - number of citations to select for validation (that have a title & for which a match was found). This param is ignored when full='yes'
    '''

    from bs4 import BeautifulSoup
    from hashlib import md5
    from openalex_functions_v6 import get_title, get_author_id, get_year, get_journal_id, get_extra_info, get_extra_link, search_with_title, search_with_meta
    import glob
    import itertools
    import json
    import os
    import pandas as pd
    import re

    rel_threshold = rel_thres
    mycount = 0

    path_base = "R:/Personal/Hannah/research_projects/ml"
    path_xml = os.path.join(path_base, "from_py/grobid_output_v2")  # From run_grobid_no_cons_v2.py
    path_output = os.path.join(path_base, f"from_openalex/{script_name}")
    os.makedirs(path_output, exist_ok=True)

    # Subfolders
    if full == 'yes':
        path_res = os.path.join(path_output, 'results')
    else:
        path_res = os.path.join(path_output, 'for_deciding_threshold')

    path_crossref = os.path.join(path_output, 'for_crossref')
    os.makedirs(path_res, exist_ok=True)
    os.makedirs(path_crossref, exist_ok=True)

    file_pattern = os.path.join(path_xml, "oa_citations_*.tei.xml")
    file_paths = glob.glob(file_pattern, recursive=False)
    file_paths = sorted(file_paths)  # alphabetical

    for j, file_path in enumerate(file_paths):

        results_j = []

        metadata_y_match_n = []  # We'll give these citations to crossref (we append to this list later on).
        metadata_n = []  # We'll give these citations to crossref

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

        for i, bibl_struct in enumerate(bibl_structs):

            result_i = {}
            rel_score = 0

            xml_id = bibl_struct["xml:id"]
            raw_ref = bibl_struct.find("note", {"type": "raw_reference"}).get_text()
            raw_ref = re.sub(r'\n$', '', raw_ref.strip())

            # FILTER
            md5_id = md5(raw_ref.lower().encode("utf-8")).hexdigest()
            if md5_id not in biblio_li:
                continue

            # INFO
            info_di = {'xml_id': xml_id, 'raw_ref': raw_ref, 'md5_id': md5_id}

            # SEARCH WITH TITLE
            title = get_title(bibl_struct)
            if title != None:
                result_i = search_with_title(title)
                if len(result_i) != 0:
                    info_di.update({'search_term': 'title'})
                    rel_score = result_i['relevance_score']

            '''
            -rel_score: this will be recycled from the previous round when: no title OR title, but no match. In both these cases we will already be proceeding to the meta-data search.
            So it doesn't matter that the rel_score is being recycled. However, if the first iteration doesn't have a match, then rel_score won't be defined, and we need rel_score in L101.
            So I've set rel_score to zero above.
            '''

            if full == 'yes':

                # SEARCH WITH AUTHOR,YEAR,JOURNAL & AT LEAST ONE EXTRA PIECE OF INFO (vol, issue, first page, last page)
                if ((title == None) or (len(result_i) == 0) or (rel_score < rel_threshold)):

                    author_id = get_author_id(bibl_struct)
                    journal_id = get_journal_id(bibl_struct)
                    year = get_year(bibl_struct)
                    extra_info_val = get_extra_info(bibl_struct)

                    # PERMUTATIONS (since grobid might incorrectly extract vol, issue, first page, last page, we permute these values and search openalex)
                    c1 = None not in (author_id, journal_id, year)
                    c2 = extra_info_val.count(None) != len(extra_info_val)
                    if c1 and c2:

                        perms = list(itertools.permutations(extra_info_val))  # list, elements are tuples
                        for p, perm in enumerate(perms):

                            extra_link = get_extra_link(perm)
                            if extra_link == None:
                                if p == (len(perms) - 1):
                                    metadata_y_match_n.append(raw_ref)
                                continue

                            result_i = search_with_meta(author_id, year, journal_id, extra_link)
                            if len(result_i) != 0:
                                info_di.update({'search_term': 'auth_yr_journ_plus'})
                                break
                            else:
                                # p = 0, 1, etc, so need to minus 1
                                if p == (len(perms) - 1):
                                    metadata_y_match_n.append(raw_ref)

                    else:
                        metadata_n.append(raw_ref)

            # FORMAT RESULTS

            if full == 'yes':
                keep = ['id', 'doi', 'title', 'publication_year', 'publication_date', 'language', 'is_oa', 'type', 'type_crossref', 'authorships', 'cited_by_count',
                        'cited_by_percentile_year', 'biblio', 'is_retracted', 'referenced_works_count', 'relevance_score', 'primary_location']
            else:
                keep = ['id', 'doi', 'title', 'relevance_score']

            if len(result_i) != 0:
                res_i = {key: result_i[key] for key in keep if key in result_i}
                res_i = info_di | res_i
                results_j.append(res_i)

        # RESULTS
        with open(os.path.join(path_res, f"{stem}.json"), 'w') as file:
            json.dump(results_j, file, indent=4)

        # FOR VALIDATION
        if full == 'no':
            mycount = mycount + len(results_j)
            if mycount > n_for_val:
                break

        if full == 'yes':

            '''
            df_metadata_n
            -Citations that don't have required info for meta-data search.
            -When collecting these citations we only consider citations:
            --without a title, or
            --with a title but no match found, or
            --with a title, match found, but rel score below threshold
            
            df_metadata_y_match_n
            -Citation has required info for meta-data search, but no match found
            '''

            df_metadata_n = pd.DataFrame(metadata_n)
            df_metadata_n.to_csv(os.path.join(path_crossref, f"metadata_n_{j}.csv"), encoding='utf-8', index=False)

            df_metadata_y_match_n = pd.DataFrame(metadata_y_match_n)
            df_metadata_y_match_n.to_csv(os.path.join(path_crossref, f"metadata_y_match_n_{j}.csv"), encoding='utf-8', index=False)

    print("end")
