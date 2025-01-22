import datetime
import sys
import os
import requests
import time

from selenium import webdriver
from selenium.webdriver import EdgeOptions
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from urllib3.exceptions import ReadTimeoutError


def save_file(url, path):
    """Download a file from a URL and save it to a specified path."""
    name = os.path.basename(url)
    with open(os.path.join(path, name), 'wb') as f:
        f.write(requests.get(url).content)


def main(url):
    """Scrape SujetExa and download PDFs."""
    service = Service('edgedriver/msedgedriver.exe')

    base_download_dir = os.path.join(os.path.expanduser('~'), 'Downloads\\SujetExa')
    os.makedirs(base_download_dir, exist_ok=True)

    options = EdgeOptions()
    options.add_argument('--headless')
    options.add_argument("--log-level=3")
    browser = webdriver.Edge(service=service, options=options)

    try:
        browser.get(url)
        wait(browser, 120).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        time.sleep(5)
        browser.execute_script("window.scrollBy(0, 500);")

        time.sleep(5)
        browser.execute_script("window.scrollBy(0, 500);")

        menu_title = browser.find_element(By.CLASS_NAME, 'current-menu-parent').find_element(By.TAG_NAME, 'a').text
        category = browser.find_element(By.CLASS_NAME, 'page-title').find_element(By.TAG_NAME, 'span').text

        next_page = True

        while next_page:
            page_number = browser.find_element(By.CLASS_NAME, 'page-numbers.current').text

            page_download_dir = os.path.join(base_download_dir, menu_title, category, page_number)
            os.makedirs(page_download_dir, exist_ok=True)

            posts = browser.find_elements(By.CLASS_NAME, 'post-title.entry-title')
            for post in posts:
                try:
                    print(post.text)
                    post.click()

                    pdf_url = wait(browser, 60).until(EC.visibility_of_element_located(
                        (By.CLASS_NAME, 'wp-block-image'))).find_element(By.TAG_NAME, 'a').get_attribute('href')
                    save_file(pdf_url, page_download_dir)
                    time.sleep(5)

                    browser.execute_script("window.history.back()")
                    wait(browser, 120).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                    browser.execute_script("window.scrollBy(0, 500)")
                except ReadTimeoutError:
                    print(f"!-------- \t ECHEC DU TÉLÉCHARGEMENT - FAUTE DE CONNEXION : {post.text} \t --------!")
                    browser.execute_script("window.history.back()")
                    wait(browser, 120).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                    browser.execute_script("window.scrollBy(0, 500)")

            try:
                next_button = wait(browser, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'next.page-numbers')))
                next_button.click()
            except NoSuchElementException:
                print("Plus de page")
                next_page = False
        browser.quit()
    except WebDriverException and ReadTimeoutError:
        print("----------------------------------------------------------")
        print("!-------- \t ERREUR DE LANCEMENT DE PAGE \t --------!")
        print("----------------------------------------------------------")
        print("!-------- \t VERIFIES TA CONNEXION \t\t --------!")
        print("----------------------------------------------------------")
        print("!-------- \t ATTENTE DE 2 MINUTES DÉPASSÉ \t --------!")
        browser.quit()


if __name__ == '__main__':
    main(sys.argv[1])
