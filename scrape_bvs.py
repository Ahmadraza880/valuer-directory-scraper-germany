# Example scraper for BVS

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait, Select
import time
import pandas as pd
import copy

# Setup options
options = Options()
# options.add_argument("--headless")  # Uncomment after testing
options.add_argument("--window-size=1920,1080")

# Start the browser
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 10)

search_inputs = [
    {"plz": "10115"},
    {"plz": "20095"},
    {"plz": "50667"},
    {"plz": "20095"},
    {"plz": "70173"},
    {"plz": "01067"},
    {"plz": "90402"},
    {"plz": "04109"},
    {"plz": "28195"},
    {"plz": "65183"},
    {"plz": "80331"},
    {"plz": "39104"},
    {"plz": "99084"},
    {"plz": "24103"},
    {"plz": "66111"},
    {"plz": "45127"},
    {"plz": "79539"},
    {"plz": "02826"},

]
response=[]
def extract_results():
    try:
        rows = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//tr[@class='row1']"))
        )

        for i in range(len(rows)):
            try:
                row = rows[i]

                driver.execute_script("arguments[0].scrollIntoView(true);", row)
                time.sleep(0.3)

                try:
                    row.click()
                except Exception:
                    driver.execute_script("arguments[0].click();", row)

                # Get full name from activated row
                active_row = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//tr[contains(@class, 'row1') and contains(@class, 'active')]"))
                )
                full_name_elem = active_row.find_element(By.XPATH, ".//td[1]/a")
                full_name = full_name_elem.text.strip()

                # Get detailed person info block
                det = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//tr[@class='full active' and contains(@style, 'display')]//div[@class='personDetail']"))
                )

                # Extract plain text parts
                lines = det.get_attribute("innerText").splitlines()
                lines = [line.strip() for line in lines if line.strip()]

                company = ""
                address_lines = []
                phone = ""
                cert_lines = []

                for i, line in enumerate(lines):
                    if "Adresse" in line:
                        company = lines[i + 1] if i + 1 < len(lines) else ""
                        address_lines = lines[i + 2:i + 5]
                    elif "Tel" in line:
                        phone = line.replace("Tel.:", "").strip()
                    elif "Tätigkeitsgebiet" in line:
                        cert_lines = lines[i + 2:]

                address = ", ".join(address_lines)
                cert = ", ".join(cert_lines)

                # ✅ Extract email (from mailto and components inside <a.mymail>)
                try:
                    email_elem = det.find_element(By.CSS_SELECTOR, "a.mymail")
                    email_user = email_elem.find_element(By.XPATH, "./text()[1]").strip()
                    email_domain = email_elem.find_element(By.XPATH, "./text()[2]").strip()
                    email = f"{email_user}@{email_domain}"
                except Exception:
                    try:
                        email_href = det.find_element(By.CSS_SELECTOR, "a.mymail").get_attribute("href")
                        email = email_href.replace("mailto:", "").strip()
                    except:
                        email = ""

                # ✅ Extract website from "Web:" label
                try:
                    website_elem = det.find_element(By.XPATH, ".//a[starts-with(@href, 'http')]")
                    website = website_elem.get_attribute("href")
                except:
                    website = ""

                response.append({
                    "Full Name": full_name,
                    "Address": address,
                    "Phone Number": phone,
                    "Email Address": email,
                    "Website": website,
                    "Certification Type / Details": cert,
                    "Source Directory Name": "BVS e.V."
                })

            except Exception as block_err:
                print(f"❗ Error extracting a row: {str(block_err)}")

    except TimeoutException:
        print("⏱️ Timeout: No detailed results found.")
    except Exception as e:
        print(f"❗ Unexpected error extracting results: {str(e)}")
# Start search loop
for search in search_inputs:
    driver.get("https://www.bvs-ev.de/sachverstaendige-suchen?keyword=")
    time.sleep(2)

    wait = WebDriverWait(driver, 15)
    try:
        cookie = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@id='uc-btn-accept-banner']"))
        )
        driver.execute_script("arguments[0].click();", cookie)
        time.sleep(1)
    except:
        print("✅ Cookie banner not found or already accepted.")
    driver.switch_to.frame("svzFrame")
    try:   
        plz_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@id='plz']")))
        plz_input.clear()
        plz_input.send_keys(search["plz"])

        name_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@id='name']")))
        name_input.clear()
        name_input.send_keys("%")

        umkreis_select = wait.until(EC.presence_of_element_located((By.XPATH, "//select[@id='umkreis']")))
        driver.execute_script("arguments[0].style.display = 'block';", umkreis_select)
        Select(umkreis_select).select_by_visible_text("50 km")

        search_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @value='Suchen']")))
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", search_button)
        time.sleep(5)
        search_button.click()
        
        print("✅ Form submitted successfully.")       
        try:
            extract_results()
            time.sleep(3)
        except Exception as e:
            print(f"🔁 All the Data Extract for the search")
            

    except Exception as e:
        print(f"❌ Error with search: ({search['plz']}) — {type(e).__name__}: {e}")
        driver.save_screenshot(f"error_{search['plz']}_{search['city']}.png")
        continue

driver.quit()



print("✅ BVS scraping with All Serach Inputs complete.")

print(len(response))

# Make a backup before filtering out entries without addresses
backup_response = copy.deepcopy(response)
response = [entry for entry in response if entry.get("Address")]
print(f"🔎 Original: {len(backup_response)} entries")
print(f"✅ After cleaning: {len(response)} entries")

# Save results
df = pd.DataFrame(response)
df.drop_duplicates(inplace=True)
df.to_csv("BVS_e.V._results.csv", index=False)
df.to_excel("BVS_e.V._results.xlsx", index=False)
df.head(10)
