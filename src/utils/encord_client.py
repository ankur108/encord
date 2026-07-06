# Import dependencies
from encord import EncordUserClient
from src.config import (
    PRIVATE_KEY_PATH
)

# Authenticate with Encord using the path to your private key
user_client = EncordUserClient.create_with_ssh_private_key(
    ssh_private_key_path=PRIVATE_KEY_PATH
    )