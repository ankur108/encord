# Import dependencies
import os

from encord import EncordUserClient
from src.config import (
    PRIVATE_KEY_PATH
)

# Authenticate with Encord. The configured value may be either a path to a
# private key file (local dev) or the key contents itself (CI, where the key
# is injected via a secret). Detect which and pass the right argument.
if PRIVATE_KEY_PATH and os.path.isfile(PRIVATE_KEY_PATH):
    user_client = EncordUserClient.create_with_ssh_private_key(
        ssh_private_key_path=PRIVATE_KEY_PATH
    )
else:
    user_client = EncordUserClient.create_with_ssh_private_key(
        ssh_private_key=PRIVATE_KEY_PATH
    )