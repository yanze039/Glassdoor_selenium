import json
import pandas as pd
from pathlib import Path
import os

class JsonProcess:
    def __init__(self, json_file_path, output_dir):
        # self.category = category
        self.json_file_path = json_file_path
        self.output_dir = output_dir
    
    @ staticmethod    
    def json_to_df(json_file):
        """
        Convert json dict to pandas DataFrame when json file is not NA, otherwise return empty DataFrame.
        """
        records = []
        # Iterate over each category and its comments
        for benefit_name, benefit_info in json_file["categories"].items():
            for category_name, category_info in benefit_info.items():
                if category_name != "error":
                    for comment_id, comment_info in category_info["comments"].items():
                        # Create a record combining overall info and specific comment info
                        record = {
                            "searched_company_name": json_file["searched_company_name"],
                            "overall_rating": json_file["overall_rating"],
                            "benefit": benefit_name,
                            "category": category_info["category"],
                            "category_rating": category_info["rating"],
                            "comment_date": comment_info["date"],
                            "comment_score": comment_info["score"],
                            "comment_position": comment_info["position"],
                            "comment_content": comment_info["content"],
                            "employee_reporting": category_info["employee_reporting"].split(' ')[0],
                            "employer_verified": category_info["employer_verified"],
                            "error": json_file.get("error", "No record")
                        }
                        records.append(record)

        # Create the DataFrame
        df = pd.DataFrame(records)
        if df.empty:
            # otherwise return empty DataFrame
            df = pd.DataFrame()
            
        return df
        
    def load_json_file(self):
        """
        Load saved json file.
        """
        with open(self.json_file_path, encoding= 'utf-8') as f:
            json_file = json.load(f)
        return json_file
    
    # def get_category_comments(self, df):
        
    #     if len(df)!= 0 :
    #         return df[df['category'] == self.category]
    #     else:
    #         return df
    
    def save_csv(self):
        
        json_file = self.load_json_file()
        df = self.json_to_df(json_file)
        # category_df = self.get_category_comments(df)
        
        company_name_without_space = (self.json_file_path).split('/')[-1].split('json')[0][:-1]
        df.to_csv(self.output_dir/ f'{company_name_without_space}.csv', index = False)
        
    
if __name__ == "__main__":
    
    json_folder_path = 'company_info.full/'
    json_file_names = os.listdir(json_folder_path)
    output_folder = 'company_csv_full/'
    output_dir = Path(output_folder)
    output_dir.mkdir(exist_ok=True)
    
    for json_file_name in json_file_names:
        
        company_name_without_space = json_file_name.split('json')[0][:-1]
        company_name = company_name_without_space.replace('_', ' ')
        if os.path.exists(output_dir/f"{company_name_without_space}.csv"):
            print(f"Existed, Skip {company_name}")
            continue
        print(f"Start to save {company_name}")
        json_file_path = json_folder_path + json_file_name
        data = JsonProcess(json_file_path, output_dir)
        data.save_csv()
        
    print('data for all companies has been saved.')


# match excel file
excel_name = "data/compustat_full_sample.xlsx"
excel_file = pd.read_excel(excel_name)
excel_file['gvkey'] = excel_file['gvkey'].apply(lambda x: str(x))
excel_file['company_name_without_space'] = excel_file['conm'].apply(lambda x: x.replace(' ', '_').replace('/', '_'))
    
# Save all the data in one csv
csv_files = sorted(os.listdir(output_dir))
dfs = []
company_count = 0
for csv_file in csv_files:
    try:
        company_name_without_space = csv_file.split('.csv')[0]
        company_original_info = excel_file[excel_file['company_name_without_space'] == company_name_without_space]
        
        df = pd.read_csv(output_dir/f'{csv_file}')
        # Reset the index to default (starting from 0)
        company_original_info_reset = company_original_info.reset_index(drop=True)
        dfs.append(pd.concat([company_original_info_reset.reindex(df.index).ffill().drop(columns=['company_name_without_space']), df], axis=1))
        company_count = company_count+1
    except:
        # print(csv_file+' is empty.')
        continue
pd.concat(dfs, axis = 0).drop(columns= ['error']).to_csv('0_All_comments_2.csv', index=False,  encoding='utf-8-sig')
print('{} out of {} companies have comments.'.format(str(company_count), str(len(csv_files))))
print('All done.')



## error check
no_search_results_number = 0
no_family_tab_number = 0
company_with_comments = 0
company_without_comments = 0

no_family_tab_companies_list = []
company_without_comments_list = []

# company_info_paths = sorted(os.listdir(Path('company_info')))
# for company_info_path in company_info_paths:
#     with open(Path('company_info')/company_info_path) as f:
#         info_dict = json.load(f)
#     if 'error' in info_dict.keys():
#         if info_dict['error'] == 'No search result found.':
#             no_search_results_number += 1
            
#         elif info_dict['error'] == 'No Family tab found.':
#             no_family_tab_number += 1
#             no_family_tab_companies_list.append([company_info_path.split('.json')[0].replace('_', ' '), info_dict["searched_company_name"]])
#         else:
#             if info_dict['categories'] != {}:
#                 if all(list(info_dict['categories'].values())[i]['comments'] == {} for i in range(len(info_dict['categories']))):
#                     # ASCENDIS_PHARMA_AS.json
#                     # GEOSPACE_TECHNOLOGIES_CORP.json
#                     # JARDEN_CORP.json
#                     # NORTHFIELD_BANCORP_INC.json
#                     company_without_comments +=1
#                     company_without_comments_list.append([company_info_path.split('.json')[0].replace('_', ' '), info_dict["searched_company_name"]])
#                 else:
#                     company_with_comments +=1     
#             else:
#                 company_without_comments +=1
#                 company_without_comments_list.append([company_info_path.split('.json')[0].replace('_', ' '), info_dict["searched_company_name"]])
            
#     else:
#         if 'searched_company_name' not in info_dict.keys():
#             no_search_results_number +=1  
#         elif (info_dict['overall_rating'] == 'N/A' and info_dict['categories'] == {}):
#             no_family_tab_number +=1
#             no_family_tab_companies_list.append([company_info_path.split('.json')[0].replace('_', ' '), info_dict["searched_company_name"]])
#         else:
#             if info_dict['categories'] != {}:
#                 company_with_comments +=1          
#             else:
#                 company_without_comments +=1
#                 company_without_comments_list.append([company_info_path.split('.json')[0].replace('_', ' '), info_dict["searched_company_name"]])
                
            
# print('{} companies are not found in Glassdoor.'.format(str(no_search_results_number)))
# print('{} companies do not have family&parenting tab in Glassdoor.'.format(str(no_family_tab_number)))
# print('{} companies are found and also have comments.'.format(str(company_with_comments)))
# print('{} companies are found but without comments.'.format(str(company_without_comments)))

# pd.DataFrame(no_family_tab_companies_list, columns = ['comn', 'searched_company_name']).to_excel('no_family_tab_companies.xlsx', index = False)
# pd.DataFrame(company_without_comments_list, columns = ['comn', 'searched_company_name']).to_excel('companies_without_comments.xlsx', index = False)
