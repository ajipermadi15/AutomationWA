import time
import os
import sys
from urllib.parse import quote

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains

import pandas as pd
import numpy as np

from log import record_message

class AutomationWA:
    def __init__(
            self, 
            wait_time: int = 600,
            sleep_time: int = 5,
    ) -> None:      
        self.web = webdriver.Chrome(options = self.options)
        self.web.implicitly_wait(wait_time)
        self.wait = WebDriverWait(self.web, wait_time)

        self.files_folder_PATH = os.path.realpath("files")
        # self.data_folder_PATH = 'data/'

        self.sleep_time = sleep_time

    @property
    def options(self) -> None:
        options = Options()
        if sys.platform == "win32":
            options.add_argument("--profile-directory=Default")
            options.add_argument("--user-data-dir=C:/Temp/ChromeProfile")
        else:
            options.add_argument("start-maximized")
            options.add_argument("--user-data-dir=./User_Data")

        return options
    
    def login(self) -> None:
        website = "https://web.whatsapp.com/"    
        self.web.get(website)
        
        # barcode_XPATH = '//*[@id="app"]//*[@aria-label="Scan me!"]'
        # self.wait.until_not(EC.presence_of_element_located((By.XPATH, barcode_XPATH)))
        # time.sleep(self.sleep_time)
        menu_XPATH = '//*[@id="app"]//*[@data-icon="menu"]/..'
        self.wait.until(
                EC.presence_of_element_located((By.XPATH, menu_XPATH)))
        
        print('login completed!')

    def logout(self) -> None:
        get_url = self.web.current_url
        website = "https://web.whatsapp.com/"
        
        if str(get_url) != website:
            self.web.get(website)

        menu_XPATH = '//*[@id="app"]//*[@data-icon="menu"]/..'
        logout_XPATH = '//*[@id="app"]//*[@aria-label="Log out"]/..'
        logout_confirm_XPATH = '//*[@id="app"]/div/span[2]/div/div/div/div/div/div/div[3]/div/button[2]/div/div'
        
        menu_button = self.web.find_element(By.XPATH, menu_XPATH)
        menu_button.click()

        logout_button = self.web.find_element(By.XPATH, logout_XPATH)
        logout_button.click()

        logout_confirm_button = self.wait.until(
                EC.presence_of_element_located((By.XPATH, logout_confirm_XPATH)))
        logout_confirm_button.click()

        time.sleep(self.sleep_time)
        print('logout completed!')


    def read_database(
            self,
            # filename: str,
            file_PATH: str,
            delimiter: str = ';'
    ) -> None:
        """
        
        """
        format = file_PATH.split('.')[-1]

        # file_PATH = os.path.realpath(f"{self.data_PATH}{filename}")
        if format == 'csv':
            self.data = pd.read_csv(file_PATH, delimiter=delimiter, na_values='')
        elif format == 'xlxs':
            pass
        
    def new_tab(self) -> None:
        self.web.switch_to.new_window('tab')
        current_tab = self.web.current_window_handle

        all_tabs = self.web.window_handles

        self.web.switch_to.window(all_tabs[0])
        self.web.close()
        self.web.switch_to.window(current_tab)

    def send_to_multiple_receivers(
            self,
            data_file_PATH: str,
            delimiter: str = ';',
            start: int = 1,
            end: int = -999, #end>start>0,
            custom_caption: str = None,
            auto_logout: bool = False,
            gui: bool = False,
    ) -> None:
        """
        
        """
        self.read_database(data_file_PATH, delimiter)
        n_data = len(self.data)
        if end == -999:
            end = n_data
        
        if not(end > start) and not(start > 0):
            pass #raise error

        for index, row in self.data[start-1:end].iterrows():
            # print(index)

            name = row["name"]
            number = row["number"]
            filename = row["filename"]
            caption = row["caption"]
            attachment_type = row["type"]

            # print(name, number, filename, caption)

            if custom_caption != None:
                caption = custom_caption.replace('%n', name)           

            if attachment_type == 3: #no atttachment
                # print(caption)
                self.send_messages(number, caption)

                record_message(_time=time.localtime(), name=name, number=number, _type="")
            else:
                file_PATH = f"{self.files_folder_PATH}/{filename}"
                self.send_attachment(number, file_PATH, caption, attachment_type)

                record_message(_time=time.localtime(), name=name, number=number, _type="file", filename=filename)
                # print(f'{filename} has sent to {name}.')

            if gui:
                if index != (end - 1):
                    self.update_progress_bar()
                else:
                    self.update_progress_bar(finished=True)

            if index != (end - 1):
                self.new_tab()
            else:
                if auto_logout:
                    time.sleep(self.sleep_time)
                    self.logout()
                time.sleep(3)
                self.web.close()

    def send_messages(
            self, 
            number: str,
            message: str,
    ) -> None:
        """ 
        
        """
        website = f"https://web.whatsapp.com/send?phone={number}&text"
        self.web.get(website)
        print(self.web.current_url)

        message_box_XPATH = '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]/p'
        message_box = self.web.find_element(By.XPATH, message_box_XPATH)

        for line in message.split("\n"):
                message_box.send_keys(line)
                ActionChains(self.web).key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(
                    Keys.ENTER
                ).key_up(Keys.SHIFT).perform()

        message_send_XPATH = '//*[@id="main"]/footer//*[@data-icon="send"]/..'
        message_send_button = self.web.find_element(By.XPATH, message_send_XPATH)
        message_send_button.click()
        time.sleep(self.sleep_time)

    def send_attachment(
            self,
            number: str,
            # filename: str,
            file_PATH: str,
            caption: str = '',
            attachment_type: bool = 0 #0: file, 1: photo/video
    ) -> None:
        """
        
        """
        website = f"https://web.whatsapp.com/send?phone={number}&text"
        self.web.get(website)
        
        attach_XPATH = '//*[@id="main"]/footer//*[@data-icon="attach-menu-plus"]/..'
        send_button_XPATH = '//*[@id="app"]//*[@data-icon="send"]/..'
        
        if attachment_type == 0: 
            file_upload_XPATH = '//input[@accept="*"]'
            caption_box_XPATH = '//*[@id="app"]/div/div[2]/div[2]/div[2]/span/div/div/div/div[2]/div/div[1]/div[3]/div/div/div[1]/div[1]'
        elif attachment_type == 1:
            media_upload_XPATH = '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]'
            caption_box_XPATH = '//*[@id="app"]/div/div[2]/div[2]/div[2]/span/div/div/div/div[2]/div/div[1]/div[3]/div/div/div[2]/div[1]/div[1]'
        else:
            pass #Raise error

        attach_button = self.web.find_element(By.XPATH, attach_XPATH)
        attach_button.click()

        if attachment_type == 0:
            doc_upload = self.web.find_element(By.XPATH, file_upload_XPATH)
            doc_upload.send_keys(file_PATH)
        else:
            media_upload = self.web.find_element(By.XPATH, media_upload_XPATH)
            media_upload.send_keys(file_PATH)
            print('uploaded!')

        if (caption not in ['', None, np.nan]):
            # print(caption)
            caption_box = self.web.find_element(By.XPATH, caption_box_XPATH)
            for line in caption.split("\n"):
                caption_box.send_keys(line)
                ActionChains(self.web).key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(
                    Keys.ENTER
                ).key_up(Keys.SHIFT).perform()
        print('caption done!')
        doc_send_button = self.web.find_element(By.XPATH, send_button_XPATH)
        doc_send_button.click()
        print('sent!')
        
        time.sleep(self.sleep_time)
        # self.wait.until_not(EC.presence_of_element_located((By.XPATH, '//*[@id="main"]//*[@data-icon="msg-time"]')))





# data_folder_PATH = 'data'
# filename = 'receiver_data.csv'
# data_file_PATH = os.path.realpath(f"{data_folder_PATH}/{filename}")

# automation = AutomationWA()

# automation.login()
# automation.send_to_multiple_receivers(data_file_PATH, start=3, end=5, auto_logout=False)