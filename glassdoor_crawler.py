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


class GlassdoorCrawler:
    def __init__(
            self,
            user_email,
            user_password,
            login_url = "https://www.glassdoor.com/profile/login_input.htm",
            max_page_search = 999,
        ):
        self.driver = webdriver.Chrome()
        self.login_url = login_url
        self.user_email = user_email
        self.user_password = user_password
        self.max_page_search = max_page_search
    
    def sleep(self, seconds):
        time.sleep(seconds)

    def login(self):
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
        try:
            self.get_clickable(By.XPATH, '//button[@data-test="search-button"]').click()  # search_btn
            self.sleep(0.5)
        except:
            print("search button not found")
            pass
        input_btn = self.driver.find_element(By.XPATH, '//input[@data-test="keyword-search-input"]')
        input_btn.clear()
        input_btn.send_keys(company_name)
        self.sleep(0.5)
        input_btn.send_keys(Keys.RETURN)
        self.sleep(3.5)
        self.driver.switch_to.window(self.driver.window_handles[-1])
        try:
            first_search = self.driver.find_element(By.XPATH, '//*[@id="Discover"]/div/div/div[1]/div[1]/div[1]/a[1]')
            match_name = first_search.find_element(By.XPATH, "./div[2]/h3").text
        except:
            print("No search result")
            return None
        self.get_clickable(By.XPATH, '//*[@id="Discover"]/div/div/div[1]/div[1]/div[1]/a[1]').click()  # first_search
        self.sleep(3.5)
        self.driver.switch_to.window(self.driver.window_handles[-1])
        return match_name
    
    def go_to_benefit(self):
        try:
            self.get_clickable(By.XPATH, '//a[@data-test="ei-nav-benefits-link"]').click()
            self.sleep(6)
        except:
            self.driver.refresh()
            self.sleep(3)
            self.get_clickable(By.XPATH, '//a[@data-test="ei-nav-benefits-link"]').click()
            self.sleep(6)
        self.driver.switch_to.window(self.driver.window_handles[-1])
    
    def go_to_family_tab(self):
        # family_btn = self.driver.find_element(By.XPATH, '//*[@id="3"]')
        try:
            family_btn = self.driver.find_element(By.XPATH, '//span[@data-test="tabName-Family & Parenting"]')
            family_btn.click()
            self.sleep(1.5)
        except:
            print("Family tab not found")
            return False
        self.driver.switch_to.window(self.driver.window_handles[-1])
        return True
    
    def get_overall_rating(self):
        overall_rating = self.driver.find_element(By.XPATH, '//*[@id="Container"]/div/div/div[2]/main/div[1]/div/div[2]/div/div[1]/strong')
        return overall_rating.text

    def get_categories(self):
        categories = self.driver.find_elements(By.XPATH, '//*[@id="Container"]/div/div/div[2]/main/div[2]/div[5]/div/div/div')
        company_info = {}

        for category_box in categories:
            try:
                rating_score = category_box.find_element(By.XPATH, "./div[2]/span[1]/span[1]").text
                category_name = category_box.find_element(By.XPATH, "./div[1]/a").text
                print(f"Item {category_name} are rated {rating_score}")
                company_info[category_name] = {
                    "category": category_name,
                    "rating": rating_score
                }
            except:
                continue
        return company_info
    
    def get_comments_under_category(self, category_name):
        self.driver.find_element(By.LINK_TEXT, category_name).click()
        time.sleep(2.5)
        self.driver.switch_to.window(self.driver.window_handles[-1])
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
        self.driver.find_element(By.XPATH, '//*[@id="globalNavContainer"]/div/div[1]/a').click()
        self.driver.switch_to.window(self.driver.window_handles[-1])
    
    def run(self, company_name):
        match_name = self.search(company_name)
        if not match_name:
            self.go_to_home()
            self.sleep(3.5)
            return {
                "overall_rating": "N/A",
                "categories": {}
            }
        self.go_to_benefit()
        family_btn = self.go_to_family_tab()
        if not family_btn:
            return {
                "overall_rating": "N/A",
                "categories": {}
            }
        overall_rating = self.get_overall_rating()
        company_info = self.get_categories()
        for category_name in company_info.keys():
            comments = self.get_comments_under_category(category_name)
            category_info = {
                "comments": comments
            }
            company_info[category_name].update(category_info)
            self.go_to_benefit()
            self.go_to_family_tab()
        return {
            "searched_company_name": match_name,
            "overall_rating": overall_rating,
            "categories": company_info
        }
    
    def get_clickable(self, by, value, wait_time=10):
        return WebDriverWait(self.driver, wait_time).until(
            EC.element_to_be_clickable((by, value))
        )
       

if __name__ == "__main__":
    # user_email = "xxxx"
    # user_password = "xxxx"
    user_email = input("Please input your email: ")
    user_password = input("Please input your password: ")
    result_dir = Path("company_info")
    result_dir.mkdir(exist_ok=True)
    
    company_excel = "random50_nolink.xlsx"
    df = pd.read_excel(company_excel)
    # first column is the company name
    company_names = df.iloc[:, 0].tolist()
    crawler = GlassdoorCrawler(user_email, user_password, max_page_search=999)
    crawler.login()
    for company_name in company_names:
        company_name_without_space = company_name.replace(" ", "_")
        if os.path.exists(result_dir/f"{company_name_without_space}.json"):
            print(f"Existed, Skip {company_name}")
            continue
        print(f"Start to crawl {company_name}")
        result = crawler.run(company_name)
        print(result)
        
        with open(result_dir/f"{company_name_without_space}.json", "w") as f:
            json.dump(result, f, indent=4)
        crawler.sleep(3.5)
        
    print("All done")
