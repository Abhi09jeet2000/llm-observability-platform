import re
import hashlib


def normalize_message(message: str) -> str:
    message = re.sub(r"\b\d+\b", "<NUM>", message)
    message = re.sub(r"\b[0-9a-fA-F-]{8,}\b", "<ID>", message)
    message = re.sub(r"\b\d+\.\d+\.\d+\.\d+\b", "<IP>", message)
    return message


def generate_template_key(normalized_message: str) -> str:
    return hashlib.md5(normalized_message.encode()).hexdigest()