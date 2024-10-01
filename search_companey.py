from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import json


driver = webdriver.Chrome()
driver.get("https://www.glassdoor.com/profile/login_input.htm")


# login
time.sleep(1.586967)

login_email = driver.find_element(By.XPATH, '//*[@id="inlineUserEmail"]')
login_email.send_keys("yanze039@mit.edu")
time.sleep(1.245)
continue_button = driver.find_element(By.XPATH, '//*[@id="InlineLoginModule"]/div/div[1]/div/div/div/div/form/div[2]/button')
continue_button.click()
time.sleep(1.5)

#### your password here
login_password = driver.find_element(By.XPATH, '//*[@id="inlineUserPassword"]')
login_password.send_keys("xxxx")
#### your password here

time.sleep(2.245)
login_button = driver.find_element(By.XPATH, '//*[@id="InlineLoginModule"]/div/div[1]/div/div/div/div/form/div[2]/button')
login_button.click()

# 等待页面加载
time.sleep(2.586967)

# switch to new window
driver.switch_to.window(driver.window_handles[-1])
a_list = [1,2,3,4]
x = a_list[-1]
a_list.append(5)

orginal_webpage = driver.window_handles[-1]

try:
    search_btn = driver.find_element(By.XPATH, '//*[@id="UtilityNav"]/div[1]/button')
    search_btn.click()
    time.sleep(2.245)
except:
    print("search button not found")
    pass

input_btn = driver.find_element(By.XPATH, '//*[@id="sc.keyword"]')
input_btn.send_keys("IBM")
time.sleep(1.0)
input_btn.send_keys(Keys.RETURN)

driver.switch_to.window(driver.window_handles[-1])

# //*[@id="Discover"]/div/div/div[1]/div[1]/div[1]/a[1]
# search_list = driver.find_elements(By.XPATH, '//*[@id="Discover"]/div/div/div[1]/div[1]/div[1]')
# first_search = search_list[0]
first_search = driver.find_element(By.XPATH, '//*[@id="Discover"]/div/div/div[1]/div[1]/div[1]/a[1]')
first_search.click()
time.sleep(1.245)
# switch to new window
driver.switch_to.window(driver.window_handles[-1])

time.sleep(1.586967)
benefit_btn = driver.find_element(By.XPATH, '//*[@id="EmpLinksWrapper"]/div[2]/div/div[1]/a[7]')
benefit_btn.click()
time.sleep(3.245)

driver.switch_to.window(driver.window_handles[-1])

overall_rating = driver.find_element(By.XPATH, '//*[@id="Container"]/div/div/div[2]/main/div[1]/div/div[2]/div/div[1]/strong')
print("Overall Rating: ")
print(overall_rating.text)

family_btn = driver.find_element(By.XPATH, '//*[@id="3"]')
family_btn.click()
time.sleep(1.245)
driver.switch_to.window(driver.window_handles[-1])

rating_categories = driver.find_elements(By.XPATH, '//*[@id="Container"]/div/div/div[2]/main/div[2]/div[5]/div/div/div')
print("Rating Categories: ", len(rating_categories))

family_window = driver.window_handles[-1]

for category in rating_categories:
    try:
        rating_score = category.find_element(By.XPATH, "./div[2]/span[1]/span[1]")
        employer_verified = False
        category_name = category.find_element(By.XPATH, "./div[1]/a")
        try :
            category = category.find_element(By.XPATH, "./span[2]/div")
            employer_verified = True
        except:
            pass
        print(f"Item {category_name.text} are rated {rating_score.text}")
    except:
        continue
    # go to subpage
    driver.find_element(By.LinkText("Google")).Click()
    driver.switch_to.window(driver.window_handles[-1])
    

# work from home
# //*[@id="Container"]/div/div/div[2]/main/div[2]/div[5]/div/div/div[1]/div[1]/a
# //*[@id="Container"]/div/div/div[2]/main/div[2]/div[5]/div/div/div[1]/div[2]/span[1]/span[1]
# leave
# //*[@id="Container"]/div/div/div[2]/main/div[2]/div[5]/div/div/div[2]/div[1]/a
    
# //*[@id="Container"]/div/div/div[2]/main/div[2]/div[5]/div/div/div[1]/div[1]/a
# //*[@id="Container"]/div/div/div[2]/main/div[2]/div[5]/div/div/div[3]/div[2]/span/span[1]
# //*[@id="Container"]/div/div/div[2]/main/div[2]/div[5]/div/div/div[6]/div[2]/span/span[1]
# //*[@id="Container"]/div/div/div[2]/main/div[2]/div[5]/div/div/div[2]/div[2]/span[1]/span[1]
time.sleep(113.586967)
driver.switch_to.window(orginal_webpage)


