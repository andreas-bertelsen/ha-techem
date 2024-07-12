import sys
import requests
import datetime
import json

# Get date (YYYY-MM-DDThh:mm:ss.000Z) n days ago
def get_time_as_string(n: int):
    today = datetime.datetime.now()
    date = today - datetime.timedelta(days=n)

    return f"{date.year}-{date.month:02d}-{date.day:02d}T{date.hour:02d}:{date.minute:02d}:{date.second:02d}.000Z"

# Get date (YYYY-MM-DDThh:mm:ss.000Z) as tuple with first day of year and yesterday
def get_time_as_string_year():
    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(1)
    stop = f"{yesterday.year}-{yesterday.month:02d}-{yesterday.day:02d}T{yesterday.hour:02d}:{yesterday.minute:02d}:{yesterday.second:02d}.000Z"

    firstDay = datetime.datetime(today.year, 1, 1)
    start = f"{firstDay.year}-{firstDay.month:02d}-{firstDay.day:02d}T{firstDay.hour:02d}:{firstDay.minute:02d}:{firstDay.second:02d}.000Z"

    return start, stop

# Request token
def get_token(techemEmail: str, techemPassword: str):
    token_body = "{\"query\":\"mutation tokenAuth($email: String!, $password: String!) { tokenAuth(email: $email, password: $password) { payload refreshExpiresIn token refreshToken } }\",\"variables\":{\"email\":\"" + techemEmail + "\",\"password\":\"" + techemPassword + "\"}}"
    
    token_headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://beboer.techemadmin.no/",
        "Content-Type": "application/json"
    }

    return requests.post("https://techemadmin.no/graphql", headers=token_headers, data=token_body, timeout=10.0).json()["data"]["tokenAuth"]["token"]

def get_data(tenantID: int, yearly: bool):
    token = get_token(sys.argv[1], sys.argv[2])

    starttime, endtime = "", ""

    if yearly:
        # Get data from first day of year to yesterday
        starttime, endtime = get_time_as_string_year()
    else:
        # Get data from previous seven days, with 2 days offset to ensure data is available
        starttime = get_time_as_string(9)
        endtime = get_time_as_string(2)

    body = "{\"operationName\":\"getDashboardPage\",\"variables\":{\"tenancyId\":" + str(tenantID) + ",\"periodBegin\":\"" + starttime + "\",\"periodEnd\":\"" + endtime + "\",\"compareWith\":\"last_year\"},\"query\":\"query getDashboardPage($tenancyId: Int!, $periodBegin: String, $periodEnd: String, $compareWith: String!) {\\n  dashboard(\\n   tenancyId: $tenancyId\\n    periodBegin: $periodBegin\\n    periodEnd: $periodEnd\\n    compareWith: $compareWith\\n  ) {\\n    consumptions {\\n      value\\n      kind\\n      comparePercent\\n      __typename\\n    }\\n    climateAverages {\\n      value\\n      valueCompare\\n      kind\\n      __typename\\n    }\\n    __typename\\n  }\\n}\"}"
    
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Origin": "https://beboer.techemadmin.no/",
        "Referer": "https://beboer.techemadmin.no/",
        "Authorization": f"JWT {token}",
        "Content-Type": "application/json",
        "Connection" : "keep-alive"
    }

    response = requests.post("https://techemadmin.no/graphql", headers=headers, data=body, timeout=10.0).json()["data"]["dashboard"]["consumptions"]
    
    for entry in response:
        del entry["__typename"]

    return json.dumps(response)

print(get_data(int(sys.argv[3]), sys.argv[4] == "True"))