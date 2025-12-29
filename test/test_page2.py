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
            self.page.go(self.current)

    def forward(self, e=None):
        """前进"""
        if self.forward_stack:
            self.back_stack.append(self.current)
            self.current = self.forward_stack.pop()
            self.page.go(self.current)

# 路由管理
class RouteManager:
    _routes = {}
    @classmethod
    def register(cls, path: str, page_class):
        cls._routes[path] = page_class
    @classmethod
    def get(cls, path: str):
        return cls._routes.get(path)

def register_route(path: str):
    def decorator(cls):
        RouteManager.register(path, cls)
        cls.route_path = path
        return cls
    return decorator

# 基类
class BasePage:
    def __init__(self, page: ft.Page, nav: Navigator):
        self.page = page
        self.nav = nav

    def common_navbar(self, title: str):
        return ft.AppBar(
            title=ft.Text(title),
            actions=[
                ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=self.nav.back),
                ft.IconButton(icon=ft.Icons.ARROW_FORWARD, on_click=self.nav.forward),
            ]
        )

    def build(self) -> ft.View:
        raise NotImplementedError

# 页面
@register_route("/")
class HomePage(BasePage):
    def build(self) -> ft.View:
        return ft.View(
            route=self.route_path,
            controls=[
                self.common_navbar("首页"),
                ft.Text("欢迎来到首页！"),
                ft.ElevatedButton("去设置页",
                    on_click=lambda e: self.nav.navigate("/settings")),
                ft.ElevatedButton("去关于页",
                    on_click=lambda e: self.nav.navigate("/about")),
            ],
            vertical_alignment=ft.MainAxisAlignment.CENTER
        )

@register_route("/settings")
class SettingsPage(BasePage):
    def build(self) -> ft.View:
        return ft.View(
            route=self.route_path,
            controls=[
                self.common_navbar("设置页面"),
                ft.Text("这里是设置页面"),
                ft.ElevatedButton("返回首页", on_click=lambda e: self.nav.navigate("/")),
            ],
            vertical_alignment=ft.MainAxisAlignment.CENTER
        )

@register_route("/about")
class AboutPage(BasePage):
    def build(self) -> ft.View:
        return ft.View(
            route=self.route_path,
            controls=[
                self.common_navbar("关于页面"),
                ft.Text("这是关于我们页面"),
                ft.ElevatedButton("返回首页", on_click=lambda e: self.nav.navigate("/")),
            ],
            vertical_alignment=ft.MainAxisAlignment.CENTER
        )

# 应用
class MyApp:
    def main(self, page: ft.Page):
        page.title = "Flet 真正前进/后退 Demo"
        page.window_width = 400
        page.window_height = 300

        nav = Navigator(page)

        def route_change(e: ft.RouteChangeEvent):
            page.views.clear()
            PageCls = RouteManager.get(e.route)
            if PageCls:
                page.views.append(PageCls(page, nav).build())
            else:
                page.views.append(ft.View(
                    route=e.route,
                    controls=[ft.Text(f"404: {e.route}")]
                ))
            page.update()

        page.on_route_change = route_change
        page.go("/")   # 进入首页
        nav.current = "/"  # 初始化当前路由

    def run(self):
        ft.app(target=self.main)

if __name__ == "__main__":
    MyApp().run()
