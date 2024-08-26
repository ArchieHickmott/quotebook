import bcrypt
import hashlib
import hmac

_log_rounds = 12
_prefix = '2b'
_handle_long_passwords = False

def _unicode_to_bytes(unicode_string):
    if isinstance(unicode_string, str):
        bytes_object = bytes(unicode_string, 'utf-8')
    else:
        bytes_object = unicode_string
    return bytes_object

def generate_password_hash(password, rounds=None, prefix=None):
    if not password:
        raise ValueError('Password must be non-empty.')

    if rounds is None:
        rounds = _log_rounds
    if prefix is None:
        prefix = _prefix

    # Python 3 unicode strings must be encoded as bytes before hashing.
    password = _unicode_to_bytes(password)
    prefix = _unicode_to_bytes(prefix)

    if _handle_long_passwords:
        password = hashlib.sha256(password).hexdigest()
        password = _unicode_to_bytes(password)

    salt = bcrypt.gensalt(rounds=rounds, prefix=prefix)
    return str(bcrypt.hashpw(password, salt).decode("utf-8"))

def check_password_hash(pw_hash, password):
    pw_hash = _unicode_to_bytes(pw_hash)
    password = _unicode_to_bytes(password)

    if _handle_long_passwords:
        password = hashlib.sha256(password).hexdigest()
        password = _unicode_to_bytes(password)

    return bcrypt.checkpw(password, pw_hash)