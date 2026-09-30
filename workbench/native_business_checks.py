"""Executable approved native business examples, reused by standalone delivery probes."""

import httpx


def wire(template, sample):
    def key(name):
        first, *rest = name.split("_")
        return first + "".join(piece.title() for piece in rest)
    return {(name if template == "fastapiadmin" else key(name)): value for name, value in sample.items()}


def successful(response):
    return response.is_success and response.json().get("code", 200) in {0, 200}


def data(response):
    if not successful(response):
        raise ValueError("Native rule positive example failed: HTTP " + str(response.status_code))
    body = response.json()
    return body.get("data", body)


def check_business_examples(template, base, token, targets, plan):
    """Reject creates/updates before persistence; never accept a server crash as validation."""
    plan = plan.model_dump() if hasattr(plan, "model_dump") else plan
    result = {"passed": False, "rules": []}
    with httpx.Client(base_url=base, trust_env=False, timeout=30,
                      headers={"Authorization": "Bearer " + token, "tenant-id": "1"}) as client:
        for rule in plan.get("custom_rules", []):
            target = next(t for t in targets if t["entity"] == rule["entity"])
            api, fast = target["api"], template == "fastapiadmin"
            accepted = [wire(template, row) for row in rule["accept_examples"]]
            rejected = [wire(template, row) for row in rule["reject_examples"]]
            identifiers = []
            def rows():
                value = data(client.get(target["list"], params={"pageSize": 100, "page_size": 100}))
                return value.get("items", value.get("list"))
            def get(identifier):
                return data(client.get(api + (f"/detail/{identifier}" if fast else "/get"), params={} if fast else {"id": identifier}))
            try:
                for sample in accepted:
                    created = data(client.post(api + "/create", json=sample))
                    identifier = created["id"] if isinstance(created, dict) else created
                    if type(identifier) is not int or identifier <= 0:
                        raise ValueError("Native create returned no real record ID")
                    identifiers.append(identifier)
                    actual = get(identifier)
                    if any(actual.get(k) != v for k, v in sample.items()):
                        raise ValueError("Native rule accepted record changed")
                identifier = identifiers[0]
                baseline = get(identifier)
                for sample in rejected:
                    previous_ids = {row["id"] for row in rows()}
                    response = client.post(api + "/create", json=sample)
                    if successful(response):
                        accidental = data(response)
                        accidental = accidental["id"] if isinstance(accidental, dict) else accidental
                        if type(accidental) is int:
                            identifiers.append(accidental)
                    if successful(response) or response.status_code >= 500:
                        raise ValueError("Native rule negative create was accepted or crashed")
                    if response.status_code not in {200, 400, 422}:
                        raise ValueError("Native rule rejection was not a client validation result")
                    if "RND_BUSINESS_RULE" not in response.text:
                        raise ValueError("Negative example failed for an unrelated reason")
                    if {row["id"] for row in rows()} != previous_ids:
                        raise ValueError("Rejected create wrote a business record")
                    response = client.put(api + (f"/update/{identifier}" if fast else "/update"), json=sample if fast else {"id": identifier, **sample})
                    if successful(response) or response.status_code >= 500 or "RND_BUSINESS_RULE" not in response.text:
                        raise ValueError("Native rule negative update was not validated")
                    if any(get(identifier).get(k) != v for k, v in baseline.items()):
                        raise ValueError("Rejected update changed the saved record")
                # Positive update must work too; the rule cannot simply disable editing.
                value = accepted[-1]
                data(client.put(api + (f"/update/{identifier}" if fast else "/update"), json=value if fast else {"id": identifier, **value}))
                if any(get(identifier).get(k) != v for k, v in value.items()):
                    raise ValueError("Positive update did not persist")
                result["rules"].append({"entity": rule["entity"], "accepted": len(accepted), "rejected_create": len(rejected), "rejected_update": len(rejected), "positive_update": True, "rejected_writes_absent": True})
            finally:
                for identifier in identifiers:
                    data(client.request("DELETE", api + "/delete", **({"json": [identifier]} if fast else {"params": {"id": identifier}})))
    result["passed"] = True
    return result
