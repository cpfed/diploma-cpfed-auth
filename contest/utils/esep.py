import requests, json

from django.conf import settings

from contest.models import UserContest, Contest


def reg_users_to_esep_organization(contest: Contest, user_email=None):
    if contest.esep_org is None:
        return
    user_emails = [user_email]
    if user_email is None:
        user_emails = list(UserContest.objects.filter(contest=contest).values_list("user__email", flat=True))
    resp = requests.post(url=f"https://esep.cpfed.kz/api/add_users_to_org/{settings.CPFED_TOKEN}/",
                         data=json.dumps({
                             "org_id": contest.esep_org,
                             "emails": user_emails
                         }))

    try:
        resp.raise_for_status()
    except Exception as e:
        return str(e)
    if resp.status_code != 201:
        return resp.json().get('detail')
