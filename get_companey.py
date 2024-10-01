import pandas as pd
import json
from pathlib import Path
import os

company_excel = "/Users/wangyanz/Desktop/glassdoor_selenium/data/company_check_list.xlsx"
df = pd.read_excel(company_excel)
# first column is the company name
all_company_names = df.iloc[:, 0].tolist()

# ---- single process ----
company_names = all_company_names

not_found_list = []
not_run_list = []
    

result_dir = Path("/Users/wangyanz/Desktop/glassdoor_selenium/company_info")
for company_name in company_names:
    if "/" in company_name:
        company_name = company_name.replace("/", " ")
    company_name_without_space = company_name.replace(" ", "_")
    
    if not os.path.exists(result_dir/f"{company_name_without_space}.json"):
        not_run_list.append(company_name)
        continue
    
#     with open(result_dir/f"{company_name_without_space}.json", "r") as f:
#         company_info = json.load(f)
    
#     if "error" in company_info:
#         if company_info["error"] == "No search result found.":
#             not_found_list.append(company_name)
#             continue

# print("Not found:")
# print(len(not_found_list))
# print("not run:")
# print(len(not_run_list))

# with open("not_found.txt", "w") as f:
#     for name in not_found_list:
#         f.write(name + "\n")

with open("not_run.txt", "w") as f:
    for name in not_run_list:
        f.write(name + "\n")