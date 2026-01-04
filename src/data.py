from datetime import date, datetime, time, timedelta


class TimeRange:
    @classmethod
    def from_string(cls, range_str: str, sep="~"):
        """支持从 "14:30~15:10" 这种格式直接创建对象"""
        s, e = range_str.split(sep)
        start_time = time(*(int(x) for x in s.split(":")))  # type: ignore
        end_time = time(*(int(x) for x in e.split(":")))  # type: ignore
        return cls(start_time, end_time)

    def __init__(self, start_time: time, end_time: time):
        self.start_time = start_time
        self.end_time = end_time

    def contains(self, check_time: time) -> bool:
        if self.start_time <= self.end_time:
            return self.start_time <= check_time <= self.end_time
        else:
            return check_time >= self.start_time or check_time <= self.end_time

    @property
    def duration(self) -> timedelta:
        start_dt = datetime.combine(date.min, self.start_time)
        end_dt = datetime.combine(date.min, self.end_time)
        if end_dt < start_dt:
            end_dt += timedelta(days=1)
        return end_dt - start_dt


class Lesson:
    def __init__(
        self, name: str, alias: str, time_range: TimeRange, *, hidden: bool = False
    ):
        self.name = name
        self.alias = alias
        self.time_range = time_range
        self.hidden = hidden

    def is_happening_at(self, check_time: time) -> bool:
        return self.time_range.contains(check_time)


LESSONS = [
    [
        Lesson("升旗仪式", "*", TimeRange.from_string("7:40~8:00")),
        Lesson("化学", "Ch", TimeRange.from_string("8:30~9:10")),
        Lesson("历史", "H", TimeRange.from_string("9:18~10:00")),
        Lesson("物理", "P", TimeRange.from_string("10:08~10:55")),
        Lesson("英语", "E", TimeRange.from_string("11:05~11:45")),
        Lesson("语文", "C", TimeRange.from_string("12:25~12:55")),
        Lesson("语文", "C", TimeRange.from_string("13:00~13:40")),
        Lesson("体育", "PE", TimeRange.from_string("13:48~14:35")),
        Lesson("大课间", "*", TimeRange.from_string("14:40~15:00"), hidden=True),
        Lesson("数学", "M", TimeRange.from_string("15:00~15:45")),
        Lesson("数学", "M", TimeRange.from_string("15:53~16:35")),
        Lesson("曲", "Ru", TimeRange.from_string("16:45~17:30")),
    ],
    [
        Lesson("生物", "B", TimeRange.from_string("7:40~8:00")),
        Lesson("生物", "B", TimeRange.from_string("8:30~9:10")),
        Lesson("美术", "A", TimeRange.from_string("9:18~10:00")),
        Lesson("道德与法治", "Ru", TimeRange.from_string("10:08~10:55")),
        Lesson("体育", "PE", TimeRange.from_string("11:05~11:45")),
        Lesson("数学", "M", TimeRange.from_string("12:25~12:55")),
        Lesson("英语", "E", TimeRange.from_string("13:00~13:40")),
        Lesson("数学", "M", TimeRange.from_string("13:48~14:35")),
        Lesson("大课间", "*", TimeRange.from_string("14:40~15:00"), hidden=True),
        Lesson("语文", "C", TimeRange.from_string("15:00~15:45")),
        Lesson("语文", "C", TimeRange.from_string("15:53~16:35")),
        Lesson("物理", "P", TimeRange.from_string("16:45~17:30")),
    ],
    [
        Lesson("道德与法治", "Ru", TimeRange.from_string("7:40~8:00")),
        Lesson("英语", "E", TimeRange.from_string("8:30~9:10")),
        Lesson("语文", "C", TimeRange.from_string("9:18~10:00")),
        Lesson("物理", "P", TimeRange.from_string("10:08~10:55")),
        Lesson("数学", "M", TimeRange.from_string("11:05~11:45")),
        Lesson("班级", "*", TimeRange.from_string("12:25~12:55")),
        Lesson("音乐", "Mu", TimeRange.from_string("13:00~13:40")),
        Lesson("体育", "PE", TimeRange.from_string("13:48~14:35")),
        Lesson("大课间", "*", TimeRange.from_string("14:40~15:00"), hidden=True),
        Lesson("班会", "*", TimeRange.from_string("15:00~15:45")),
        Lesson("群育", "*", TimeRange.from_string("15:53~16:35")),
        Lesson("英语", "E", TimeRange.from_string("16:45~17:30")),
    ],
    [
        Lesson("语文", "C", TimeRange.from_string("7:40~8:00")),
        Lesson("数学", "M", TimeRange.from_string("8:30~9:10")),
        Lesson("道德与法治", "Ru", TimeRange.from_string("9:18~10:00")),
        Lesson("语文", "C", TimeRange.from_string("10:08~10:55")),
        Lesson("体育", "PE", TimeRange.from_string("11:05~11:45")),
        Lesson("英语", "E", TimeRange.from_string("12:25~12:55")),
        Lesson("历史", "H", TimeRange.from_string("13:00~13:40")),
        Lesson("物理", "P", TimeRange.from_string("13:48~14:35")),
        Lesson("大课间", "*", TimeRange.from_string("14:40~15:00"), hidden=True),
        Lesson("英语", "E", TimeRange.from_string("15:00~15:45")),
        Lesson("英语", "E", TimeRange.from_string("15:53~16:35")),
        Lesson("晚锻炼", "*", TimeRange.from_string("16:45~17:30")),
    ],
    [
        Lesson("英语", "E", TimeRange.from_string("7:40~8:00")),
        Lesson("道德与法治", "Ru", TimeRange.from_string("8:30~9:10")),
        Lesson("英语", "E", TimeRange.from_string("9:18~10:00")),
        Lesson("数学", "M", TimeRange.from_string("10:08~10:55")),
        Lesson("语文", "C", TimeRange.from_string("11:05~11:45")),
        Lesson("单:数学/双:物理", "?", TimeRange.from_string("12:25~12:55")),
        Lesson("生物", "B", TimeRange.from_string("13:00~13:40")),
        Lesson("化学", "Ch", TimeRange.from_string("13:48~14:35")),
    ],
]
