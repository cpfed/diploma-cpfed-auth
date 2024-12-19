import time
from hashlib import sha256

from django.conf import settings
from django.utils import timezone

from facebook_business.adobjects.serverside.event import Event
from facebook_business.adobjects.serverside.event_request import EventRequest
from facebook_business.adobjects.serverside.user_data import UserData
from facebook_business.adobjects.serverside.action_source import ActionSource
from facebook_business.api import FacebookAdsApi

if not settings.DEBUG:
    FacebookAdsApi.init(access_token=settings.META_PIXEL_ACCESS_TOKEN)


def send_registration(email: str):
    if settings.DEBUG:
        return
    try:
        events = [Event(
            event_name="Lead",
            event_time=int(timezone.now().timestamp()),
            user_data=UserData(
                emails=[sha256(email.encode(encoding="utf-8")).hexdigest()]
            ),
            action_source=ActionSource.WEBSITE
        )]
        event_request = EventRequest(
            events=events,
            pixel_id=settings.META_PIXEL_ID
        )
        event_response = event_request.execute()
        print(event_response)
    except Exception as e:
        print("ERROR Meta Pixel: ", str(e))
