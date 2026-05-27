"""Project settings.

Subclasses ``CoreSettings`` from core-utils, which defines the fields shared
across all projects (environment, logging). Add project-specific fields below.
"""

from core_utils.settings import CoreSettings


class Settings(CoreSettings):
    """Application settings, loaded from environment variables and .env files.

    Inherits ``environment``, ``log_level``, ``log_folder``, ``log_console``
    and the ``logs_dir`` property from ``CoreSettings``. ``model_config`` is
    merged with the parent's by pydantic, so only ``env_file`` is added here.
    """

    model_config = {
        "env_file": [".env", ".env.local"],
        "env_file_encoding": "utf-8",
    }

    # Add project-specific fields here, e.g.:
    # api_key: str = ""


settings = Settings()
