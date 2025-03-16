from collections import defaultdict
from datetime import datetime
from decimal import Decimal


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
            if float(a["amount"]["value"]) != 0
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


def parse_balance(entries: list[dict], memberships: dict[str, dict]) -> dict:
    amounts = defaultdict(lambda: 0)
    total_expenses = defaultdict(lambda: 0)
    for entry in entries:
        amounts[
            entry["RegistryEntry"]["membership_owned"]["RegistryMembershipNonUser"][
                "uuid"
            ]
        ] -= Decimal(entry["RegistryEntry"]["amount"]["value"])
        for allocation in entry["RegistryEntry"]["allocations"]:
            amounts[allocation["membership"]["RegistryMembershipNonUser"]["uuid"]] += (
                Decimal(allocation["amount"]["value"])
            )
            if entry["RegistryEntry"]["type_transaction"] == "NORMAL":
                total_expenses[
                    allocation["membership"]["RegistryMembershipNonUser"]["uuid"]
                ] -= Decimal(allocation["amount"]["value"])

    debtors = sorted(
        [(p, m) for p, m in amounts.items() if m > 0], key=lambda x: x[1], reverse=True
    )
    creditors = sorted(
        [(p, -m) for p, m in amounts.items() if m < 0], key=lambda x: x[1], reverse=True
    )

    transactions = []

    while debtors and creditors:
        debtor, debt = debtors.pop(0)
        creditor, credit = creditors.pop(0)

        amount = min(debt, credit)
        if amount > 0.10:
            transactions.append(
                {
                    "owner": memberships[creditor],
                    "target": memberships[debtor],
                    "amount": amount,
                }
            )

        if debt > credit:
            debtors.insert(0, (debtor, debt - amount))
        elif credit > debt:
            creditors.insert(0, (creditor, credit - amount))

    return {
        "summary": [
            {"name": name, "total": total_expenses[uuid], "balance": amounts[uuid]}
            for uuid, name in memberships.items()
        ],
        "refunds": transactions,
    }
