import os
import re
import shutil
import time

from selenium import webdriver
from selenium.webdriver.common.by import By


def scrape_data(folder_name):
    driver = webdriver.Chrome()
    driver.get("https://www.rgd.gov.lk/web/index.php?lang=en")
    time.sleep(2)

    module = driver.find_elements(By.CLASS_NAME, "moduletable")[1]
    inner_module = module.find_element(By.CLASS_NAME, "custom")
    module_cards = inner_module.find_elements(By.XPATH, "./div")

    folder = get_folder(folder_name)
    for card in module_cards:
        inner_card = card.find_element(By.CLASS_NAME, "insideCOn")
        card_heading = inner_card.find_element(By.XPATH, "./h2").text
        print(card_heading)
        inner_links = inner_card.find_elements(By.XPATH, "./ul/li/a")

        links_dict = {}

        for link in inner_links:
            links_dict[link.text] = link.get_attribute("href")

        for link in links_dict:
            category = link
            print(category)
            driver.get(links_dict[link])
            time.sleep(2)

            accordions = driver.find_elements(By.CLASS_NAME, "accordion-group")
            print(len(accordions))
            for grp in accordions:
                title = grp.find_element(By.CLASS_NAME, "accordion-heading").text
                print(title)

                grp.click()
                time.sleep(2)
                content = grp.find_element(By.CLASS_NAME, "accordion-body")
                cleaned_content = clean_content(content.get_attribute("textContent"))

                important_links = content.find_elements(By.TAG_NAME, "a")
                print(len(important_links))
                link_content = ""

                for l in important_links:
                    link_text = l.get_attribute('textContent')
                    if not link_text:
                        link_text = l.get_attribute('href').split("/")[-1].split(".")[0]
                    link_content = link_content + f"- {link_text} - {l.get_attribute('href')}\n"

                file_path = get_file_path(folder, title)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(f"""# {title}
## category: {card_heading}/{category}

{cleaned_content}

Important links in this guide:
{link_content}

For more information: {driver.current_url}
""")
                print(f"Markdown file created at: {file_path}\n")
            break
        if card_heading == "Civil Registration":
            break
    driver.quit()


def get_folder(folder_name):
    parent_dir = os.path.abspath(os.path.join(os.getcwd(), "."))
    folder_path = os.path.join(parent_dir, folder_name)
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    os.makedirs(folder_path)
    return folder_path


def clean_content(content):
    content = content.strip()
    content = re.sub(r'\n\s*\n+', '\n', content)
    lines = content.strip().splitlines()
    content = "\n".join(lines[1:])
    return content


def get_file_path(folder_path, title):
    sanitized_title = re.sub(r'[\/\\:*?"<>|]', '_', title)  # Replace illegal characters
    file_name = "_".join(sanitized_title.lower().split()) + ".md"
    file_path = os.path.join(folder_path, file_name)
    return file_path


scrape_data(folder_name="rgd_data")
