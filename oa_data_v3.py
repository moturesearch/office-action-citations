'''
This code gets OA data from BigQuery.
'''

from functions_bq_data_v1 import create_text_files
from pathlib import Path
import google.cloud.bigquery as bq
import os
import pandas as pd

pd.options.display.max_colwidth = 1000
script_name = Path(__file__).stem
path_base = "R:/Personal/Hannah/research_projects/ml"
path_output = os.path.join(path_base, f"from_py/{script_name}")
os.makedirs(path_output, exist_ok=True)

# Get data
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "xx" # path to json file.
client = bq.Client()

query_crosswalk = client.query("""
SELECT * FROM patents-public-data.uspto_office_actions_citations.citedoc_pub_crosswalk
WHERE (publication_number IS NULL OR publication_number = '')
""")

result = query_crosswalk.result(page_size=5000)
create_text_files(result=result, path_output=path_output, colname="citedDocumentIdentifier")

print("end")
