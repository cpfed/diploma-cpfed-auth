import requests


class ContestResult:
    def __init__(self, data: dict):
        self.user = data["user"]
        self.score = data["score"]
        self.cumulative_time = data["cumulative_time"]
        self.tiebreaker = data["tiebreaker"]
        self.rank = -1

    def same_place(self, other):
        return self.score == other.score and \
            self.cumulative_time == other.cumulative_time and \
            self.tiebreaker == other.tiebreaker


def fetch_contest_results(link: str):
    response = requests.get(link)
    response.raise_for_status()
    res = sorted((ContestResult(x) for x in response.json()["data"]["object"]["rankings"]),
                 key=lambda x: (-x.score, x.cumulative_time, x.tiebreaker))
    if len(res):
        res[0].rank = 1
    for i in range(1, len(res)):
        if res[i].same_place(res[i-1]):
            res[i].rank = res[i-1].rank
        else:
            res[i].rank = i+1
    return res
