#before running the program do the following:
# Install libraries:
# pip install playwright selectolax
# Install the required browser (paste in the terminal):
# playwright install chromium

from playwright.sync_api import sync_playwright
from selectolax.lexbor import LexborHTMLParser
import json, time


def get_page(playwright, from_place, to_place, departure_date, return_date):
    page = playwright.chromium.launch(headless=False).new_page()
    page.goto('https://www.google.com/travel/flights?hl=en-US&curr=USD')

    # type "From"
    from_place_field = page.query_selector_all('.e5F5td')[0]
    from_place_field.click()
    time.sleep(1)
    from_place_field.type(from_place)
    time.sleep(1)
    page.keyboard.press('Enter')

    # type "To"
    to_place_field = page.query_selector_all('.e5F5td')[1]
    to_place_field.click()
    time.sleep(1)
    to_place_field.type(to_place)
    time.sleep(1)
    page.keyboard.press('Enter')


    # page.keyboard.press('Tab')
    # # type "Departure date"
    # departure_date_field = page.query_selector_all('[jscontroller="s0nXec"] [aria-label="Departure"]')[0]
    # #departure_date_field.click()
    # time.sleep(1)
    # departure_date_field.type(departure_date)
    # time.sleep(1)
    # page.query_selector('.WXaAwc .VfPpkd-LgbsSe').click()
    # time.sleep(1)

    page.keyboard.press('Tab')  # Moves focus to the "Departure date" field
    time.sleep(1)  # Wait for the focus transition

    page.keyboard.type(departure_date)  # Type the departure date
    time.sleep(1)  # Wait for the date to be inputted

    page.keyboard.press('Enter')  # Confirm the date
    time.sleep(1)  # Wait for the calendar widget to close or the page to update

    # # type "Return date"
    # return_date_field = page.query_selector_all('[jscontroller="pxWpE"] [aria-label="Return"]')[0]
    # return_date_field.click()
    # time.sleep(1)
    # return_date_field.type(return_date)
    # time.sleep(1)
    # page.query_selector('.WXaAwc .VfPpkd-LgbsSe').click()
    # time.sleep(1)

    page.keyboard.press('Tab')  # Moves focus to the "Departure date" field
    time.sleep(1)  # Wait for the focus transition

    page.keyboard.type(return_date)  # Type the departure date
    time.sleep(1)  # Wait for the date to be inputted

    page.keyboard.press('Tab')  # Confirm the date
    time.sleep(1)  # Wait for the calendar widget to close or the page to update

    page.keyboard.press('Enter')  # Confirm the date
    time.sleep(5)  # Wait for the calendar widget to close or the page to update

    # # press "Explore"
    # page.query_selector('.MXvFbd .VfPpkd-LgbsSe').click()
    # time.sleep(2)
    #
    # # press "More flights"
    # page.query_selector('.zISZ5c button').click()
    # time.sleep(2)

    parser = LexborHTMLParser(page.content())
    page.close()

    return parser


def scrape_google_flights(parser):
    data = {}

    categories = parser.root.css('.zBTtmb')
    category_results = parser.root.css('.Rk10dc')

    for category, category_result in zip(categories, category_results):
        category_data = []

        for result in category_result.css('.yR1fYc'):
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

        data[category.text().lower().replace(' ', '_')] = category_data

    return data


def run(playwright):
    #here we will change the parameters to get the data from the user
    #this is just for a test
    from_place = 'Israel'
    to_place = 'Paris'
    departure_date = '4-23-2024'
    return_date = '4-30-2024'

    parser = get_page(playwright, from_place, to_place, departure_date, return_date)
    google_flights_results = scrape_google_flights(parser)

    print(json.dumps(google_flights_results, indent=2, ensure_ascii=False))


with sync_playwright() as playwright:
    run(playwright)