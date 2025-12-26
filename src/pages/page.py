import flet as ft
from abc import ABC, abstractmethod
from typing import Optional, List, Callable


class BasePage(ABC):
    """
    Flet页面基类
    提供页面的基础功能和生命周期管理
    """

    def __init__(self, page: ft.Page):
        """
        初始化基类
        :param page: Flet Page对象
        """
        self.page = page
        self.controls: List[ft.Control] = []
        self._is_initialized = False

    @abstractmethod
    def build(self) -> List[ft.Control]:
        """
        构建页面UI（子类必须实现）
        :return: 控件列表
        """
        pass

    def on_mount(self):
        """页面挂载时的钩子函数"""
        pass

    def on_unmount(self):
        """页面卸载时的钩子函数"""
        pass

    def on_resize(self, e):
        """窗口大小改变时的钩子函数"""
        pass

    def initialize(self):
        """初始化页面"""
        if not self._is_initialized:
            self.setup_page()
            self.controls = self.build()
            self.render()
            self.on_mount()
            self._is_initialized = True

    def setup_page(self):
        """设置页面基础配置（可在子类中重写）"""
        self.page.title = self.get_title()
        self.page.padding = self.get_padding()
        self.page.scroll = self.get_scroll()
        self.page.theme_mode = self.get_theme_mode()
        self.page.on_resized = self.on_resize

    def get_title(self) -> str:
        """获取页面标题（可在子类中重写）"""
        return "Flet Application"

    def get_padding(self) -> int:
        """获取页面内边距（可在子类中重写）"""
        return 20

    def get_scroll(self) -> Optional[str]:
        """获取滚动模式（可在子类中重写）"""
        return ft.ScrollMode.AUTO

    def get_theme_mode(self) -> str:
        """获取主题模式（可在子类中重写）"""
        return ft.ThemeMode.LIGHT

    def render(self):
        """渲染页面"""
        self.page.controls.clear()
        self.page.controls.extend(self.controls)
        self.page.update()

    def update(self):
        """更新页面"""
        self.page.update()

    def add_control(self, control: ft.Control):
        """添加控件到页面"""
        self.controls.append(control)
        self.page.controls.append(control)
        self.update()

    def remove_control(self, control: ft.Control):
        """从页面移除控件"""
        if control in self.controls:
            self.controls.remove(control)
        if control in self.page.controls:
            self.page.controls.remove(control)
        self.update()

    def clear(self):
        """清空页面所有控件"""
        self.controls.clear()
        self.page.controls.clear()
        self.update()

    def show_snack_bar(self, message: str, bgcolor: str = ft.Colors.BLUE):
        """显示消息提示"""
        snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=bgcolor
        )
        self.page.open(snack_bar)
        self.update()

    def show_dialog(self, title: str, content: str,
                   on_confirm: Optional[Callable] = None):
        """显示对话框"""
        def close_dialog(e):
            dialog.open = False
            self.update()
            if on_confirm:
                on_confirm(e)

        dialog = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Text(content),
            actions=[
                ft.TextButton("确定", on_click=close_dialog),
            ],
        )
        self.page.open(dialog)
        self.update()

    def navigate_to(self, route: str):
        """路由导航"""
        self.page.go(route)

    def go_back(self):
        """返回上一页"""
        self.page.go_back()


class ResponsiveBasePage(BasePage):
    """
    响应式页面基类
    支持不同屏幕尺寸的适配
    """

    def __init__(self, page: ft.Page):
        super().__init__(page)
        self.is_mobile = False
        self.is_tablet = False
        self.is_desktop = False
        self.update_device_type()

    def update_device_type(self):
        """更新设备类型"""
        width = self.page.width
        self.is_mobile = width < 600
        self.is_tablet = 600 <= width < 1024
        self.is_desktop = width >= 1024

    def on_resize(self, e):
        """响应窗口大小变化"""
        self.update_device_type()
        self.on_responsive_change()
        super().on_resize(e)

    def on_responsive_change(self):
        """响应式变化时的钩子函数（子类可重写）"""
        pass

    @abstractmethod
    def build_mobile(self) -> List[ft.Control]:
        """构建移动端UI"""
        pass

    @abstractmethod
    def build_tablet(self) -> List[ft.Control]:
        """构建平板端UI"""
        pass

    @abstractmethod
    def build_desktop(self) -> List[ft.Control]:
        """构建桌面端UI"""
        pass

    def build(self) -> List[ft.Control]:
        """根据设备类型构建UI"""
        if self.is_mobile:
            return self.build_mobile()
        elif self.is_tablet:
            return self.build_tablet()
        else:
            return self.build_desktop()
