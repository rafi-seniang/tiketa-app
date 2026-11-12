"""HMAC-SHA256 signatures for values the service hands out and must recognise when they come back."""

import hashlib
import hmac


class Signer:
    def __init__(self, secret: str) -> None:
        self._secret = secret.encode()

    def signature(self, text: str) -> str:
        return hmac.new(self._secret, text.encode(), hashlib.sha256).hexdigest()

    def has_signed(self, text: str, signature: str) -> bool:
        return hmac.compare_digest(signature, self.signature(text))  # constant time
