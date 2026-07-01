from __future__ import annotations

import re
from typing import Any


def sanitize_error_text(value: Any) -> str:
    text = str(value)
    return re.sub(
        r"(serviceKey=)[^&\s)]+",
        r"\1<redacted>",
        text,
        flags=re.IGNORECASE,
    )
