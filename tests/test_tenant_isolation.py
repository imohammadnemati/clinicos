import pytest
from unittest.mock import MagicMock, patch

from bot import get_or_create_patient_by_telegram, get_patient_by_telegram_id
from utils.role_utils import get_user_clinic_id


def test_unknown_user_has_no_tenant():
    db = MagicMock()
    db.query.return_value.filter_by.return_value.first.return_value = None

    with patch("utils.role_utils.SessionLocal", return_value=db):
        assert get_user_clinic_id(999999) is None


def test_ambiguous_patient_tenant_has_no_tenant():
    db = MagicMock()
    staff_query = db.query.return_value
    staff_query.filter_by.return_value.first.return_value = None
    staff_query.join.return_value.filter.return_value.distinct.return_value.all.return_value = [
        (10,),
        (20,),
    ]

    with patch("utils.role_utils.SessionLocal", return_value=db):
        assert get_user_clinic_id(999999) is None


def test_unknown_user_cannot_create_patient():
    with patch("bot.get_user_clinic_id", return_value=None):
        with pytest.raises(ValueError):
            get_or_create_patient_by_telegram(999999, "Test User", MagicMock())


def test_patient_lookup_is_scoped_to_trusted_clinic():
    db = MagicMock()
    query = db.query.return_value
    query.join.return_value.filter.return_value.first.return_value = None

    with patch("bot.get_user_clinic_id", return_value=20):
        assert get_patient_by_telegram_id(12345, db) is None

    query.join.return_value.filter.assert_called_once()
