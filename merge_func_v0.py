'''
Functions.
'''

import hashlib
import json
import pandas as pd
import re


def get_md5_id(x):

    x = re.sub(r'\n$', '', x.strip())
    x = hashlib.md5(x.lower().encode("utf-8")).hexdigest()
    return x


def get_auth(d, n0):

    new_d = {f'auth_position_{n0}': d.get('author_position'),
             f'auth_id_{n0}': d.get('author', {}).get('id'),
             f'auth_name_{n0}': d.get('author', {}).get('display_name'),
             f'is_corresponding_{n0}': d.get('is_corresponding')}

    return new_d


def get_inst(d, n0, n1):

    new_d = {f'auth_inst_id_{n0}_{n1}': d.get('id'),
             f'auth_inst_name_{n0}_{n1}': d.get('display_name'),
             f'auth_inst_country_{n0}_{n1}': d.get('country_code'),
             f'auth_inst_type_{n0}_{n1}': d.get('type')}

    return new_d


def json_to_df(filepath_json):

    lines = []
    with open(filepath_json) as f:
        data = json.load(f)  # list of dicts

        for item in data:

            auth_info = {}
            authors = item.get('authorships')  # list of dicts
            for j, author in enumerate(authors):
                d_auth = get_auth(author, n0=j)

                d_insts = {}
                insts = author.get('institutions')
                for k, inst in enumerate(insts):
                    d_inst = get_inst(inst, n0=j, n1=k)
                    d_insts = d_insts | d_inst

                d_auth_insts = d_auth | d_insts  # One author, all institutes
                auth_info = auth_info | d_auth_insts  # All authors (for a given cit)

            try:
                journal = item['primary_location']['source']['display_name']
            except:
                journal = None

            try:
                is_oa = item['primary_location']['is_oa']
            except:
                is_oa = None

            if 'doi' in filepath_json:
                raw_ref = item.get('raw_ref')
                raw_ref = raw_ref.strip('\"')
                # raw_ref = html.unescape(raw_ref)
                md5_id_val = get_md5_id(raw_ref)
            else:
                md5_id_val = item.get('md5_id')

            d = {'md5_id': md5_id_val,
                 'openalex_id': item.get('id'),
                 'raw_ref': item.get('raw_ref'),
                 'publication_year': item.get('publication_year'),
                 'cited_by_percentile_year_min': item.get('cited_by_percentile_year', {}).get('min'),
                 'cited_by_percentile_year_max': item.get('cited_by_percentile_year', {}).get('max'),
                 'is_oa': is_oa,
                 'journal': journal,
                 'relevance_score': item.get('relevance_score'),
                 'type': item.get('type'),
                 'type_crossref': item.get('type_crossref'),
                 'cited_by_count': item.get('cited_by_count'),
                 'is_retracted': item.get('is_retracted')}

            d = d | auth_info

            lines.append(d)

    df_openalex = pd.DataFrame(lines)
    return df_openalex
