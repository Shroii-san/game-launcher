from __future__ import annotations

from gamelauncher.exception_handler import build_exception_dialog_text, format_exception_details


def test_build_exception_dialog_text_hides_stack_trace_from_user() -> None:
    user_message, detail = build_exception_dialog_text(ValueError("bad data"), "demo")

    assert "bad data" not in user_message
    assert "ValueError" in user_message
    assert "demo" in detail
    assert "Traceback" not in user_message


def test_format_exception_details_contains_exception_type_and_message() -> None:
    details = format_exception_details(ValueError("bad data"), "demo")

    assert "ValueError" in details
    assert "bad data" in details
    assert "demo" in details
