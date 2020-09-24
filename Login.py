from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import json
from woocommerce import API
from selenium.webdriver.support.ui import Select


with open('Login_Info.json', 'r') as f:
    key = json.load(f)
    USERNAME = key['username']
    PASSWORD = key['password']
    CONSUMER_KEY = key['consumer_key']
    CONSUMER_SECRET = key['consumer_secret']


class Woocommerce:
    def __init__(self):
        self.consumer_key = CONSUMER_KEY
        self.consumer_secret = CONSUMER_SECRET
        self.url = 'https://calpros.net'
        self.wcapi = self.get_api_info()
        self.automation = EZ_Web_Automation()

    def get_api_info(self):

        return API(
            url=self.url,
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            version='wc/v3'
        )

    def get_complete_orders_data(self, params):
        complete_orders = self.wcapi.get('orders', params=params).json()
        self.process_orders(complete_orders)
        return complete_orders

    def process_orders(self, new_orders):
        ezlynk_order = ''
        efilive_order = ''
        for info in new_orders:
            meta = info['line_items'][0]['name']
            if meta == 'Ez-Lynk Order':
                ez_order = info['line_items'][0]['meta_data']
                ez_order_details = []
                for ez_data in ez_order:
                    ez_info = ez_data['value']
                    ez_order_details.append(ez_info)
                    ezlynk_order = ez_order_details
                self.fullfill_ezlynk_order(ezlynk_order)
            elif meta == 'Ez-Lynk Wholesale':
                ez_order = info['line_items'][0]['meta_data']
                ez_order_details = []
                for ez_data in ez_order:
                    ez_info = ez_data['value']
                    ez_order_details.append(ez_info)
                    ezlynk_order = ez_order_details
                self.fullfill_ezlynk_wholesale_order(ezlynk_order)
            elif meta == 'EFI Tune Order':
                efi_order = info['line_items'][0]['meta_data']
                efi_order_details = []
                for efi_data in efi_order:
                    efi_info = efi_data['value']
                    efi_order_details.append(efi_info)
                    efilive_order = efi_order_details
                # self.efi_order_info(efilive_order)

                #return ezlynk_order, efilive_order

    def fullfill_ezlynk_order(self, ez_order_details):
        vehicle_type = ez_order_details[2]
        lynk_time = ez_order_details[3]
        vin_number = ez_order_details[4]
        self.automation.ez_web_access()
        self.automation.ez_auto_lynk()
        self.automation.ez_vehicle_fuel_type()
        self.automation.lynk_type(lynk_time)
        self.automation.enter_vin_number(vin_number)
        self.automation.select_rating_for_profile(lynk_time)

    def fullfill_ezlynk_wholesale_order(self, ez_order_details):
        vehicle_type = ez_order_details[2]
        lynk_time = ez_order_details[1]
        vin_number = ez_order_details[2]
        self.automation.ez_web_access()
        self.automation.ez_auto_lynk()
        self.automation.ez_vehicle_fuel_type()
        self.automation.lynk_type(lynk_time)
        self.automation.enter_vin_number(vin_number)
        self.automation.select_rating_for_profile(lynk_time)
#         self.automation.submit_order()
#
#     def  efi_order_info(self, efi_product_specs):
#         efi_order_details = efi_product_specs
#         year = efi_order_details[0]
#         power_level = efi_order_details[1]
#         body_type = efi_order_details[2]
#         trans_type = efi_order_details[3]
#         emissions = efi_order_details[4]
#         trans_tune = efi_order_details[5]
#         turbo = efi_order_details[6]
#         injectors = efi_order_details[7]
#         print(year,power_level,body_type,trans_type,emissions,trans_tune,turbo,injectors)
#
    def filter_orders(self, orders):
        try:
            for order in orders:
                data = self.change_status_of_order(order['id'], "completed")
        except:
            print('Sorry Your Order Could Not Be Processed')
            exit(0)

    def change_status_of_order(self, order_id, status):
        data = {
            "status": status
        }

        return self.wcapi.put(f"orders/{order_id}", data).json()
#

class EZ_Web_Automation:
    def __init__(self):
        self.username = USERNAME
        self.password = PASSWORD
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.url = 'https://cloud.ezlynk.com/'
        self.tech_account = 'https://cloud.ezlynk.com/wp/customers?sortBy=name&sortDir=asc'
        self.vin_click = 'https://cloud.ezlynk.com/wp/autosharing/queue?sortBy=value&sortDir=asc&vin=true'
        self.driver = webdriver.Chrome("/home/ubuntu/ezlynkapi/EZ-EFI-Order_Script_Automation/chromedriver", chrome_options=self.chrome_options, service_args=['--verbose', '--log-path=/tmp/chromedriver.log'])
    
    def ez_web_access(self):
        self.driver.get(self.url)
        self.driver.find_element_by_id('Email').send_keys(self.username)
        self.driver.find_element_by_id('Password').send_keys(self.password)
        self.driver.find_element_by_id('Password').send_keys(Keys.ENTER)

    def ez_auto_lynk(self):
        self.driver.get(self.vin_click)
        self.driver.find_element_by_xpath('/html/body/div[1]/div[3]/app-router-outlet/app-auto-lynk-container/app-sticky-container/app-container/app-button-icon').click()
        time.sleep(1)

    def ez_vehicle_fuel_type(self):
        button = self.driver.find_element_by_css_selector("body > div.modal.ng-scope.ng-isolate-scope.in > div > div > div > div.select-vehicle-type-state-container.ng-pristine.ng-valid > div.state-buttons-container > button.btn.brand-button.next-state")
        button.click()
        time.sleep(1)

    def lynk_type(self, lynk_time):
        if lynk_time == 'Zero Lynk':
            self.driver.find_element_by_css_selector('body > div.modal.ng-scope.ng-isolate-scope.in > div > div > div > div.choose-capabilities-state-container.ng-pristine.ng-valid > div.modal-body > div.lynk-capabilities-buttons-container > lynk-capabilities-buttons > div > ul:nth-child(2) > li.lynk-button > button').click()
            time.sleep(1)
        elif '4 Week' in lynk_time:
            try:
                self.driver.find_element_by_css_selector('body > div.modal.ng-scope.ng-isolate-scope.in > div > div > div > div.choose-capabilities-state-container.ng-pristine.ng-valid > div.modal-body > div.lynk-capabilities-buttons-container > lynk-capabilities-buttons > div > ul:nth-child(3) > li.lynk-button > button').click()
                time.sleep(1)
            except:
                print("Could not process order because you are currently out of tokens. Please refill tokens to be able to process order")
                exit(0)
        elif 'lifetime' in lynk_time:
            try:
                self.driver.find_element_by_css_selector('body > div.modal.ng-scope.ng-isolate-scope.in > div > div > div > div.choose-capabilities-state-container.ng-pristine.ng-valid > div.modal-body > div.lynk-capabilities-buttons-container > lynk-capabilities-buttons > div > ul:nth-child(4) > li.lynk-button > button').click()
                time.sleep(1)
            except:
                print("Could not process order because you are currently out of tokens. Please refill tokens to be able to process order")
                exit(0)

    def enter_vin_number(self, vin_id_number):
        self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div/div[3]/div[2]/div[2]/select').click()
        time.sleep(1)
        self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div/div[3]/div[2]/div[2]/select/option[2]').click()
        time.sleep(1)
        self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div/div[3]/div[2]/div[3]/div/div/div[1]/div[1]/input').send_keys(vin_id_number)
        agent_id_next = self.driver.find_element_by_css_selector('body > div.modal.ng-scope.ng-isolate-scope.in > div > div > div > div.choose-creation-item-state-container.ng-invalid.ng-invalid-required.ng-valid-server-validation-failed.ng-valid-agent-ids-symbols.ng-valid-agent-ids-length.ng-valid-mask.ng-valid-vin-length.ng-valid-vin-duplicated.ng-valid-vin-server-validation-failed.ng-valid-vin-symbols.ng-dirty.ng-valid-parse > div.state-buttons-container > button.btn.brand-button.next-state')
        agent_id_next.click()
        time.sleep(1.5)

    def select_rating_for_profile(self, profile_rating):
        if 'Single' in profile_rating :
            self.driver.find_element_by_css_selector('body > div.modal.ng-scope.ng-isolate-scope.in > div > div > div > div.modal-message.ecu-profile-edit-auto-sharing > div.modal-body > ecu-profile-edit-auto-sharing-component > div.ecu-profile-rate-tag-container > div:nth-child(3)').click()
            self.driver.find_element_by_css_selector('body > div.modal.ng-scope.ng-isolate-scope.in > div > div > div > div.modal-message.ecu-profile-edit-auto-sharing > div.modal-body > div > button.btn.brand-button.next-state').click()
            self.driver.find_element_by_css_selector('body > div.modal.ng-scope.ng-isolate-scope.in > div > div > div > div.confirm-state-container.ng-pristine.ng-valid > div.state-buttons-container > button.btn.brand-button.ok-state').click()
            time.sleep(10)
            self.driver.close()
        elif 'SOTF' in profile_rating:
            self.driver.find_element_by_css_selector('body > div.modal.ng-scope.ng-isolate-scope.in > div > div > div > div.modal-message.ecu-profile-edit-auto-sharing > div.modal-body > ecu-profile-edit-auto-sharing-component > div.ecu-profile-rate-tag-container > div.rate-tag.ng-scope.enabled').click()
            self.driver.find_element_by_css_selector('body > div.modal.ng-scope.ng-isolate-scope.in > div > div > div > div.modal-message.ecu-profile-edit-auto-sharing > div.modal-body > div > button.btn.brand-button.next-state').click()
            self.driver.find_element_by_css_selector('body > div.modal.ng-scope.ng-isolate-scope.in > div > div > div > div.confirm-state-container.ng-pristine.ng-valid > div.state-buttons-container > button.btn.brand-button.ok-state').click()
            time.sleep(10)
            self.driver.close()
#
#     # def submit_order(self):
#     #     submit_lynk = self.driver.find_element_by_xpath('body > div.modal.ng-scope.ng-isolate-scope.in > div > div > div > div.confirm-state-container.ng-pristine.ng-valid > div.state-buttons-container > button.btn.brand-button.ok-state')
#     #     submit_lynk.click()


if __name__ == '__main__':
    data = Woocommerce()
    params = {
        "status": 'processing'
    }
    orders = data.get_complete_orders_data(params)
    data.filter_orders(orders)


















