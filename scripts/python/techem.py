import sys
import requests
import datetime
import json

# Get date (YYYY-MM-DD) n days ago
def get_date_as_string(n: int) -> str:
    today = datetime.datetime.now()
    date = today - datetime.timedelta(days=n)

    return f"{date.year}-{date.month:02d}-{date.day:02d}"

# Get date (YYYY-MM-DD) of first day of year
def get_first_date_as_string() -> str:
    first_day = datetime.datetime(datetime.datetime.now().year, 1, 1)

    return f"{first_day.year}-{first_day.month:02d}-{first_day.day:02d}"

# Request token
def get_token(techem_email: str, techem_password: str) -> str:
    url = "https://techemadmin.no/analytics/graphql"

    token_body = {
        "query": """
            mutation nucleolusLogin($credentials: CredentialsInput!) {
                loginWithEmailAndPassword(credentials: $credentials) {
                    ok {
                        token
                    }
                }
            }
        """,
        "variables": {
            "credentials": {
                "username": techem_email,
                "password": techem_password,
                "targetResource": "tenant"
            }
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

        return response.json()["data"]["loginWithEmailAndPassword"]["ok"]["token"]
    
    except requests.exceptions.RequestException:
        return ""
    except KeyError:
        return ""

def get_data(techem_email: str, techem_password: str, object_id: int, yearly: bool, days_offset: int) -> str:
    token = get_token(techem_email, techem_password)

    if not token:
        return ""

    if yearly:
        # Get data from entire current year
        start_time = get_first_date_as_string()
        end_time = get_date_as_string(days_offset)

        # Compare with previous year
        compare_period = "previous-year"
    else:
        # Get data from previous seven days
        start_time = get_date_as_string(days_offset + 7)
        end_time = get_date_as_string(days_offset)

        # Compare with previous seven days
        compare_period = "previous-period"

    url = "https://techemadmin.no/analytics/graphql"

    body = {
        "query": """
            query TenantTable($table: TenantTableInput!) {
                tenantTable(table: $table) {
                    rows {
                        values
                        comparisonValues
                    }
                }
            }
        """,
        "variables": {
            "table": {
                "aggregationLevel": "UNIT",
                "objectId": str(object_id),
                "periodBegin": f"{start_time}T00:00:00",
                "periodEnd": f"{end_time}T00:00:00",
                "compareWith": compare_period
            }
        },
        "operationName": "TenantTable"
    }

    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Origin": "https://beboer.techemadmin.no",
        "Referer": "https://beboer.techemadmin.no/",
        "Authorization": f"JWT {token}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=body,
            timeout=10.0
        )
        response.raise_for_status()

        data = response.json()["data"]["tenantTable"]["rows"][0]
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

    offset = 1

    result = get_data(email, password, id, yearly, offset)

    if result:
        print(result)

if __name__ == "__main__":
    main()