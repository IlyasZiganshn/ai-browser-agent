from agent.safety import is_dangerous


def test_forbidden_payment_word_blocked():
    assert is_dangerous("Оплати счёт 12345") is True


def test_forbidden_delete_word_blocked():
    assert is_dangerous("Удали все файлы") is True


def test_forbidden_confirm_payment_blocked():
    assert is_dangerous("Подтвердить платеж") is True


def test_safe_navigation_task_allowed():
    assert is_dangerous("Открой википедию и найди статью") is False


def test_case_insensitive():
    assert is_dangerous("ОПЛАТИ") is True
