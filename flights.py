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


def get_page(from_place, to_place, departure_date, return_date):
    options = Options()
    options.headless = True  # Run Chrome in headless mode
    options.add_argument("--disable-webusb") 
    driver = webdriver.Chrome(options=options)
    try:

        # Navigate to Google Flights
        driver.get('https://www.google.com/travel/flights?hl=en-US&curr=USD')
        time.sleep(10)
        wait = WebDriverWait(driver, 10)
        # Interact with the web page to input flight details
        from_place_field = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input.II2One.j0Ppje.zmMKJ.LbIaRd")))
        if from_place_field:
              # Wait for the "From" input field to be clickable and interact with it
            from_place_field.click()
            from_place_field.clear()
            from_place_field.send_keys(from_place)
            from_place_field.send_keys(Keys.TAB)
            time.sleep(2)  # Wait for focus transition
            from_place_field.send_keys(Keys.TAB)
            time.sleep(3)
            to_place_field = driver.switch_to.active_element  # Switch to the active element, which should be the "Where to?" field
            to_place_field.send_keys(to_place)
            time.sleep(2)
            to_place_field.send_keys(Keys.TAB)
            time.sleep(2)  # Wait for focus transition
            to_place_field.send_keys(Keys.TAB)
            time.sleep(2)
            from_date_field = driver.switch_to.active_element
            from_date_field.send_keys(departure_date)
            from_date_field.send_keys(Keys.TAB)
            time.sleep(2)  # Wait for focus transition
            from_date_field.send_keys(Keys.TAB)
            time.sleep(2)
            return_date_field = driver.switch_to.active_element
            return_date_field.send_keys(return_date)

      



        # Initiate the search
        search_button = driver.find_element("css selector", ".VfPpkd-LgbsSe VfPpkd-LgbsSe-OWXEXe-k8QpJ VfPpkd-LgbsSe-OWXEXe-Bz112c-M1Soyc nCP5yc AjY5Oe LQeN7 TUT4y zlyfOd")
        search_button.click()  # Click the search button to initiate the search
        time.sleep(5)  # Wait for the search results to load

        time.sleep(5)  # Wait for search results

        # Parse the page content
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        return soup

    finally:
        driver.quit()


def scrape_google_flights(soup):
    data = {}
    try:
        categories = soup.select('.zBTtmb')
        category_results = soup.select('.Rk10dc')

        for category, category_result in zip(categories, category_results):
            category_data = []

            for result in category_result.select('.yR1fYc'):
                date = result.css('[jscontroller="cNtv4b"] span')
                departure_date = date[0].text()
                arrival_date = date[1].text()
                company = result.css_first('.Ir0Voe .sSHqwe').text()
                duration = result.css_first('.AdWm1c.gvkrdb').text()
                stops = result.css_first('.EfT7Ae .ogfYpf').text()
                emissions = result.css_first('.V1iAHe .AdWm1c').text()
                emission_comparison = result.css_first('.N6PNV').text()
                price = result.css_first('.U3gSDe .FpEdX span').text()
                price_type = result.css_first('.U3gSDe .N872Rd').text() if result.css_first('.U3gSDe .N872Rd') else None

                flight_data = {
                    'departure_date': departure_date,
                    'arrival_date': arrival_date,
                    'company': company,
                    'duration': duration,
                    'stops': stops,
                    'emissions': emissions,
                    'emission_comparison': emission_comparison,
                    'price': price,
                    'price_type': price_type
                }

                airports = result.css_first('.Ak5kof .sSHqwe')
                service = result.css_first('.hRBhge')

                if service:
                    flight_data['service'] = service.text()
                else:
                    flight_data['departure_airport'] = airports.css_first('span:nth-child(1) .eoY5cb').text()
                    flight_data['arrival_airport'] = airports.css_first('span:nth-child(2) .eoY5cb').text()

                category_data.append(flight_data)

            data[category.get_text().lower().replace(' ', '_')] = category_data

    except Exception as e:
        print(f"An error occurred in scrape_google_flights: {e}")
        raise

    return data


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
