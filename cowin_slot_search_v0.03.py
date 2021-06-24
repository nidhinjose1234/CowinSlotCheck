import datetime
import json
import requests
from urllib.parse import quote
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

url_host = 'https://cdn-api.co-vin.in/api/'
api_search = 'v2/appointment/sessions/public/calendarByPin'
my_no = '+919743355533'


def send_message(phone_no, message):
    global chrome
    parsed = quote(message)
    chrome.get(f'https://web.whatsapp.com/send?phone={phone_no}&text={parsed}')
    time.sleep(6)       # Wait for send button to load
    ActionChains(chrome).send_keys(Keys.ENTER).perform()
    time.sleep(2)


def slot_check(phone, pincode, vacc, age, dose_no, date):
    slot_found = False
    url = url_host + api_search
    response = requests.get(url, {'pincode': pincode, 'date': date})
    if response.status_code == 200:
        result = json.loads(response.text)
        centers = result.get('centers')
        for center in centers:
            sessions = center.get('sessions')
            for session in sessions:
                dose_find = 'available_capacity_dose' + dose_no
                if session.get('min_age_limit') == age and session.get(dose_find) > 1 and \
                        (not (bool(vacc)) or session.get('vaccine') == vacc):

                    slot_found = True
                    time_now = datetime.datetime.now().time().strftime('%H:%M:%S')
                    # Print a system output
                    print(f'{session.get(dose_find)} slots for Dose {dose_no} Opened in '
                          f'{center.get("name")} at pincode {pincode} for date {session.get("date")} '
                          f'at {time_now}')
                    # Send a Message
                    send_message(phone,
                                 f'{session.get(dose_find)} slots  for Dose {dose_no} Opened in '
                                 f'{center.get("name")} at pincode {pincode} for date {session.get("date")}')
    else:
        time.sleep(10)               # Wait for 10 seconds before next run
    return slot_found


def process(phn, pincodes, vax, chk_age, vax_dose, today, wait_time):

    while True:
        try:
            for code in pincodes:
                found = slot_check(phn, code, vax, chk_age, vax_dose, today)
                if found:
                    time.sleep(10)
                else:
                    time.sleep(wait_time)       # Before next run

        except TimeoutError or OSError:
            # send_message(my_no, 'Timeout while fetching slots, check execution')
            time_now = datetime.datetime.now().time().strftime('%H:%M:%S')
            print(f'Timeout error at {time_now}')
            time.sleep(60)
            break
        except KeyboardInterrupt:
            print('Thank you')
            break
        except:
            time_now = datetime.datetime.now().time().strftime('%H:%M:%S')
            print(f'Connection error at {time_now}')
            # send_message(my_no, 'Connection error while fetching slots, check execution')
            time.sleep(60)
            break


if __name__ == '__main__':
    mobile = input('Mobile number to notify (Including Country Code e.g. +919123456789): ')
    vaccine = input('Vaccine Name (All caps, leave blank to check both): ')
    min_age = input('Age group (18/40/45): ')
    dose = input('Dose Number (1/2): ')
    wait = int(input('Time gap between fetch (3/6/9 according to number of parallel sessions) in seconds: '))
    pin_str = input('Pincodes to search (Multiple separated by spaces): ')
    pins = pin_str.split(' ')
    pins = list(map(lambda pin: int(pin), pins))
    check_date = datetime.datetime.now().date()
    tod = check_date.strftime('%d-%m-%Y')

# Login to Whatsapp
    chrome = webdriver.Chrome('chromedriver')  # Use the downloaded chromedriver
    chrome.get('https://web.whatsapp.com/')
    chrome.maximize_window()
    login = input('Enter any key after login: ')

    while True:
        try:
            process(mobile, pins, vaccine, min_age, dose, tod, wait)
        except KeyboardInterrupt:
            print('Thank you')
            break
        except:
            time.sleep(60)      # Try again after a minute
            continue

        time.sleep(30)  # Search resume after 30 seconds
