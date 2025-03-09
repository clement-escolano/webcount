from datetime import datetime

from django.shortcuts import render

from tricount_proxy.services.register import register_user
from tricount_proxy.services.tricount_api import lookup


def tricount_details(request, tricount_id: str):
    if "app_installation_uuid" not in request.session:
        (app_installation_uuid, token, user_id) = register_user()
        request.session["user_id"] = user_id
        request.session["app_installation_uuid"] = str(app_installation_uuid)
        request.session["token"] = str(token)
    registry = lookup(tricount_id, request.session)["Response"][0]["Registry"]

    return render(
        request,
        "tricount_detail.html",
        {
            "title": registry["title"],
            "memberships": [
                m["RegistryMembershipNonUser"]["alias"]["display_name"]
                for m in registry["memberships"]
                if m["RegistryMembershipNonUser"]["status"] == "ACTIVE"
            ],
            "currency": registry["currency"],
            "expenses": [
                {
                    "amount": float(e["RegistryEntry"]["amount"]["value"]) * -1,
                    "description": e["RegistryEntry"]["description"],
                    "date": datetime.strptime(
                        e["RegistryEntry"]["date"], "%Y-%m-%d %H:%M:%S.%f"
                    ),
                    "owner": e["RegistryEntry"]["membership_owned"][
                        "RegistryMembershipNonUser"
                    ]["alias"]["display_name"],
                    "allocations": [
                        {
                            "ratio": a.get("share_ratio"),
                            "amount": float(a["amount"]["value"]) * -1,
                            "name": a["membership"]["RegistryMembershipNonUser"][
                                "alias"
                            ]["display_name"],
                        }
                        for a in e["RegistryEntry"]["allocations"]
                    ],
                    "allocations_have_ratio": any(
                        "share_ratio" in a for a in e["RegistryEntry"]["allocations"]
                    ),
                }
                for e in sorted(
                    registry["all_registry_entry"],
                    key=lambda e: e["RegistryEntry"]["date"],
                    reverse=True,
                )
                if e["RegistryEntry"]["type_transaction"] == "NORMAL"
            ],
        },
    )
