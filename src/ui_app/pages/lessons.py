from data import LESSONS
from ui_framework.components.text import Text
from ui_framework.components.unifont_text import UnifontText
from ui_framework.page import Page


class LessonsPage(Page):
    def __init__(self):
        super().__init__("Lessons")

        self.weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        self.current_weekday = 0
        self.cursor_row = 0
        self.cursor_col = 0

        self.weekday_text = Text("", x=64, y=0, align="center")
        self.add_component(self.weekday_text)

        self.lesson_grid_y = 10
        self.lesson_texts = []
        for i in range(12):
            row = i // 5
            col = i % 5
            x = col * 25 + 2
            y = self.lesson_grid_y + row * 8
            text = Text("", x=x, y=y, color=1)
            self.lesson_texts.append(text)
            self.add_component(text)

        self.selected_name_text = UnifontText("", x=2, y=36)
        self.add_component(self.selected_name_text)

        self.selected_time_text = Text("", x=2, y=54)
        self.add_component(self.selected_time_text)

        self.long_press_time = {}
        self.long_press_threshold = 0.5
        self.long_press_triggered = {}

    def on_enter(self, **kwargs):
        super().on_enter(**kwargs)
        self.update_display()

    def update_display(self):
        self.weekday_text.text = self.weekdays[self.current_weekday]

        lessons = LESSONS[self.current_weekday]
        # 移除hidden的课程
        lessons = [lesson for lesson in lessons if not lesson.hidden]

        for i in range(12):
            if i < len(lessons):
                lesson = lessons[i]
                alias = lesson.alias
                if len(alias) == 1:
                    alias = alias + " "
                self.lesson_texts[i].text = alias
            else:
                self.lesson_texts[i].text = ""

        if len(lessons) > 0:
            cursor_index = self.cursor_row * 5 + self.cursor_col
            if cursor_index < len(lessons):
                lesson = lessons[cursor_index]
                self.selected_name_text.text = lesson.name
                # 不能用strftime，因为micropython没实现
                # start = lesson.time_range.start_time.strftime("%H:%M")
                # end = lesson.time_range.end_time.strftime("%H:%M")
                start = f"{lesson.time_range.start_time.hour}:{lesson.time_range.start_time.minute:02d}"
                end = f"{lesson.time_range.end_time.hour}:{lesson.time_range.end_time.minute:02d}"
                self.selected_time_text.text = f"{start}~{end}"
            else:
                self.selected_name_text.text = ""
                self.selected_time_text.text = ""
        else:
            self.selected_name_text.text = ""
            self.selected_time_text.text = ""

    def render(self, display):
        super().render(display)

        lessons = LESSONS[self.current_weekday]
        cursor_index = self.cursor_row * 5 + self.cursor_col
        if cursor_index < len(lessons):
            col = self.cursor_col
            row = self.cursor_row
            x = col * 25 + 2
            y = self.lesson_grid_y + row * 8
            display.rect(x - 1, y - 1, 17, 9, 1)

    def update(self, delta_time):
        super().update(delta_time)

        for key in list(self.long_press_time.keys()):
            if key in self.long_press_time:
                self.long_press_time[key] += delta_time
                if self.long_press_time[key] >= self.long_press_threshold:
                    if key not in self.long_press_triggered:
                        self.long_press_triggered[key] = True
                        self._handle_long_press(key)

    def _handle_long_press(self, key):
        if key == "up":
            self.current_weekday = (self.current_weekday - 1) % 5
            self.update_display()
        elif key == "down":
            self.current_weekday = (self.current_weekday + 1) % 5
            self.update_display()

    def _handle_page_event(self, event):
        event_type = event.get("type")
        key = event.get("key")

        if event_type == "key_press":
            if key in ["up", "down"]:
                self.long_press_time[key] = 0
                self.long_press_triggered.pop(key, None)

            if key == "up":
                # 向前移动光标
                lessons = LESSONS[self.current_weekday]
                cursor_index = self.cursor_row * 5 + self.cursor_col
                if cursor_index > 0:
                    cursor_index -= 1
                    self.cursor_row = cursor_index // 5
                    self.cursor_col = cursor_index % 5
                    self.update_display()
                return True
            elif key == "down":
                # 向后移动光标
                lessons = LESSONS[self.current_weekday]
                lessons = [lesson for lesson in lessons if not lesson.hidden]
                cursor_index = self.cursor_row * 5 + self.cursor_col
                if cursor_index + 1 < len(lessons):
                    cursor_index += 1
                    self.cursor_row = cursor_index // 5
                    self.cursor_col = cursor_index % 5
                    self.update_display()
                return True
            elif key == "back":
                # 返回
                if self.manager:
                    self.manager.pop_page()
                return True
            elif key == "ok":
                # 什么都不做
                return True

        elif event_type == "key_release":
            if key in self.long_press_time:
                del self.long_press_time[key]
            if key in self.long_press_triggered:
                del self.long_press_triggered[key]

        return False
