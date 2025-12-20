import streamlit as st
from appState import get_state


class PageBase():
    def __new__(cls, *args, **kwargs):
        """单例模式：每个类只会实例化一次"""
        key = f"_page_instance_{cls.__name__}"
        if key not in st.session_state:
            st.session_state[key] = super().__new__(cls)
        return st.session_state[key]


    def __init__(self):
        self.init()

        if not hasattr(self, "_initialized"):
            self.state = get_state()
            self._initialized = True  # 标记已初始化

    def init(self):
        pass

    def show():
        st.warning("请实现子类中的 show() 方法")