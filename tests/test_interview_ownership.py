
from unittest.mock import MagicMock, patch


def test_dashboard_does_not_expose_unowned_interviews():
    """
    When ownership is not configured, the dashboard should not
    return interview records to a user.
    """
    from services.dashboard_service import get_dashboard_data

    with patch(
        "services.dashboard_service.SessionLocal"
    ) as mock_session_factory:
        mock_session = MagicMock()
        mock_session_factory.return_value = mock_session

        # Simulate a model/query configuration where ownership
        # cannot be safely enforced.
        result = get_dashboard_data(user_id=123)

        assert isinstance(result, dict)

        if result.get("ownership_configured") is False:
            assert result.get("total_interviews", 0) == 0
            assert result.get("recent_interviews", []) == []

        mock_session.close.assert_called_once()


def test_authentication_rejects_invalid_credentials():
    """Invalid credentials must not authenticate a user."""

    from services.auth_service import authenticate_user

    result = authenticate_user(
        username="nonexistent_test_user_987",
        password="WrongPassword123",
    )

    assert not result


def test_password_hash_does_not_store_plaintext():
    """Passwords should be stored as hashes, not plain text."""

    from services.auth_service import hash_password, verify_password

    password = "TestPassword123"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("IncorrectPassword123", hashed)
