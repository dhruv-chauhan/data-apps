import os
import streamlit.components.v1 as components

parent_dir = os.path.dirname(os.path.abspath(__file__))
build_dir = os.path.join(parent_dir, "build")
_component_func = components.declare_component("header", path=build_dir)

def header(title="", img_src="", author_url="", author="", key=None):
    component_value = _component_func(title=title, img_src=img_src, author_url=author_url, author=author, key=key)
    return component_value