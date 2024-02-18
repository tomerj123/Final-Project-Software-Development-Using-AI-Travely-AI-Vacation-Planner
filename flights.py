import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException


# def get_page(from_place, to_place, departure_date, return_date):
#     options = Options()
#     options.headless = True
#     options.add_argument("--disable-webusb")
#     driver = webdriver.Chrome(options=options)

#     try:
#         driver.get('https://www.google.com/travel/flights?hl=en-US&curr=USD')
#         wait = WebDriverWait(driver, 20)

#         # Interact with the "From" input field
#         from_place_field = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input.II2One.j0Ppje.zmMKJ.LbIaRd")))
#         from_place_field.click()
#         from_place_field.clear()
#         from_place_field.send_keys(from_place)
#         from_place_field.send_keys(Keys.TAB)  # Move focus to the next field

#         # Ensure the "Where to?" field is focused and interact with it
#         wait.until(lambda driver: driver.switch_to.active_element.get_attribute('aria-label') == 'Where to?')
#         to_place_field = driver.switch_to.active_element
#         to_place_field.send_keys(to_place)
#         to_place_field.send_keys(Keys.TAB)  # Move focus to the next field

#         # Interact with "Departure" and "Return" date fields
#         # Similar approach as above using wait.until and driver.switch_to.active_element
#         departure_date_field = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[placeholder='Departure']")))
#         if departure_date_field:
#             departure_date_field.click()
#             departure_date_field.clear()
#             time.sleep(3) 
#             departure_date_field.send_keys(departure_date)
#             time.sleep(3) 
#             departure_date_field.send_keys(Keys.TAB)
#             time.sleep(3)  # Wait for focus transition
#         return_date_field = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[placeholder='Return']")))
#         if return_date_field:
#             return_date_field.click()
#             return_date_field.clear()
#             time.sleep(3) 
#             return_date_field.send_keys(return_date)
#             time.sleep(3) 
#             return_date_field.send_keys(Keys.TAB)
#             time.sleep(3)

#         # Initiate the search
#         search_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Search']")))  # Adjusted for a more generic selector
#         search_button.click()

#         wait.until(lambda driver: "results" in driver.current_url)  # Wait for the search results page to load

#         # Parse the page content
#         soup = BeautifulSoup(driver.page_source, 'html.parser')
#         return soup

#     finally:
#         driver.quit()
def get_page(from_place, to_place, departure_date, return_date):
    options = Options()
    options.add_argument("--disable-webusb")
    options.headless = True  # Run Chrome in headless mode
    driver = webdriver.Chrome(options=options)
    

    try:
        driver.get('https://www.google.com/travel/flights?hl=en-US&curr=USD')
        wait = WebDriverWait(driver, 10)

        # Interact with the "From" input field
        from_place_field = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input.II2One.j0Ppje.zmMKJ.LbIaRd")))
        from_place_field.click()
        from_place_field.clear()
        from_place_field.send_keys(from_place)
        
        # Use TAB key to navigate to the "Where to?" input field
        from_place_field.send_keys(Keys.TAB)
        time.sleep(3)  # Wait for focus transition
        from_place_field.send_keys(Keys.TAB)
        time.sleep(3)  # Wait for focus to reach the "Where to?" field

        # Assuming the focus is now on the "Where to?" field, start typing the destination
        # to_place_field = driver.switch_to.active_element
        # while to_place_field.get_attribute('accessible_name') != 'Where to? ':
        #     from_place_field.send_keys(Keys.TAB) 
        #     to_place_field = driver.switch_to.active_element # Move focus to the next field
        to_place_field = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[aria-label='Where to? ']")))
        if to_place_field:
            time.sleep(3)  # Wait for the field to be focused
            to_place_field.send_keys(to_place)
            time.sleep(3)  # Wait for the input to be processed
            to_place_field.send_keys(Keys.TAB)  # Move focus to the next field
            time.sleep(3)  # Wait for focus transition
            to_place_field.send_keys(Keys.TAB)  # Move focus to the next field
            time.sleep(3)  # Wait for focus transition
            to_place_field.send_keys(Keys.TAB)
            time.sleep(3)  # Wait for focus transition
        # Interact with the "Departure" and "Return" date fields
        departure_date_field = driver.switch_to.active_element
        while departure_date_field.accessible_name != 'Departure':
            departure_date_field.send_keys(Keys.TAB) 
            time.sleep(3)
            departure_date_field = driver.switch_to.active_element

        time.sleep(3) 
        departure_date_field.send_keys(departure_date)
        time.sleep(3) 
        departure_date_field.send_keys(Keys.TAB)
        time.sleep(3)  # Wait for focus transition
        # return_date_field = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[placeholder='Return']")))
        return_date_field = driver.switch_to.active_element
        while return_date_field.accessible_name != 'Return':
            return_date_field.send_keys(Keys.TAB) 
            time.sleep(3)
            return_date_field = driver.switch_to.active_element

        if return_date_field:
            time.sleep(3) 
            return_date_field.send_keys(return_date)
            time.sleep(3) 
            return_date_field.send_keys(Keys.TAB)
            time.sleep(3)
      


      



        search_button = driver.switch_to.active_element
        time.sleep(3)
        search_button.click()

        # Wait for search results to load
        time.sleep(5)  # Consider using WebDriverWait here as well for a more reliable wait

        # Parse the page content
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        return soup
    except NoSuchElementException as e:
        print(f"Element not found: {e}")
    except TimeoutException as e:
        print(f"Operation timed out: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        driver.quit()




def scrape_google_flights(soup):
    flights = []
    try:
    # Each flight information is enclosed in a 'div' with class 'gQ6yfe m7VU8c'
        flight_containers = soup.select('.gQ6yfe.m7VU8c')

        for flight in flight_containers:
        # Extracting airline
            airline = flight.select_one('.sSHqwe.tPgKwe.ogfYpf span').get_text() if flight.select_one('.sSHqwe.tPgKwe.ogfYpf span') else None

            # Extracting price
            price = flight.select_one('.YMlIz.FpEdX span').get_text() if flight.select_one('.YMlIz.FpEdX span') else None

            # Extracting flight type (e.g., Nonstop)
            flight_type = flight.select_one('.EfT7Ae.AdWm1c.tPgKwe span').get_text() if flight.select_one('.EfT7Ae.AdWm1c.tPgKwe span') else None

            # Extracting departure and arrival times
            departure_time = flight.select_one('.wtdjmc.YMlIz.ogfYpf.tPgKwe').get_text() if flight.select_one('.wtdjmc.YMlIz.ogfYpf.tPgKwe') else None
            arrival_time = flight.select_one('.XWcVob.YMlIz.ogfYpf.tPgKwe').get_text() if flight.select_one('.XWcVob.YMlIz.ogfYpf.tPgKwe') else None

            # Extracting total duration
            duration = flight.select_one('.gvkrdb.AdWm1c.tPgKwe.ogfYpf').get_text() if flight.select_one('.gvkrdb.AdWm1c.tPgKwe.ogfYpf') else None

            # Extracting departure and arrival airports using more specific selectors based on the provided snippets
            departure_airport_div = flight.select_one('.ZHa2lc.tdMWuf.y52p7d')
            departure_airport_name = departure_airport_div.get_text(strip=True) if departure_airport_div else None
            airport_code_span = departure_airport_div.select_one('span[dir="ltr"]')
            if airport_code_span:
                departure_airport_code = airport_code_span.get_text(strip=True).strip('()')
            else:
                departure_airport_code = None
            # Extracting arrival airport name and code
            arrival_airport_div = flight.select_one('.FY5t7d.tdMWuf.y52p7d')
            arrival_airport_name = arrival_airport_div.get_text(strip=True) if arrival_airport_div else None
            airport_code_span = arrival_airport_div.select_one('span[dir="ltr"]')
            if airport_code_span:
                arrival_airport_code = airport_code_span.get_text(strip=True).strip('()')
            else:
                arrival_airport_code = None


            flight_info = {
                'airline': airline,
                'price': price,
                'flight_type': flight_type,
                'departure_time': departure_time,
                'arrival_time': arrival_time,
                'duration': duration,
                'departure_airport': departure_airport_name + " " + departure_airport_code,
                'arrival_airport': arrival_airport_name + " " + arrival_airport_code
            }

            flights.append(flight_info)
    except Exception as e:
        print(f"An error occurred while scraping flight information: {e}")
    finally:
        return flights




def run(from_place, to_place, departure_date, return_date):
    try:
        soup = get_page(from_place, to_place, departure_date, return_date)
        google_flights_results = scrape_google_flights(soup)
        return json.dumps(google_flights_results, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"An error occurred during the scraping process: {e}")

# Example usage
# results = run("NYC", "LAX", "2023-10-01", "2023-10-15")
# print(results)
