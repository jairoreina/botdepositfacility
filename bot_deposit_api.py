import csv
import json
import requests
import datetime
import pandas as pd

api = "https://app.bot.or.th/finmarket/api/fmo"

#gets the current date, and if a weekend, then last friday.
def get_last_weekday():
    current_date = datetime.date.today()

    if current_date.weekday() >= 5:  
        friday = current_date
        while friday.weekday() != 4: 
            friday -= datetime.timedelta(days=1)
        return friday.strftime("%Y-%m-%d")
    else:
        return current_date.strftime("%Y-%m-%d")

#gets previous date and if monday, then last friday
def get_prev_day():
    prev_date = datetime.date.today() - datetime.timedelta(days=1)
    if prev_date.weekday() >= 5:  
        friday = prev_date
        while friday.weekday() != 4: 
            friday -= datetime.timedelta(days=1)
        return friday.strftime("%Y-%m-%d")
    else:
        return prev_date.strftime("%Y-%m-%d")

#sends the api reuqest with necessary headers to work
def send_request(date):
    headers = {
        "authority" : "app.bot.or.th", 
        "accept" : "*/*",  
        "accept-language" : "en-US, en; q=0.9", 
        "origin" : "https://app.bot.or.th",
        "sec-fetch-dest" : "empty",
        "sec-fetch-mode" : "cors",
        "sec-fetch-site" : "same-origin",
        "user-agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67"
    }
    data = {"type": "/deposit-facility",
            "startDate": date,
            "endDate": date}

    response = requests.post(api, headers=headers, data=data)
    resp_content = response.content
    decoded_output = resp_content.decode('utf-8')
    return json.loads(decoded_output)

def json_to_csv():
    result = json_data['responseResults'][0]
    settlement_date = pd.to_datetime(result['settlementDate']).strftime("%d %b %Y")
    maturity_date = pd.to_datetime(result['maturityDate']).strftime("%d %b %Y")
    tenor = result['productTerm']
    allocated_amount = result['allocatedAmount']
    rate_accepted = format(result['weightAverageRate'], ".3f")

    table_headers = ["Settlement Date", "Maturity Date", "Tenor", "Deposit Amount (Mil.Baht)", "Rate Accepted(%)"]
    data_row_list = [settlement_date, maturity_date, tenor, allocated_amount, rate_accepted]

    with open("bot_deposit_facility.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(table_headers)
        writer.writerow(data_row_list)

    print("CSV Downloaded!")

json_data = send_request(get_last_weekday())

#checks if the request returned a blank list, which means data isnt out yet.
#if so, it gets the data from the previous day and if monday from last friday
try:
    if json_data["responseResults"] == []:
        json_data = send_request(get_prev_day())
        json_to_csv()
    else:
        json_to_csv()
except:
    print("API Request Error. Compare headers in python script with headers in browser DevTools.")