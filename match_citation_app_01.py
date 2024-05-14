'''
Match citation to application
'''

from pathlib import Path
import google.cloud.bigquery as bq
import hashlib
import os
import pandas as pd
import re


def get_md5_id(x):

    x = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', x)  # removes all control characters (eg SOH) except for \n
    x = re.sub(r'\n$', '', x.strip())
    x = hashlib.md5(x.lower().encode("utf-8")).hexdigest()

    return x


pd.options.display.max_colwidth = 1000

script_name = Path(__file__).stem
path_base = "R:/Personal/Hannah/research_projects/ml"
path_output = os.path.join(path_base, f"from_py/{script_name}")
os.makedirs(path_output, exist_ok=True)

# Get data
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "xx" # path to json file.
client = bq.Client()

query_enrich = client.query("""
SELECT DISTINCT patentApplicationNumber, citedDocumentIdentifier 
FROM patents-public-data.uspto_office_actions_citations.enriched_citations
""")

result = query_enrich.result(page_size=5000)
for i, df in enumerate(result.to_dataframe_iterable()):

    try:
        df['md5_id'] = df['citedDocumentIdentifier'].apply(get_md5_id)
        md = 'y'
    except:
        print(f'No md5_id column created - {i}')
        md = 'n'

    df.to_csv(os.path.join(path_output, f'enrich_{i}_{md}.csv'), index=False)

print("end")
