import requests

from src.schemas.hot_issues import HotIssuesResponseModel
from src.schemas.response import RequestResponse


def fetch_active_issues() -> RequestResponse:
    url = "https://kbf.lesta.ru/api/v2/hot_issues/"

    querystring = {
        "include": "translations",
        "filter\\[system_tags\\]": "wotb",
        "filter\\[translations.lang\\]": "ru",
        "filter\\[status\\]": "active",
        "sort": "-published",
        "filter[system_tags]": "wotb",
        "filter[translations.lang]": "ru",
        "filter[status]": "active"
    }

    headers = {
        "authority": "kbf.lesta.ru",
        "accept": "application/json, text/plain, */*",
        "accept-language": "ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7",
        "origin": "https://lesta.ru",
        "referer": "https://lesta.ru/",
        "sec-ch-ua": "'Microsoft Edge';v='119', 'Chromium';v='119', 'Not?A_Brand';v='24'",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "'Windows'",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0"
    }

    response: requests.Response = requests.get(url, headers=headers, params=querystring)
    response_status = response.status_code
    content = HotIssuesResponseModel.parse_obj(response.json()) if response_status == 200 else None
    return RequestResponse(status_code=response_status, content=content)
