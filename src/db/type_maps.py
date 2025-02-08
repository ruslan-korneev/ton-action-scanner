from datetime import datetime
from typing import Annotated

from sqlalchemy import DateTime, func
from sqlalchemy.orm import mapped_column

datetime_auto_now_add = Annotated[
    datetime,
    mapped_column(DateTime(timezone=True), server_default=func.now()),
]
datetime_auto_now = Annotated[
    datetime,
    mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    ),
]
