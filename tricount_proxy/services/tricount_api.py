import uuid
from typing import TypedDict

import requests
from django.conf import settings


class SessionDict(TypedDict):
    user_id: int
    app_installation_uuid: str
    token: str


def get_registry(session: SessionDict, tricount_public_identifier: str) -> dict:
    response = requests.get(
        settings.TRICOUNT_API
        + f"/v1/user/{session['user_id']}/registry?public_identifier_token={tricount_public_identifier}",
        headers={
            "User-Agent": settings.TRICOUNT_USER_AGENT,
            "app-id": session["app_installation_uuid"],
            "X-Bunq-Client-Authentication": session["token"],
            "X-Bunq-Client-Request-Id": str(uuid.uuid4()),
        },
        timeout=5,
    )
    response.raise_for_status()
    return response.json()["Response"][0]["Registry"]
