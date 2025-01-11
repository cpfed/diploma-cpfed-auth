import requests


class ContestResult:
    def __init__(self, data: dict):
        self.user = data["user"]
        self.score = data["score"]
        self.cumulative_time = data["cumulative_time"]
        self.tiebreaker = data["tiebreaker"]


def fetch_contest_results(link: str):
    response = requests.get(link)
    response.raise_for_status()
    res = sorted((ContestResult(x) for x in response.json()["data"]["object"]["rankings"]),
                 key=lambda x: (-x.score, x.cumulative_time, x.tiebreaker))
    return res
