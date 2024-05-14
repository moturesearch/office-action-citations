'''
Merge csv files from journals_v1.py with openalex output

csv files are crosswalk & enriched data.
'''

from merge_func_v0 import get_md5_id, json_to_df
from pathlib import Path
import glob
import os
import pandas as pd

pd.options.display.max_colwidth = 500

script_name = Path(__file__).stem
path_base = "R:/Personal/Hannah/research_projects/ml"
path_openalex = os.path.join(path_base, "from_openalex/run_openalex01/results")
path_csv = os.path.join(path_base, "from_py/journals_v1")

path_output = os.path.join(path_base, f"from_py/{script_name}")
os.makedirs(path_output, exist_ok=True)

filepaths_csv = glob.glob(f'{path_csv}/data_enriched_*.csv', recursive=False)
filepaths_json = glob.glob(f'{path_openalex}/oa_citations_*.json', recursive=False)  # From OpenAlex.
filepaths_doi = glob.glob(f'{path_base}/from_openalex/crossref_part_b_01/results/*.json', recursive=False)  # From Crossref.

filepaths_json = filepaths_json + filepaths_doi
filepaths_json = sorted(filepaths_json)

filepaths_class = glob.glob(f'{path_base}/from_py/classify02/oa_citations_*.csv', recursive=False)

# CROSSWALK/ENRICHED DATA
dfs = []
for f, filepath_csv in enumerate(filepaths_csv):
    print(f'Enrich - {f}')
    df = pd.read_csv(filepath_csv)
    df['md5_id'] = df['citedDocumentIdentifier'].apply(get_md5_id)
    dfs.append(df)
df_enrich = pd.concat(dfs)
df_enrich = df_enrich.drop_duplicates()
df_enrich = df_enrich.sort_values('md5_id')

# CLASSIFIED CITATIONS
dfs = []
for filepath_class in filepaths_class:
    df = pd.read_csv(filepath_class)
    dfs.append(df)
df_class = pd.concat(dfs)

# OPENALEX JSON FILES
for i, filepath_json in enumerate(filepaths_json):

    stem = os.path.basename(filepath_json).split('.')[0]
    df_openalex = json_to_df(filepath_json)

    if df_openalex.shape[0] == 0:
        continue  # In run_openalex_func02.py, if all citations in a file are unmatched an empty output json file is created.

    df_openalex = df_openalex.sort_values('md5_id')

    # MERGE 1
    ids_in_openalex = df_openalex['md5_id'].tolist()
    df_enrich_i = df_enrich[df_enrich['md5_id'].isin(ids_in_openalex)]
    df_merged = pd.merge(df_openalex, df_enrich_i, how='left', on='md5_id')

    # MERGE 2
    df_merged = pd.merge(df_merged, df_class, how='left', on='md5_id')
    df_merged['input_file'] = f'{stem}'
    
    df_merged = df_merged[(df_merged['relevance_score'] > 600) | df_merged['relevance_score'].isna()] 
    # if title match had rel score below 600 we searched for match using author/title/journal.
    
    df_merged.to_csv(os.path.join(path_output, f'merged_{stem}.csv'), index=False)

print("end")
