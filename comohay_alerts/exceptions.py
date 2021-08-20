from typing import Optional


class HTTPException(Exception):
    def __init__(
        self,
        status_code: Optional[int],
        detail: Optional[str],
        *args: object,
    ):
        super().__init__(*args)
        self.status_code = status_code
        self.detail = detail
