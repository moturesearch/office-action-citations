'''
Match enriched data to classified citations.
'''

from pathlib import Path
import glob
import hashlib
import os
import pandas as pd
import re


def get_md5_id(x):
    x = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', x)  # removes all control characters (eg SOH) except for \n
    x = re.sub(r'\n$', '', x.strip())
    x = hashlib.md5(x.lower().encode("utf-8")).hexdigest()
    return x


script_name = Path(__file__).stem

path_base = "R:/Personal/Hannah/research_projects/ml"
path_enrich = os.path.join(path_base, "from_py/match_citation_app_01")
path_class = os.path.join(path_base, "from_py/match_classify_01")

enrich_filepaths = glob.glob(f'{path_enrich}/enrich_*.csv', recursive=False)
class_filepaths = glob.glob(f'{path_class}/oa_citations_*.csv', recursive=False)

path_output = os.path.join(path_base, 'from_py', script_name)
os.makedirs(path_output, exist_ok=True)

dfs = []
for i, class_filepath in enumerate(class_filepaths):
    df = pd.read_csv(class_filepath)
    dfs.append(df)
df_class = pd.concat(dfs)

for j, enrich_filepath in enumerate(enrich_filepaths):
    df_enrich = pd.read_csv(enrich_filepath)

    if 'md5_id' not in list(df_enrich):
        df_enrich = df_enrich.dropna(subset=['citedDocumentIdentifier'])
        if df_enrich.shape[0] != 0:
            df_enrich['md5_id'] = df_enrich['citedDocumentIdentifier'].apply(get_md5_id)
        else:
            continue

    df_j = pd.merge(df_class, df_enrich, how='inner', on='md5_id')

    if df_j.shape[0] != 0:
        df_j.to_csv(f'{path_output}/merged_{j}.csv', index=False)

    print(f'File {j}')
