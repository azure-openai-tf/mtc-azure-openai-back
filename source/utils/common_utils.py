"""
@created_by ayaan
@created_at 2023.05.08
"""
import time
from datetime import datetime
from pytz import timezone


class CommonUtils:
    @classmethod
    def get_running_time(cls, start: time, end: time) -> time:
        return end - start

    @classmethod
    def get_kst_now(cls) -> str:
        return datetime.now(timezone("Asia/Seoul"))

    @classmethod
    def get_kst_now_str(cls, format: str = "%Y-%m-%d") -> str:
        return datetime.now(timezone("Asia/Seoul")).strftime(format)
