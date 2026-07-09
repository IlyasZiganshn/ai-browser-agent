FORBIDDEN = ["оплат", "удал", "подтвердить платеж"]


def is_dangerous(text: str) -> bool:
    return any(word in text.lower() for word in FORBIDDEN)
