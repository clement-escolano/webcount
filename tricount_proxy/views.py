from urllib.parse import urlparse

from django.conf import settings
from django import forms
from django.urls import resolve, Resolver404
from django.utils.translation import gettext_lazy as _
from django.shortcuts import render, redirect

from tricount_proxy.services.context import parse_expense, parse_refund, parse_balance
from tricount_proxy.services.register import register_user
from tricount_proxy.services.tricount_api import lookup


class TricountLinkForm(forms.Form):
    url = forms.URLField()

    def clean_url(self):
        url = self.cleaned_data["url"]
        required_domain = "tricount.com"
        parsed_url = urlparse(url)
        if parsed_url.netloc != required_domain:
            raise forms.ValidationError(
                _("The link must start with %(required_prefix)s")
                % {"required_prefix": "https://" + required_domain}
            )
        try:
            match = resolve(parsed_url.path)
        except Resolver404:
            raise forms.ValidationError(_("This Tricount link is not valid.")) from None
        if match.view_name != "tricount_details":
            raise forms.ValidationError(_("This Tricount link is not valid."))
        self.cleaned_data["tricount_id"] = match.kwargs.get("tricount_id")
        return url


def home(request):
    errors: list[str] = []
    if request.method == "POST":
        form = TricountLinkForm(request.POST)
        if form.is_valid():
            tricount_id = form.cleaned_data["tricount_id"]
            return redirect(
                "tricount_details",
                tricount_id=tricount_id,
                permanent=False,
            )
        else:
            errors = form.errors.get_json_data()["url"]
    return render(
        request, "home.html", {"host": settings.SITE_DOMAIN, "errors": errors}
    )


def tricount_details(request, tricount_id: str):
    if "app_installation_uuid" not in request.session:
        (app_installation_uuid, token, user_id) = register_user()
        request.session["user_id"] = user_id
        request.session["app_installation_uuid"] = str(app_installation_uuid)
        request.session["token"] = str(token)
    registry = lookup(tricount_id, request.session)["Response"][0]["Registry"]

    memberships = {
        m["RegistryMembershipNonUser"]["uuid"]: m["RegistryMembershipNonUser"]["alias"][
            "display_name"
        ]
        for m in registry["memberships"]
        if m["RegistryMembershipNonUser"]["status"] == "ACTIVE"
    }
    balance = parse_balance(registry["all_registry_entry"], memberships)

    return render(
        request,
        "tricount_detail.html",
        {
            "title": registry["title"],
            "memberships": memberships.values(),
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
            "balance": balance,
        },
    )
