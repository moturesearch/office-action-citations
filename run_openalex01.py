'''
1 - Run OpenAlex until we have 100 matched citations with a title.
2 - Validate these citations and choose threshold value.
3 - Run OpenAlex on full sample using threshold value.
'''

from pathlib import Path
from run_openalex_func02 import run_openalex

script_name = Path(__file__).stem

# VALIDATION (I ran the line below before running openalex on the full sample).
# run_openalex(script_name=script_name, full='no', rel_thres='', n_for_val=100)

# FULL SAMPLE
run_openalex(script_name=script_name, full='yes', rel_thres=600, n_for_val='')
