'''
Merge crosswalk & enriched data.
'''

from pathlib import Path
import google.cloud.bigquery as bq
import os
import pandas as pd

pd.options.display.max_colwidth = 1000
script_name = Path(__file__).stem
path_base = "R:/Personal/Hannah/research_projects/ml"
path_output = os.path.join(path_base, f"from_py/{script_name}")
os.makedirs(path_output, exist_ok=True)

# GET DATA
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "xx" # path to json file.
client = bq.Client()

query_joined = client.query("""
SELECT  t1.citedDocumentIdentifier,
        t2.patentApplicationNumber,
        t2.officeActionCategory,
        t2.examinerCitedReferenceIndicator, 
        t2.citationCategoryCode, 
        t2.applicantCitedExaminerReferenceIndicator, 
        t2.groupArtUnitNumber
FROM patents-public-data.uspto_office_actions_citations.citedoc_pub_crosswalk AS t1
LEFT JOIN patents-public-data.uspto_office_actions_citations.enriched_citations AS t2
ON t1.citedDocumentIdentifier = t2.citedDocumentIdentifier
WHERE 
    (t1.publication_number IS NULL OR t1.publication_number = '')
    AND
    (t1.citedDocumentIdentifier IS NOT NULL)
    AND
    (t2.inventorNameText IS NULL)
""")

result = query_joined.result(page_size=5000)

for i, df in enumerate(result.to_dataframe_iterable()):

    colname = 'citedDocumentIdentifier'

    df.loc[:, colname] = df.loc[:, colname].astype(str)
    df.loc[:, colname] = df.loc[:, colname].str.title()
    df.loc[:, colname] = df.loc[:, colname].str.replace(r'^\s+|\s+$', '', regex=True)  # removes whitespace from start & end

    to_remove = ['Database Wpi', 'Patent Abstracts', 'Chemical Abstracts', 'Wpi']
    df = df[~df[colname].astype(str).str.startswith(tuple(to_remove))]

    df.loc[:, colname] = df.loc[:, colname].str.replace(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', regex=True)  # removes all control characters (eg SOH) except for \n
    df.loc[:, colname] = df.loc[:, colname].str.replace(r'\s+', ' ', regex=True)

    df.to_csv(f'{path_output}/data_enriched_{i}.csv', index=False)

print("end")
