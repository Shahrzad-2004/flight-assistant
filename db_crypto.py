
import os

from cryptography.fernet import Fernet, InvalidToken

PREFIX = "enc:v1:"

_fernet = None


def _load_key() -> str:
    key = os.environ.get("DB_ENCRYPTION_KEY")

    if not key:
        try:
            import streamlit as st
            key = st.secrets.get("DB_ENCRYPTION_KEY")
        except Exception:
            key = None

    if not key:
        raise RuntimeError(
            "کلید DB_ENCRYPTION_KEY پیدا نشد. با دستور زیر یک کلید بساز و در "
            ".streamlit/secrets.toml بگذار:\n"
            'python -c "from cryptography.fernet import Fernet; '
            'print(Fernet.generate_key().decode())"'
        )

    return key


def _get_fernet() -> Fernet:
    global _fernet

    if _fernet is None:
        try:
            _fernet = Fernet(_load_key().encode())
        except ValueError as error:
            raise RuntimeError(
                "DB_ENCRYPTION_KEY معتبر نیست؛ باید خروجی Fernet.generate_key() باشد."
            ) from error

    return _fernet


def is_encrypted(value) -> bool:
    return isinstance(value, str) and value.startswith(PREFIX)


def encrypt_text(value):
    """None و مقدار از قبل رمزشده دست‌نخورده برمی‌گردند."""
    if value is None or is_encrypted(value):
        return value

    token = _get_fernet().encrypt(str(value).encode("utf-8"))
    return PREFIX + token.decode("ascii")


def decrypt_text(value):
    """مقدار بدون پیشوند (داده‌ی قدیمی) همان‌طور که هست برمی‌گردد."""
    if not is_encrypted(value):
        return value

    try:
        return _get_fernet().decrypt(value[len(PREFIX):].encode("ascii")).decode("utf-8")
    except InvalidToken as error:
        raise RuntimeError(
            "رمزگشایی ناموفق بود: DB_ENCRYPTION_KEY با کلیدی که داده با آن "
            "رمز شده یکی نیست."
        ) from error
