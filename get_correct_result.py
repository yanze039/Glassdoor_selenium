import pandas as pd

raw_data = "0_All_comments_2.csv"
similarirty_data = "data/similarity_matched_2_verified-1.xlsx"

raw_data = pd.read_csv(raw_data)
similarirty_data = pd.read_excel(similarirty_data)


# get the company name which ["mismatch"] == 1 and not NaN
similarirty_data = similarirty_data[similarirty_data["mismatch"] == 1]
similarirty_data = similarirty_data.dropna(subset=["conm"])
print(similarirty_data["conm"])
print(len(similarirty_data["conm"]))

print(len(raw_data["conm"]))
# get rows of raw_data which company_name is not in processed similarirty_data
raw_data = raw_data[~raw_data["conm"].isin(similarirty_data["conm"])]
print(len(raw_data["conm"]))

# save to new csv file
raw_data.to_csv("0_All_comments_2_all_matched.csv", index=False)



