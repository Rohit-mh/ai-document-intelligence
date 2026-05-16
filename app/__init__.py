"""
Application package.
"""
import logging

# ========================================
# Passlib Bcrypt Fix
# ========================================
# Passlib 1.7.4 has a bug with bcrypt >= 4.0.0 where it fails internal checks.
# This monkey-patch disables the buggy check.
# It must be applied BEFORE passlib.context.CryptContext is initialized.
try:
    from passlib.handlers.bcrypt import bcrypt as _bcrypt
    _bcrypt._finalize_backend_mixin = lambda *args, **kwargs: None
    logging.getLogger("passlib").setLevel(logging.ERROR)
except ImportError:
    pass