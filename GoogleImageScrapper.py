# -*- coding: utf-8 -*-
"""
Created on Sat Jul 18 13:01:02 2020

@author: OHyic
"""
#import selenium drivers
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException

#import helper libraries
import time

class GoogleImageScraper():
    def __init__(self,headless=True,number_of_images=10,verbose=True):
        self.webdriver_path = "webdriver/chromedriver"
        self.template_search_url = "https://www.google.com/search?q=%s&source=lnms&tbm=isch&sa=X&ved=2ahUKEwie44_AnqLpAhUhBWMBHUFGD90Q_AUoAXoECBUQAw&biw=1920&bih=947"


        self.verbose = verbose
        self.number_of_images = number_of_images
        self.headless=headless
        self.saved_extension = "jpg"
        self.valid_extensions = ["jpg","png","jpeg"]

        self._initialize_driver()


    def reinitialize_driver(self):
        self.close_driver()

        self._initialize_driver()

    def _initialize_driver(self):
        options = Options()
        if self.headless:
            options.add_argument('--headless')

        # self.driver = webdriver.Chrome(self.webdriver_path, chrome_options=options)
        try:
            self.driver = webdriver.Chrome(self.webdriver_path, chrome_options=options)

        except Exception as e:
            print(e)
            
            print("[-] Please update the chromedriver.exe in the webdriver folder according to your chrome version:https://chromedriver.chromium.org/downloads")

    def find_image_urls(self, search_key):
        search_url = self.template_search_url%(search_key)

        if self.verbose:
            print("[+] Scraping for image link for %s. Please wait..."%(search_key, ))

        driver = self.driver
        driver.get(search_url)

        timeout = 5
        try:
            element_present = EC.presence_of_element_located((By.XPATH,
            '//*[@id="islrg"]/div[1]/div[1]/a[1]/div[1]/img'))
            WebDriverWait(driver, timeout).until(element_present)
        except TimeoutException:
            print("Timed out waiting for page to load")
            return None


        for idx in range (1, self.number_of_images + 1):
            try:
                #find and click image
                imgurl = driver.find_element_by_xpath('//*[@id="islrg"]/div[1]/div[%s]/a[1]/div[1]/img'%(str(idx)))
                imgurl.click()

            except Exception:
                # print("[-] Unable to click this photo.")
                continue


            total_time = 0
            while True and total_time < 0.5:
                try:
                    # Select image from the popup
                    time.sleep(0.015)
                    total_time += 0.015
                    class_names = ["n3VNCb"]
                    images = [driver.find_elements_by_class_name(class_name) for class_name in class_names if len(driver.find_elements_by_class_name(class_name)) != 0 ][0]
                    for image in images:
                        # Only download images that starts with http
                        if image.get_attribute("src")[:4].lower() in ["http"]:
                            image_url = image.get_attribute("src")

                            if self.verbose:
                                print("Est img waiting time: %s"%(total_time, ))
                            return image_url

                except Exception:
                    pass



        # driver.close()
        return None
        print("[+] Google search ended")


    def close_driver(self):
        self.driver.close()
