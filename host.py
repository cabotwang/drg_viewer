from Widget.Hydralit import HydraApp
import streamlit as st
from coding import codingApp
from graph import graphyApp

st.set_page_config(layout="wide", initial_sidebar_state='collapsed')

for line in open('style.css', encoding='utf-8'):
    st.markdown(f'<style>{line}</style>', unsafe_allow_html=True)

if __name__ == '__main__':
    st.title('编码辅助平台')
    app = HydraApp(title='编码辅助平台', favicon="🏠", navbar_theme={'menu_background':'royalblue'})
    app.add_app("编码推荐", icon="📚", app=codingApp())
    app.add_app("图像化编码", icon="⌨", app=graphyApp())
    app.run()


