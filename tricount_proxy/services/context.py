from datetime import datetime


def _common_expense(expense: dict) -> dict:
    return {
        "amount": float(expense["RegistryEntry"]["amount"]["value"]) * -1,
        "description": expense["RegistryEntry"]["description"],
        "date": datetime.strptime(
            expense["RegistryEntry"]["date"], "%Y-%m-%d %H:%M:%S.%f"
        ),
        "owner": expense["RegistryEntry"]["membership_owned"][
            "RegistryMembershipNonUser"
        ]["alias"]["display_name"],
    }


def parse_expense(expense: dict) -> dict:
    return {
        **_common_expense(expense),
        "type": "EXPENSE",
        "allocations": [
            {
                "ratio": a.get("share_ratio"),
                "amount": float(a["amount"]["value"]) * -1,
                "name": a["membership"]["RegistryMembershipNonUser"]["alias"][
                    "display_name"
                ],
            }
            for a in expense["RegistryEntry"]["allocations"]
        ],
        "allocations_have_ratio": any(
            "share_ratio" in a for a in expense["RegistryEntry"]["allocations"]
        ),
    }


def parse_refund(expense: dict) -> dict:
    allocations = [
        a
        for a in expense["RegistryEntry"]["allocations"]
        if float(a["amount"]["value"]) != 0
    ]
    # In the case where the refund targets several people (this seems to be possible
    # from the API response, not sure if it can happen in practice), just return the
    # regular expense format that handle multiple people.
    if len(allocations) != 1:
        return parse_expense(expense)
    return {
        **_common_expense(expense),
        "type": "REFUND",
        "target": allocations[0]["membership"]["RegistryMembershipNonUser"]["alias"][
            "display_name"
        ],
    }
