import flet as ft

class Navigator:
    def __init__(self, page: ft.Page):
        self.page = page
        self.back_stack = []     # 历史访问
        self.forward_stack = []  # 前进历史
        self.current = None

    def navigate(self, route: str):
        """导航到新页面"""
        if self.current is not None:
            self.back_stack.append(self.current)
        self.current = route
        self.forward_stack.clear()  # 新导航清空前进栈
        self.page.go(route)

    def back(self, e=None):
        """后退"""
        if self.back_stack:
            self.forward_stack.append(self.current)
            self.current = self.back_stack.pop()
            self.page.views.pop()
            self.page.go(self.current)

    def forward(self, e=None):
        """前进"""
        if self.forward_stack:
            self.back_stack.append(self.current)
            self.current = self.forward_stack.pop()
            self.page.go(self.current)
