"""
主菜单页面
"""

from datetime import time, timedelta

from data import LESSONS
from ntp import Ntp
from ui_framework.components.progress_bar import ProgressBar
from ui_framework.components.text import Text
from ui_framework.components.unifont_text import UnifontText
from ui_framework.page import Page


class Home(Page):
    """首页"""

    def __init__(self):
        super().__init__("Home")

        self.primary = UnifontText("--:--:--", 8, 8)
        self.add_component(self.primary)
        self.secondary = Text("----/--/--", 8, 32)
        self.add_component(self.secondary)

    def update(self, delta_time):
        super().update(delta_time)
        year, month, day, hour, minute, second, weekday, yearday, us = Ntp.time()
        if 0 <= weekday <= 4:
            # 查询现在是哪节课
            lesson = None
            lessons_today = LESSONS[weekday]
            for l in lessons_today:
                if l.time_range.contains(time(hour, minute, second)):
                    lesson = l
                    break
            if lesson:
                # 距离下课的时间
                time_until_end = (
                    lesson.time_range.end_time.hour * 3600
                    + lesson.time_range.end_time.minute * 60
                    + lesson.time_range.end_time.second
                    - (hour * 3600 + minute * 60 + second)
                )
                self.primary.text = (
                    f"{lesson.name}>{time_until_end // 60:02}:{time_until_end % 60:02}"
                )
                self.secondary.text = f"{hour:02}:{minute:02} {month:02}/{day:02}"
                return
            else:
                next_lesson = None
                for l in lessons_today:
                    if l.time_range.start_time > time(hour, minute, second):
                        next_lesson = l
                        break
                # 上课倒计时
                if next_lesson is not None:
                    time_until_start = (
                        next_lesson.time_range.start_time.hour * 3600
                        + next_lesson.time_range.start_time.minute * 60
                        + next_lesson.time_range.start_time.second
                        - (hour * 3600 + minute * 60 + second)
                    )
                    self.primary.text = f"{time_until_start // 60:02}:{time_until_start % 60:02}>{next_lesson.name}"
                    self.secondary.text = f"{hour:02}:{minute:02} {month:02}/{day:02}"
                    return
        self.primary.text = f"{hour:02}:{minute:02}:{second:02}"
        self.secondary.text = f"{year:04}/{month:02}/{day:02}"

    def _handle_page_event(self, event):
        if event.get("type") == "key_press":
            key = event.get("key")
            if key == "ok":
                if self.manager:
                    self.manager.push_page("main_menu")
                    return True
            elif key == "back":
                if self.manager:
                    self.manager.push_page("lessons")
                    return True
        return False
