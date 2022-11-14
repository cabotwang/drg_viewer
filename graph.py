import streamlit as st
import pandas as pd
from Widget import modal
from Widget.Hydralit import HydraHeadApp
import base64
import streamlit.components.v1 as components

bone_position_dict = {'肱骨': ['近端', '骨干', '远端'], '尺桡骨': ['近端', '骨干', '远端'], '股骨': ['近端', '骨干', '远端'],
                      '胫腓骨': ['近端', '骨干', '远端'], '骨盆': ['骨盆环', '髋臼']}

bone_pc_dict = {('肱骨', '近端'): '11ABC', ('肱骨', '骨干'): '12ABC', ('肱骨', '远端'): '13ABC',
                ('尺桡骨', '近端'): '21ABC', ('尺桡骨', '骨干'): '22ABC', ('尺桡骨', '远端'): '23ABC',
                ('股骨', '近端'): '31ABC', ('股骨', '骨干'): '32ABC', ('股骨', '远端'): '33ABC',
                ('胫腓骨', '近端'): '41ABC', ('胫腓骨', '骨干'): '42ABC', ('胫腓骨', '远端'): '43ABC',
                ('骨盆', '骨盆环'): '61ABC', ('胫腓骨', '髋臼'): '62ABC'}


class graphyApp(HydraHeadApp):
    def run(self):
        c1, c2, c0 = st.columns([1, 1, 3])
        bone = c1.selectbox('请选择骨折部位', ('肱骨', '尺桡骨', '股骨', '胫腓骨', '骨盆'))
        position = c2.selectbox('请选择骨折节段', set(bone_position_dict[bone]))

        pc_df = pd.read_csv('resource/图像化编码点位图.csv', usecols=['图像名称', '形状', '点位1', '点位2', '点位3', '点位4',
                                                                 '术语编码', '术语名称', 'ICD编码', 'ICD名称'])

        def bone_pic(pic_name):
            file_ = open(f"picture/肱骨/{pic_name}.png", "rb")
            contents = file_.read()
            data_url = base64.b64encode(contents).decode("utf-8")
            file_.close()
            selected_df = pc_df[pc_df['图像名称'] == pic_name]
            full_text = ''
            func_text = ''
            for index, col in selected_df.iterrows():
                text1 = '''<area shape=''' + str(col['图像名称']) + ''' coords="''' + \
                        ','.join([str(col['点位1']), str(col['点位2']), str(col['点位3']), str(col['点位4'])]) \
                        + '''" onclick="myFunction_''' + str(index + 1) + '''()">'''
                full_text = full_text + '\n' + text1
                text2 = '''<script>
                    function myFunction_''' + str(index + 1) + '''() {
                        document.getElementById("chgtext2").innerHTML = "''' + ' '.join(
                    [str(col['ICD编码']), str(col['ICD名称'])]) + '''",  document.getElementById("chgtext1").innerHTML = 
                    "''' + str(col['术语名称']) + '''" 
                    }
                    </script>'''
                func_text = func_text + text2
                print(func_text)

            components.html(
                """
                    <!DOCTYPE html>
                    <html>
                    <body>
    
                    <p>点击图片，选择对应的骨折类型:</p>
    
                    <img src="data:image/gif;base64,""" + data_url + """" width="500" height="500" alt="Planets" usemap="#planetmap">
    
                    <map name="planetmap"> """ +
                full_text +
                """
                    </map>
                """ +
                func_text +
                """
                    <p id="chgtext1"></p>
                        <div id="chgtext2"></div>
                    </body>
                    </html>
                """,
                height=900,
            )

        bone_pic(bone_pc_dict[(bone, position)])
