import datetime
from urllib.parse import urlparse

from django.conf import settings
from django import forms
from django.urls import resolve, Resolver404
from django.utils.translation import gettext_lazy as _
from django.shortcuts import render, redirect

from tricount_proxy.services.context import parse_expense, parse_refund, parse_balance
from tricount_proxy.services.register import register_user
from tricount_proxy.services.tricount_api import get_registry, add_expense
from tricount_proxy.templatetags.money import currencies


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
        self.cleaned_data["tricount_public_identifier"] = match.kwargs.get(
            "tricount_public_identifier"
        )
        return url


def home(request):
    errors: list[str] = []
    if request.method == "POST":
        form = TricountLinkForm(request.POST)
        if form.is_valid():
            tricount_public_identifier = form.cleaned_data["tricount_public_identifier"]
            return redirect(
                "tricount_details",
                tricount_public_identifier=tricount_public_identifier,
                permanent=False,
            )
        else:
            errors = form.errors.get_json_data()["url"]
    return render(
        request, "home.html", {"host": settings.SITE_DOMAIN, "errors": errors}
    )


def tricount_details(request, tricount_public_identifier: str):
    if (
        "app_installation_uuid" not in request.session
        or request.session.get("tricount_public_identifier")
        != tricount_public_identifier
    ):
        (app_installation_uuid, token, user_id) = register_user()
        request.session["user_id"] = user_id
        request.session["app_installation_uuid"] = str(app_installation_uuid)
        request.session["token"] = str(token)
        request.session["tricount_public_identifier"] = tricount_public_identifier
    registry = get_registry(request.session, tricount_public_identifier)

    memberships = {
        m["RegistryMembershipNonUser"]["uuid"]: m["RegistryMembershipNonUser"]["alias"][
            "display_name"
        ]
        for m in registry["memberships"]
        if m["RegistryMembershipNonUser"]["status"] == "ACTIVE"
    }

    class NewExpenseForm(forms.Form):
        description = forms.CharField(label=_("Title"))
        amount = forms.FloatField(
            step_size=0.01,
            max_value=1e6,
            min_value=0,
            label=_("Amount (%(currency)s)")
            % {"currency": currencies.get(registry["currency"], registry["currency"])},
        )
        date = forms.DateField(
            label=_("Date"),
            initial=lambda: datetime.date.today().strftime("%Y-%m-%d"),
            widget=forms.DateInput(attrs={"type": "date"}),
        )
        owner = forms.ChoiceField(label=_("Paid by"), choices=memberships.items())

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for m in registry["memberships"]:
                if m["RegistryMembershipNonUser"]["status"] == "ACTIVE":
                    self.fields[m["RegistryMembershipNonUser"]["uuid"]] = (
                        forms.IntegerField(
                            label=m["RegistryMembershipNonUser"]["alias"][
                                "display_name"
                            ],
                            initial=1,
                            min_value=0,
                        )
                    )
            self.label_suffix = ""

    if request.method == "POST":
        form = NewExpenseForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            add_expense(
                request.session,
                registry,
                data["description"],
                data["amount"],
                (data["owner"], memberships[data["owner"]]),
                data["date"],
                [
                    (
                        m["RegistryMembershipNonUser"]["uuid"],
                        data[m["RegistryMembershipNonUser"]["uuid"]],
                    )
                    for m in registry["memberships"]
                    if m["RegistryMembershipNonUser"]["status"] == "ACTIVE"
                ],
            )
            form = NewExpenseForm()
            registry = get_registry(request.session, tricount_public_identifier)
    else:
        form = NewExpenseForm()

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
            "balance": parse_balance(registry["all_registry_entry"], memberships),
            "new_expense_form": form,
        },
    )
