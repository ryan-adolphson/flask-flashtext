import os


class BaseConfig:
    VERSION = "1.0.0"
    MAX_TEXT_LENGTH = 1_048_576
    MAX_KEYWORDS = 1000
    API_KEYS: set = {k.strip() for k in os.environ.get("API_KEYS", "").split(",") if k.strip()}


class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = False


class TestingConfig(BaseConfig):
    TESTING = True
    DEBUG = True
    API_KEYS: set = {"test-key-1"}
