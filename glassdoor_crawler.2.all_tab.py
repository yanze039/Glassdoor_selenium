from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
from pathlib import Path
import pandas as pd
import os
import multiprocessing as mp
from multiprocessing import Pool
import undetected_chromedriver as uc
import tqdm

# pip install undetected_chromedriver
options = uc.ChromeOptions()
options.set_capability('unhandledPromptBehavior', 'dismiss')
options.add_argument('--disable-extensions')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-notifications')
options.add_argument('--disable-popup-blocking')

class GlassdoorCrawler:
    def __init__(
            self,
            user_email,
            user_password,
            login_url = "https://www.glassdoor.com/profile/login_input.htm",
            max_page_search = 999,
        ):
        self.driver = uc.Chrome(options=options)
        self.login_url = login_url
        self.user_email = user_email
        self.user_password = user_password
        self.max_page_search = max_page_search
        self.tabs = [
            "Insurance, Health & Wellness",
            "Financial & Retirement",
            "Vacation & Time Off",
            "Perks & Discounts",
            "Family & Parenting",
            "Professional Support",
        ]
    
    def sleep(self, seconds):
        time.sleep(seconds)

    def login(self):
        """
        Log in to your Glassdoor account.
        """
        # use login email and password
        self.driver.get(self.login_url)
        self.sleep(3.5)
        login_email = self.driver.find_element(By.XPATH, '//*[@id="inlineUserEmail"]')
        login_email.send_keys(self.user_email)
        self.get_clickable(By.XPATH, '//*[@id="InlineLoginModule"]/div/div[1]/div/div/div/div/form/div[2]/button').click()
        self.sleep(2.5)
        self.driver.find_element(By.XPATH, '//*[@id="inlineUserPassword"]').send_keys(self.user_password)
        self.get_clickable(By.XPATH, '//*[@id="InlineLoginModule"]/div/div[1]/div/div/div/div/form/div[2]/button').click()
        self.sleep(3.5)
        self.driver.switch_to.window(self.driver.window_handles[-1])
    
    def search(self, company_name):
        """
        Search company name in Glassdoor.
        """
        try:
            # search by button with name "search-button"
            # do not use full XPATH, because it may change in pages other than home page
            self.get_clickable(By.XPATH, '//button[@data-test="search-button"]').click()  # search_btn
            self.sleep(0.5)
        except:
            print("search button not found")
            pass
        input_btn = self.driver.find_element(By.XPATH, '//input[@data-test="keyword-search-input"]')
        # clear before typing new company name
        input_btn.clear()
        input_btn.send_keys(company_name)
        self.sleep(0.5)
        input_btn.send_keys(Keys.RETURN)
        self.sleep(2.5)
        self.driver.switch_to.window(self.driver.window_handles[-1])
        try:
            # first search result
            first_search = self.driver.find_element(By.XPATH, '//*[@id="Discover"]/div/div/div[1]/div[1]/div[1]/a[1]')
            match_name = first_search.find_element(By.XPATH, "./div[2]/h3").text
        except:
            print("No search result")
            return None
        self.get_clickable(By.XPATH, '//*[@id="Discover"]/div/div/div[1]/div[1]/div[1]/a[1]').click()  # first_search
        self.sleep(2.5)
        self.driver.switch_to.window(self.driver.window_handles[-1])
        return match_name
    
    def go_to_benefit(self):
        """
        Click the Benefits button.
        """
        try:
            # search by button with name "Benefits"
            # in glassdoor, this means data-test="ei-nav-benefits-link" by <a></a>
            self.get_clickable(By.XPATH, '//*[@data-test="ei-nav-benefits-link"]').click()
            self.sleep(2.5)
        except:
            self.driver.refresh()
            self.sleep(2.5)
            try:
                self.get_clickable(By.XPATH, '//a[@data-test="ei-nav-benefits-link"]').click()
            except:
                self.get_clickable(By.XPATH, '//div[@data-test="ei-nav-benefits-link"]').click()
            self.sleep(2.5)
        self.driver.switch_to.window(self.driver.window_handles[-1])
    
    def go_to_family_tab(self):
        """
        Find the Family and Parenting Button and click it, otherwise report.
        """
        try:
            family_btn = self.driver.find_element(By.XPATH, '//span[@data-test="tabName-Family & Parenting"]')
            family_btn.click()
            self.sleep(0.7)
        except:
            # the company may not have family&parenting button under Benefits
            print("Family tab not found")
            return False
        self.driver.switch_to.window(self.driver.window_handles[-1])
        
        return family_btn.get_attribute('id')
    
    def go_to_tab_by_name(self, name="Family & Parenting"):
        """
        Find the tab by name and click it.
        """
        try:
            tab_btn = self.driver.find_element(By.XPATH, f'//span[@data-test="tabName-{name}"]')
            tab_btn.click()
            self.sleep(0.7)
        except:
            # the company may not have family&parenting button under Benefits
            print(f"{name} tab not found")
            return False
        self.driver.switch_to.window(self.driver.window_handles[-1])
        
        return tab_btn.get_attribute('id')
    
    def get_overall_rating(self):
        """
        Get overall rating of Benefits.
        """
        overall_rating = self.driver.find_element(By.XPATH, '//*[@id="Container"]/div/div/div[2]/main/div[1]/div/div[2]/div/div[1]/strong')
        return overall_rating.text

    def get_categories(self, name="Family & Parenting"):
        """
        Get all categories and rating score.
        We do this because we need to know the category names in advance.
        Then we would search clickable link by category name in `get_comments_under_category`.
        This procedure would ensure we get all comments under each category.
        """
        company_info = {}
        h3_block = self.driver.find_element(By.XPATH, f"//h3[text()='{name}']")
        parent_grid = h3_block.find_element(By.XPATH, "./..")
        
        try:
            # categories = self.driver.find_elements(By.XPATH, '//*[@id="Container"]/div/div/div[2]/main/div[2]/div[5]/div/div/div')
            categories = parent_grid.find_elements(By.XPATH, ".//div[starts-with(@data-test, 'benefit-')]")
        except:
            print("No categories found")
            categories = []
        for category_box in categories:
            try:
                rating_score = category_box.find_element(By.XPATH, './/span[@data-test="ratingValue"]').text
                rating_count = category_box.find_element(By.XPATH, './/div[@data-test="ratingCount"]').text
                verified = None
                try:
                    find_verified = category_box.find_element(By.XPATH, './/span[@data-test="verified"]')
                    verified = True
                except:
                    verified = False
                category_name = category_box.find_element(By.XPATH, "./div[1]/a").text
                print(f"Item {category_name} are rated {rating_score}")
                company_info[category_name] = {
                    "category": category_name,
                    "rating": rating_score,
                    "rating_count": rating_count,
                    "verified": verified
                }
            except:
                continue
        return company_info
    
    def get_employ_info(self):
        employ_info = {}
        
        try:
            employee_reporting_number = self.driver.find_element(By.XPATH, '//*[@id="Container"]/div/div/div[2]/main/div[1]/div[1]/div/p/span').text
        except:
            employee_reporting_number = "N/A"
        try:
            employer_verified = self.driver.find_element(By.XPATH, '//*[@id="Container"]/div/div/div[2]/main/div[1]/div[3]/div/p/span').text
        except:
            employer_verified = "N/A"
            
        employ_info = {
            "employee_reporting": employee_reporting_number,
            "employer_verified": employer_verified
        }
    
        return employ_info
    
    def go_to_category(self, category_name):
        self.driver.find_element(By.LINK_TEXT, category_name).click()
        time.sleep(2.5)
        self.driver.switch_to.window(self.driver.window_handles[-1])
    
    def get_comments_under_category(self):
        """
        Get all comments under a category.
        Steps:
        1. Click the category, find link by text
        2. Get all comments
        3. Click next page if `enabled`
        4. Repeat until no more page [ or reach `max_page_search` (for DEBUG) ]
        """
        end_page=False
        all_comments = {}
        page_idx = 1
        comment_id = 0
        while not end_page:
            print(f"Page {page_idx}")
            all_comment_elements = self.driver.find_elements(By.XPATH, '//*[@id="Container"]/div/div/div[2]/main/div[2]/div[1]/div')
            comments = {}
            for comment_e in all_comment_elements:
                try:
                    comment_date = comment_e.find_element(By.XPATH, "./span").text
                    comment_score = comment_e.find_element(By.XPATH, "./div[1]/div[1]/strong").text
                    commenter_position = comment_e.find_element(By.XPATH, "./div[1]/div[2]/span").text
                    comment_content = comment_e.find_element(By.XPATH, "./p").text
                    comments[comment_id] = {
                        "date": comment_date,
                        "score": comment_score,
                        "position": commenter_position,
                        "content": comment_content
                    }
                    comment_id += 1
                except:
                    continue
            all_comments.update(comments)
            page_idx += 1
            if page_idx > self.max_page_search:
                end_page = True
                break
            try:
                next_button = self.driver.find_element(By.XPATH, '//*[@id="Container"]/div/div/div[2]/main/div[2]/div[2]/div/div[1]/button[2]')
                if not next_button.is_enabled():
                    end_page = True
                    break
                next_button.click()
                time.sleep(3.0)
                self.driver.switch_to.window(self.driver.window_handles[-1])
            except:
                end_page = True
                break
        return all_comments
    
    def close(self):
        self.driver.quit()
    
    def go_to_home(self):
        """
        Go to homepage by find the button on the top left corner.
        """
        self.driver.find_element(By.XPATH, '//*[@id="globalNavContainer"]/div/div[1]/a').click()
        self.driver.switch_to.window(self.driver.window_handles[-1])
    
    def run(self, company_name):
        """Grab full company info from Glassdoor.
        1. search company name
        2. go to benefit page
        3. go to family tab
        4. get overall rating
        5. get categories
        6. get comments under each category

        NOTE: 
            * must go to homepage to renew search, otherwise searching bar will be blocked
            * if no family tab found, missing info, return empty.
            * the searched company name may not be the same as the input company name, return the `searched name` instead.

        Args:
            company_name (_type_): company name in original Excel file

        Returns:
            dict: company info in dict format. Empty if no search result or no family tab found.
                   full info includes:
                     - searched_company_name: the company name found in Glassdoor
                        - overall_rating: overall rating of the company
                        - categories: dict of categories, each category includes:
                            - comments: dict of comments, each comment includes:
                                - date: date of the comment
                                - score: score of the comment
                                - position: position of the commenter
                                - content: content of the comment
        """
        match_name = self.search(company_name)
        if not match_name:
            # no search result, return empty.
            # must go homepage to renew search, otherwise searching bar will be blocked
            self.go_to_home()
            self.sleep(2.5)
            return {
                "overall_rating": "N/A",
                "categories": {},
                "error": "No search result found."
            }
        self.go_to_benefit()
        try:
            overall_rating = self.get_overall_rating()
        except:
            overall_rating = "N/A"
            
        all_info = {}
        
        for tab_name in self.tabs:
            tab_info = {}
            btn = self.go_to_tab_by_name(tab_name)
            if not btn:
                all_info[tab_name] = {
                    "comments": {},
                    "error": f"{tab_name} tab not found."
                }
            try:
                tab_info = self.get_categories(name=tab_name)
            except:
                tab_info = {}
                
            for idx, category_name in enumerate(list(tab_info.keys())):
                # if category_name not in ["Work From Home"]:
                #     continue
                if idx > 0:
                    self.go_to_benefit()
                    self.go_to_tab_by_name(tab_name)  # go back to family tab to renew
                self.go_to_category(category_name)
                employ_info = self.get_employ_info()
                comments = self.get_comments_under_category()
                category_info = {
                    "comments": comments,
                }
                tab_info[category_name].update(category_info)
                tab_info[category_name].update(employ_info)
            tab_info["error"] = "N/A"
            all_info[tab_name] = tab_info    
            self.go_to_benefit()   
            
        return {
            "searched_company_name": match_name,
            "overall_rating": overall_rating,
            "categories": all_info,
            "error": "N/A"
        }
    
    def get_clickable(self, by, value, wait_time=10):
        return WebDriverWait(self.driver, wait_time).until(
            EC.element_to_be_clickable((by, value))
        )
       

def grab_company_info(company_names):
    result_dir = Path("company_info")
    user_email = "yanze039@mit.edu"
    user_password = "wazx31831110"
    crawler = GlassdoorCrawler(user_email, user_password)
    crawler.login()
    for company_name in company_names:
        company_name_without_space = company_name.replace(" ", "_")
        # ensure we can rerun from the last breakpoint when the code reports error
        if os.path.exists(result_dir/f"{company_name_without_space}.json"):
            print(f"Existed, Skip {company_name}")
            continue
        print(f"Start to crawl {company_name}")
        result = crawler.run(company_name)
        # print(resu
        # save json file
        with open(result_dir/f"{company_name_without_space}.json", "w") as f:
            json.dump(result, f, indent=4)
        crawler.sleep(3.5)
  


if __name__ == "__main__":
    import argparse
    time.sleep(2)
    parser = argparse.ArgumentParser()
    parser.add_argument("start", type=int)
    parser.add_argument("end", type=int)
    args = parser.parse_args()
    
    user_email = "yanze039@mit.edu"
    user_password = "wazx31831110"
    # user_email = input("Please input your email: ")
    # user_password = input("Please input your password: ")
    result_dir = Path("company_info")
    result_dir.mkdir(exist_ok=True)
    
    # company_excel = "compustat_full_sample.xlsx"
    # df = pd.read_excel(company_excel)
    # # first column is the company name
    # all_company_names = df.iloc[:, 1].tolist()
    
    with open("not_run.txt", "r") as f:
        comp_list = f.readlines()
    
    # with open("not_run.txt", "r") as f:
    #     not_run_list = f.readlines()
    
    # # all_company_names = not_found_list + not_run_list
    # all_company_names = not_run_list
    
    # all_company_names.sort()
    # all_company_names = [name.strip() for name in all_company_names]
    all_company_names = [name.strip() for name in comp_list]
    
    # ---- single process ----
    company_names = all_company_names[args.start:args.end]
    crawler = GlassdoorCrawler(user_email, user_password, max_page_search=999)
    crawler.login()
    idx = 0
    try:
        for company_name in tqdm.tqdm(company_names):
            if "/" in company_name:
                company_name = company_name.replace("/", " ")
            company_name_without_space = company_name.replace(" ", "_")
            # ensure we can rerun from the last breakpoint when the code reports error
            if os.path.exists(result_dir/f"{company_name_without_space}.json"):
                print(f"Existed, Skip {company_name}")
                continue
            print(f"Start to crawl {company_name}")
            result = crawler.run(company_name)
            # save json file
            with open(result_dir/f"{company_name_without_space}.json", "w") as f:
                json.dump(result, f, indent=4)
            crawler.sleep(2.5)
            idx += 1
            if idx % 10 == 0:
                crawler.delete_all_cookies()
            
    except:
        crawler.driver.quit()
        exit(1)
        
    # print("All done")

    # ---- multi-process ----
    
    # print("here")
    # print(all_company_names)
    # max_workers = 4
    # # divide company names into `max_workers` parts
    # div_company_names = [all_company_names[i:i + len(all_company_names)//max_workers] for i in range(0, len(all_company_names), len(all_company_names)//max_workers)]
    
    # with Pool(max_workers) as p:
    #     p.map(grab_company_info, div_company_names)
        
        
        
        
