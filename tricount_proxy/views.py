from django.shortcuts import render

from tricount_proxy.services.context import parse_expense, parse_refund
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
                parse_expense(e)
                if e["RegistryEntry"]["type_transaction"] == "NORMAL"
                else parse_refund(e)
                for e in sorted(
                    registry["all_registry_entry"],
                    key=lambda e: e["RegistryEntry"]["date"],
                    reverse=True,
                )

            ],
        },
    )
