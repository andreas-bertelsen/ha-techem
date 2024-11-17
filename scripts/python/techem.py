import sys
import requests
import datetime
import json

# Get date (YYYY-MM-DDThh:mm:ss.000Z) n days ago
def get_time_as_string(n: int) -> str:
    today = datetime.datetime.now()
    date = today - datetime.timedelta(days=n)

    return f"{date.year}-{date.month:02d}-{date.day:02d}"

# Get date (YYYY-MM-DDThh:mm:ss.000Z) as tuple with first day of year and yesterday
def get_time_as_string_year() -> tuple[str, str]:
    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(1)
    stop = f"{yesterday.year}-{yesterday.month:02d}-{yesterday.day:02d}"

    first_day = datetime.datetime(today.year, 1, 1)
    start = f"{first_day.year}-{first_day.month:02d}-{first_day.day:02d}"

    return start, stop

# Request token
def get_token(techem_email: str, techem_password: str) -> str:
    url = "https://techemadmin.no/graphql"

    token_body = {
        "query": """
            mutation tokenAuth($email: String!, $password: String!) {
                tokenAuth(email: $email, password: $password) {
                    payload
                    refreshExpiresIn
                    token
                    refreshToken
                }
            }
        """,
        "variables": {
            "email": techem_email,
            "password": techem_password
        }
    }
    
    token_headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://beboer.techemadmin.no/",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            url,
            headers=token_headers,
            json=token_body,
            timeout=10.0
        )
        response.raise_for_status()

        return response.json()["data"]["tokenAuth"]["token"]
    
    except requests.exceptions.RequestException:
        return ""
    except KeyError:
        return ""

def get_data(techem_email: str, techem_password: str, tenant_id: int, yearly: bool) -> str:
    token = get_token(techem_email, techem_password)

    if not token:
        return ""

    if yearly:
        # Get data from first day of year to yesterday
        start_time, end_time = get_time_as_string_year()
    else:
        # Get data from previous seven days, with 2 days offset to ensure data is available
        start_time = get_time_as_string(9)
        end_time = get_time_as_string(2)

    url = "https://techemadmin.no/graphql"

    body = {
        "query": """
            query DashboardData($tenancyId: Int!, $periodBegin: String, $periodEnd: String, $compareWith: String!) {
                dashboard(tenancyId: $tenancyId, periodBegin: $periodBegin, periodEnd: $periodEnd, compareWith: $compareWith) {
                    consumptions {
                        value
                        comparisonValue
                        kind
                        comparePercent
                    }
                    climateAverages {
                        value
                        valueCompare
                        kind
                    }
                }
            }
        """,
        "variables": {
            "tenancyId": tenant_id,
            "periodBegin": start_time,
            "periodEnd": end_time,
            "compareWith": "last_period"
        },
        "operationName": "DashboardData"
    }

    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Origin": "https://beboer.techemadmin.no/",
        "Referer": "https://beboer.techemadmin.no/",
        "Authorization": f"JWT {token}",
        "Content-Type": "application/json",
        "Connection" : "keep-alive"
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=body,
            timeout=10.0
        )
        response.raise_for_status()

        data = response.json()["data"]["dashboard"]["consumptions"]
        return json.dumps(data)
    
    except requests.exceptions.RequestException:
        return ""
    except KeyError:
        return ""

def main() -> None:
    email = sys.argv[1]
    password = sys.argv[2]
    id = int(sys.argv[3])
    yearly = sys.argv[4] == "True"

    result = get_data(email, password, id, yearly)

    if result:
        print(result)

if __name__ == "__main__":
    main()