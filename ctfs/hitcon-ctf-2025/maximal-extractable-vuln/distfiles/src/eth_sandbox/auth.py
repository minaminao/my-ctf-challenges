import os


def get_shared_secret() -> str:
    shared_secret = os.getenv("SHARED_SECRET")
    assert shared_secret is not None and len(shared_secret) >= 10
    return shared_secret
