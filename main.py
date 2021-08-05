
"""Script that scrapes informationf from https://apps.cra-arc.gc.ca/ebci/hacc/srch/pub/dsplyBscSrch?request_locale=en"""
import bs4 as bs
from selenium import webdriver
import time
import csv
import json
import pandas as pd

cadets = pd.read_csv("cadets.csv")
existing = cadets["Charity Name"].tolist()

keyword = "squadron" #Cadet, cadets, squadron

url = "https://apps.cra-arc.gc.ca/ebci/hacc/srch/pub/bscSrch?&q.srchNm=" + keyword
#For Mac - If you use windows change the chromedriver location
chrome_path = '/usr/local/bin/chromedriver'

driver = webdriver.Chrome(chrome_path)



def searchKeyword(url):
    # use the session to get the data

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--disable-popup-blocking")

    driver.maximize_window()

    start_time = time.monotonic()

    FIRST_TIME_CSV = False #True if its the first time this csv file is being written to
    break_out_of_loop = False
    while True:
        page = 1 #Start at first page and iterate over the next pages
        newUrl = url + "&dsrdPg=" + str(page)
        try:
            driver.get(newUrl)
            soup = bs.BeautifulSoup(driver.page_source, 'html.parser')
            charitiesURL = returnCharitiesURL(soup)
            for url in charitiesURL:
                scrapeCharity("https://apps.cra-arc.gc.ca" + url, FIRST_TIME_CSV=FIRST_TIME_CSV)
                FIRST_TIME_CSV = False

            page += 1

        except Exception as e:
            page += 1
            print(e)
            print("got all charities, last page is", page)
            if page > 3:
                break_out_of_loop = True


def returnCharitiesURL(soup):
    '''
    Scrapes fromthe canadian government website
    :param soup: beautifulsoup object
    :return: list of url substrings for the links to charities
    '''
    urls = []
    td = soup.find_all('td', {"headers": "headername"})
    for element in td:
        urls.append(element.findChild()['href'])

    return urls

def scrapeCharity(url, FIRST_TIME_CSV=False):
    '''
    scrape a particular charity
    :param url: string
    :return:
    '''
    driver.get(url)
    soup = bs.BeautifulSoup(driver.page_source, 'html.parser')

    registration_number = "".join(soup.find_all('strong')[0].text.replace("\n", "").strip().split())
    charity_name = soup.find_all('h1')[0].text.replace("\n", "").strip()[:-13]
    if charity_name == "":
        charity_name = soup.find_all('h2', {'class': 'h3'})[0].text.replace("\n", "").strip()

    print(charity_name)
    if charity_name in existing:
        print("Already in CSV")
        return
    # selectedFilingPeriodIndex=0 --> most recent filing period, aka 2020
    # q.stts=0007 --> Only search for registered charity status pages
    full_view_url = "https://apps.cra-arc.gc.ca/ebci/hacc/srch/pub/dsplyT3010FrFlngPrd?selectedFilingPeriodIndex=0&q.stts=0007&selectedCharityBn=" + registration_number

    driver.get(full_view_url)

    soup = bs.BeautifulSoup(driver.page_source, 'html.parser') #2020 full_view page

    dict = {} #The dictionary that is going to be used to write the row

    divs = soup.find_all("div", {"class": "container-fluid"})
    for div in divs:
        try:
            number_child = div.findChildren("div", {'class': "pull-left"})
            number = number_child[0].text.strip()[-4:]

            value_child = div.findChildren("div", { 'class': "text-bold mrgn-bttm-md"})
            value = value_child[0].text.strip()

            dict[number] = value

        except:
            pass
    with open('cadets.csv', 'a', encoding="utf8") as csvfile:
        fieldnames = ['1510: Was the charity in a subordinate position to a head body?',
                      '1570: Has the charity wound-up, dissolved, or terminated operations?',
                      '1600: Is the charity designated as a public foundation or private foundation?',
                      '1800: Was the charity active during the fiscal period?',
                      '2000: Did the charity make gifts or transfer funds to qualified donees or other organizations?',
                      '2100: Did the charity carry on, fund, or provide any resources through employees, volunteers, agents, joint ventures, contractors, or any other individuals, intermediaries, entities, or means (other than qualified donees) for any activity/program/project outside Canada?',
                      '2400: Did the charity carry on any public policy dialogue and development activities during the fiscal period?',
                      '2660: Types of fundraising methods (SPECIFY)',
                      '2700: Did the charity pay external fundraisers?',
                      '2770: Did the charity pay external fundraisers?',
                      "3200: Did the charity compensate any of its directors/trustees or like officials or persons not at arm's length from the charity for services provided during the fiscal period (other than reimbursement for expenses)?",
                      '3400: Did the charity incur any expenses for compensation of employees during the fiscal period?',
                      "3900: Did the charity receive any donations or gifts of any kind valued at $10,000 or more from any donor that was NOT resident in Canada and was NOT any of the following: a Canadian citizen, nor employed in Canada, nor carrying on a business in Canada, nor a person having disposed of taxable Canadian property?",
                      "4000: Did the charity receive any non-cash gifts for which it issued tax receipts?",
                      "4020: Was the financial information reported below prepared on an accrual or cash basis?",
                      "4050: Did the charity own land and/or buildings?",
                      '4100: Cash, bank accounts, and short-term investments',
                      "4110: Amounts receivable from non-arm's length persons",
                      "4120: Amounts receivable from all others",
                      "4130: Investments in non-arm's length persons",
                      "4140: Long-term investments",
                      "4150: Inventories",
                      "4155: Land and buildings in Canada",
                      "4160: Other capital assets in Canada",
                      "4165: Capital assets outside Canada",
                      "4166: Accumulated amortization of capital assets (enter negative amount)",
                      "4170: Other assets",
                      "4180: 10 year gifts",
                      "4200: Total assets (add lines 4100 to 4170)",
                      "4250: Amount included in lines 4150, 4155, 4160, 4165 and 4170 not used in charitable activities",
                      "4300: Accounts payable and accrued liabilities",
                      "4310: Deferred revenue",
                      "4320: Amounts owing to non-arm's length persons",
                      "4330: Other liabilities",
                      "4350: Total liabilities (add lines 4300 to 4330)",
                      "4400: Did the charity borrow from, loan to, or invest assets with any non-arm's length persons?",
                      "4490: Did the charity issue tax receipts for gifts?",
                      "4500: Total eligible amount of all gifts for which the charity issued tax receipts",
                      "4505: Total amount of 10 year gifts received",
                      "4510: Total amount received from other registered charities",
                      "4530: Total other gifts received for which a tax receipt was NOT issued by the charity (excluding amounts at lines 4575 and 4630)",
                      "4565: Did the charity receive any revenue from any level of government in Canada?",
                      "4570: Total amount received",
                      "4571: Total tax-receipted revenue from all sources outside of Canada (government and non-government)",
                      "4575: Total NON tax-receipted revenue from all sources outside of Canada (government and non-government)",
                      "4630: Total NON tax-receipted revenue from fundraising",
                      "4640: Total revenue from sale of goods and services (except to any level of government in Canada)",
                      "4650: Other revenue not already included in the amounts above",
                      "4700: Total revenue (add lines 4500, 4510 to 4570, and 4575 to 4650)",
                      "5610: Total eligible amount of tax-receipted tuition fees",
                      "4505: Total amount of 10 year gifts received",
                      "4510: Total amount received from other registered charities",
                      "4530: Total other gifts received for which a tax receipt was not issued by the charity (excluding amounts at lines 4575 and 4630)",
                      "4540: Total revenue received from federal government",
                      "4550: Total revenue received from provincial/territorial governments",
                      "4560: Total revenue received from municipal/regional governments",
                      "4571: Total tax-receipted revenue from all sources outside of Canada (government and non-government)",
                      "4575: Total non tax-receipted revenue from all sources outside Canada (government and non-government)",
                      "4585: Total interest and investment income received or earned",
                      "4590: Gross proceeds from disposition of assets",
                      "4600: Net proceeds from disposition of assets (show a negative amount with minus sign)",
                      "4610: Gross income received from rental of land and/or buildings",
                      "4620: Total non tax-receipted revenues received for memberships, dues and association fees",
                      "4630: Total non tax-receipted revenue from fundraising",
                      "4640: Total revenue from sale of goods and services (except to any level of government in Canada)",
                      "4650: Other revenue not already included in the amounts above",
                      "4655: Specify type(s) of revenue included in the amount reported at 4650",
                      "4700: Total revenue (add lines 4500, 4510 to 4560, 4575, 4580, and 4600 to 4650)",
                      "4800: Advertising and promotion",
                      "4810: Travel and vehicle expenses",
                      "4820: Interest and bank charges",
                      "4830: Licences, memberships, and dues",
                      "4840: Office supplies and expenses",
                      "4850: Occupancy costs",
                      "4860: Professional and consulting fees",
                      "4870: Education and training for staff and volunteers",
                      "4880: Total expenditure on all compensation (enter the amount reported at line 390 in Schedule 3, if applicable)",
                      "4890: Fair market value of all donated goods used in charitable activities",
                      "4891: Purchased supplies and assets",
                      "4900: Amortization of capitalized assets",
                      "4910: Research grants and scholarships as part of charitable activities",
                      "4920: All other expenditures not included in the amounts above (excluding gifts to qualified donees)",
                      "4930: Specify type(s) of expenditures included in the amount reported at 4920",
                      "4950: Total expenditures before gifts to qualified donees (add lines 4800 to 4920)",
                      "5000: (a) Total expenditures on charitable activities",
                      "5010: (b) Total expenditures on management and administration",
                      "5020: (c) Total expenditures on fundraising",
                      "5040: (d) Total other expenditures included in line 4950",
                      "5050: Total amount of gifts made to all qualified donees",
                      "5100: Total expenditures (add lines 4950 and 5050)",
                      "5500: Enter the amount accumulated for the fiscal period, including income earned on accumulated funds",
                      "5510: Enter the amount disbursed for the fiscal period for the specified purpose",
                      "5750: If the charity has received approval to make a reduction to its disbursement quota, enter the amount for the fiscal period",
                      "5800: Did the charity acquire a non-qualifying security?",
                      "5810: Did the charity allow any of its donors to use any of its property? (except for permissible uses)",
                      "5820: Did the charity issue any of its tax receipts for donations on behalf of another organization?",
                      "5830: Did the charity have direct partnership holdings at any time during the fiscal period?",
                      "5900: Enter the average value of property not used for charitable activities or administration during the 24 months before the BEGINNING of the fiscal period"
                      "5910: Enter the average value of property not used for charitable activities or administration during the 24 months before the END of the fiscal period",
                      ]

        fieldnames_short = [field[:4] for field in fieldnames]
        fieldnames_short.insert(0, "URL")
        fieldnames_short.insert(0, "Registration Number")
        fieldnames_short.insert(0, "Charity Name")

        dict["Charity Name"] = charity_name
        dict["URL"] = url
        dict["Registration Number"] = registration_number
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames_short)

        try:
            driver.find_element_by_xpath("//a[contains(., 'Schedule 6 - Detailed financial information')]").click()
            soup = bs.BeautifulSoup(driver.page_source, 'html.parser')  # 2020 full_view page

            divs = soup.find_all("div", {"class": "container-fluid"})
            for div in divs:
                try:
                    number_child = div.findChildren("div", {'class': "pull-left"})
                    number = number_child[0].text.strip()[-4:]

                    value_child = div.findChildren("div", {'class': "text-bold mrgn-bttm-md"})
                    value = value_child[0].text.strip()

                    dict[number] = value
                except Exception as e:
                    pass
        except:  # If there is an error returned, it means the page doesn't have Schedule 6 - Detailed financial information. We get the financial information directly from that page, under Schedule D
            # print("No Schedule 6 - Detailed Financial Information page")
            pass

        if FIRST_TIME_CSV:
            writer.writeheader()

        writer.writerow(dict)



    return url


if __name__ == '__main__':
    searchKeyword(url)