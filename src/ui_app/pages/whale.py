"""
Whale 点名结果页面
从 HTTP 服务器获取 results 和 students 数据并显示
"""

import socket

from config import save_settings, settings
from ui_framework.components.unifont_text import UnifontText
from ui_framework.page import Page


class WhalePage(Page):
    """Whale 点名结果显示页面"""

    def __init__(self):
        super().__init__("Whale")

        self.students = {}  # id -> name
        self.results = []  # list of student ids
        self.current_page = 0
        self.items_per_page = 4  # 每页显示4条，每条16像素高

        # 创建4个 UnifontText 组件用于显示
        self.text_components = []
        for i in range(self.items_per_page):
            text = UnifontText("", x=0, y=i * 16)
            self.text_components.append(text)
            self.add_component(text)

        self.error_text = UnifontText("", x=0, y=24)
        self.add_component(self.error_text)

        self.server_port = 28773
        self.data_loaded = False
        self.poll_interval = 3.0  # 轮询间隔（秒）
        self.poll_timer = 0.0

    def _get_server_ip(self):
        """从设置获取服务器IP"""
        return settings.get("whale_ip", "")

    def _set_server_ip(self, ip):
        """保存服务器IP到设置"""
        settings["whale_ip"] = ip
        save_settings()

    def on_enter(self, **kwargs):
        super().on_enter(**kwargs)
        self.current_page = 0
        self.data_loaded = False
        self.poll_timer = 0.0  # 重置轮询计时器

        # 检查是否有保存的IP
        server_ip = self._get_server_ip()
        if not server_ip:
            # 没有保存的IP，提示用户输入
            self._prompt_ip_input()
        else:
            # 尝试获取数据
            success = self.fetch_data()
            if not success:
                # 获取失败，提示用户重新输入IP
                self._prompt_ip_input()
            else:
                self.update_display()

    def _prompt_ip_input(self):
        """弹出IP输入页面"""
        from ui_app.pages.ipinput import IPInputPage

        default_ip = self._get_server_ip() or "192.168.1.1"
        ip_page = IPInputPage(
            title="Whale Server IP",
            default_value=default_ip,
            callback=self._on_ip_input,
        )
        if self.manager:
            self.manager.push_page(ip_page)

    def _on_ip_input(self, ip_address):
        """IP输入完成回调"""
        if ip_address:
            self._set_server_ip(ip_address)
            # 尝试获取数据
            success = self.fetch_data()
            if not success:
                # 仍然失败，再次提示输入
                self._prompt_ip_input()
            else:
                self.update_display()

    def fetch_data(self):
        """从服务器获取 students 和 results 数据，返回是否成功"""
        server_ip = self._get_server_ip()
        if not server_ip:
            self.error_text.text = "No server IP"
            return False

        try:
            # 获取 students
            students_data = self._http_get(server_ip, "/students")
            if students_data:
                self.students = self._parse_json(students_data)

            # 获取 results
            results_data = self._http_get(server_ip, "/results")
            if results_data:
                self.results = self._parse_json(results_data)

            self.error_text.text = ""
            self.data_loaded = True
            return True
        except Exception as e:
            self.error_text.text = f"Error: {e}"
            self.students = {}
            self.results = []
            self.data_loaded = False
            return False

    def _http_get(self, host, path):
        """发送 HTTP GET 请求"""
        addr = socket.getaddrinfo(host, self.server_port)[0][-1]
        s = socket.socket()
        s.settimeout(5)
        try:
            s.connect(addr)
            request = f"GET {path} HTTP/1.1\r\nHost: {host}:{self.server_port}\r\nConnection: close\r\n\r\n"
            s.send(request.encode())

            response = b""
            while True:
                chunk = s.recv(1024)
                if not chunk:
                    break
                response += chunk

            # 解析 HTTP 响应，获取 body
            response_str = response.decode("utf-8")
            if "\r\n\r\n" in response_str:
                body = response_str.split("\r\n\r\n", 1)[1]
                return body
            return None
        finally:
            s.close()

    def _parse_json(self, json_str):
        """简单的 JSON 解析"""
        import json

        return json.loads(json_str)

    def update(self, delta_time):
        """更新页面状态"""
        super().update(delta_time)

        # 轮询数据
        if self.data_loaded:
            self.poll_timer += delta_time
            if self.poll_timer >= self.poll_interval:
                self.poll_timer = 0.0
                self.fetch_data()
                self.update_display()

    def update_display(self):
        """更新显示内容"""
        # 如果数据未加载，不更新显示
        if not self.data_loaded:
            for text in self.text_components:
                text.text = ""
            return

        total_items = len(self.results)
        total_pages = max(
            1, (total_items + self.items_per_page - 1) // self.items_per_page
        )

        # 确保当前页有效
        if self.current_page >= total_pages:
            self.current_page = total_pages - 1
        if self.current_page < 0:
            self.current_page = 0

        start_index = self.current_page * self.items_per_page

        for i in range(self.items_per_page):
            index = start_index + i
            if index < total_items:
                student_id = self.results[index]
                # student_id 可能是字符串或整数
                student_id_str = str(student_id)
                name = self.students.get(
                    student_id_str, self.students.get(student_id, "Unknown")
                )
                self.text_components[i].text = f"{index}. #{student_id} {name}"
            else:
                self.text_components[i].text = ""

    def _handle_page_event(self, event):
        event_type = event.get("type")
        key = event.get("key")

        if event_type == "key_press":
            if key == "up":
                # 上一页
                if self.current_page > 0:
                    self.current_page -= 1
                    self.update_display()
                return True
            elif key == "down":
                # 下一页
                total_items = len(self.results)
                total_pages = max(
                    1, (total_items + self.items_per_page - 1) // self.items_per_page
                )
                if self.current_page < total_pages - 1:
                    self.current_page += 1
                    self.update_display()
                return True
            elif key == "ok":
                # 刷新数据
                success = self.fetch_data()
                if not success:
                    self._prompt_ip_input()
                else:
                    self.update_display()
                return True
            elif key == "back":
                # 返回
                if self.manager:
                    self.manager.pop_page()
                return True

        return False
