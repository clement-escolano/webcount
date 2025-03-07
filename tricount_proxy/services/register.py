import uuid

import requests
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from django.conf import settings


def get_rsa_public_key() -> str:
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return public_key_pem.decode()


def register_user() -> tuple[uuid.UUID, str, int]:
    rsa_public_key = get_rsa_public_key()
    app_installation_uuid = uuid.uuid4()
    response = requests.post(
        settings.TRICOUNT_API + "/v1/session-registry-installation",
        headers={
            "User-Agent": settings.TRICOUNT_USER_AGENT,
            "app-id": str(app_installation_uuid),
            "X-Bunq-Client-Request-Id": str(uuid.uuid4()),
        },
        json={
            "app_installation_uuid": str(app_installation_uuid),
            "client_public_key": rsa_public_key,
            "device_description": "Android",
        },
        timeout=5,
    )
    response.raise_for_status()
    json = response.json()
    return (
        app_installation_uuid,
        json["Response"][1]["Token"]["token"],
        json["Response"][3]["UserPerson"]["id"],
    )
