import uuid
from datetime import date, datetime
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


def mark_registry_as_active_if_necessary(
    session: SessionDict,
    registry: dict,
    owner_uuid: str,
    owner_display_name: str,
):
    if session.get("marked_as_active"):
        return
    session["marked_as_active"] = True
    response = requests.post(
        settings.TRICOUNT_API
        + f"/v1/user/{session['user_id']}/registry-synchronization",
        headers={
            "User-Agent": settings.TRICOUNT_USER_AGENT,
            "app-id": session["app_installation_uuid"],
            "X-Bunq-Client-Authentication": session["token"],
            "X-Bunq-Client-Request-Id": str(uuid.uuid4()),
        },
        json={
            "all_registry_active": [
                {
                    "membership_name": owner_display_name,
                    "membership_uuid": owner_uuid,
                    "public_identifier_token": registry["public_identifier_token"],
                }
            ],
            "all_registry_archived": [],
            "all_registry_deleted": [],
        },
        timeout=5,
    )
    response.raise_for_status()


def add_expense(
    session: SessionDict,
    registry: dict,
    description: str,
    amount: float,
    owner: tuple[str, str],
    date_: date,
    allocations: list[tuple[str, float]],
) -> dict:
    owner_uuid, owner_display_name = owner
    mark_registry_as_active_if_necessary(
        session, registry, owner_uuid, owner_display_name
    )
    response = requests.post(
        settings.TRICOUNT_API
        + f"/v1/user/{session['user_id']}/registry/{registry['id']}/registry-entry",
        headers={
            "User-Agent": settings.TRICOUNT_USER_AGENT,
            "app-id": session["app_installation_uuid"],
            "X-Bunq-Client-Authentication": session["token"],
            "X-Bunq-Client-Request-Id": str(uuid.uuid4()),
        },
        json={
            "attachment": [],
            "date": datetime.combine(date_, datetime.min.time()).strftime(
                "%Y-%m-%d %H:%M:%S.%f"
            ),
            "description": description,
            "exchange_rate": str(1.0),
            "membership_uuid_owner": owner_uuid,
            "type_transaction": "NORMAL",
            "uuid": str(uuid.uuid4()),
            "amount": {
                "currency": registry["currency"],
                "value": str(-1 * amount),
            },
            "amount_local": {
                "currency": registry["currency"],
                "value": str(-1 * amount),
            },
            "allocations": [
                {
                    "membership_uuid": membership_uuid,
                    "share_ratio": ratio,
                    "type": "RATIO",
                }
                for (membership_uuid, ratio) in allocations
            ],
        },
        timeout=5,
    )
    response.raise_for_status()
    return response.json()
