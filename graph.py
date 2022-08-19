import streamlit as st
import pandas as pd
from Widget import modal
from Widget.Hydralit import HydraHeadApp
import base64
from PIL import Image
import streamlit.components.v1 as components

pic_dict_sample = {}

class graphyApp(HydraHeadApp):
    def run(self):

        pic_name = '11ABC'
        file_ = open(f"picture/肱骨/{pic_name}.png", "rb")
        contents = file_.read()
        data_url = base64.b64encode(contents).decode("utf-8")
        file_.close()
        # "data:image/gif;base64,""" + data_url + """"


        # bootstrap 4 collapse example
        components.html(
            """
                <!DOCTYPE html>
                <html>
                <body>

                <p>点击图片，选择对应的骨折类型:</p>
                 <div id="chgtext"></div>

                <img src="data:image/gif;base64,""" + data_url + """" width="500" height="500" alt="Planets" usemap="#planetmap">

                <map name="planetmap">
                  <area shape="rect" coords="15,15,150,150" alt="Sun" onclick="myFunction_1()">
                  <area shape="rect" coords="180,11,290,150" alt="Mercury" onclick="myFunction_2()">
                  <area shape="rect" coords="348,13,457,156" alt="Venus" onclick="myFunction_3()">
                  <area shape="rect" coords="34,174,142,320" alt="Sun" onclick="myFunction_4()">
                  <area shape="rect" coords="171,178,285,325" alt="Mercury" onclick="myFunction_5()">
                  <area shape="rect" coords="335,186,447,325" alt="Venus" onclick="myFunction_6()">
                  <area shape="rect" coords="29,346,145,485" alt="Sun" onclick="myFunction_7()">
                  <area shape="rect" coords="171,346,285,485" alt="Mercury" onclick="myFunction_8()">
                  <area shape="rect" coords="355,346,447,485" alt="Venus" onclick="myFunction_9()">
                </map>

                <script>
                function myFunction_1() {
                    document.getElementById("chgtext").innerHTML = "S42.200x041	肱骨大结节骨折"
                }
                </script>

                <script>
                function myFunction_2() {
                    document.getElementById("chgtext").innerHTML = "S42.200x091	肱骨小结节骨折"
                }
                </script>

                            <script>
                function myFunction_3() {
                    document.getElementById("chgtext").innerHTML = "S42.202	肱骨外科颈骨折"
                }
                </script>

                <script>
                function myFunction_4() {
                    document.getElementById("chgtext").innerHTML = "S42.200x031	肱骨解剖颈骨折"
                }
                </script>
                
                <script>
                function myFunction_5() {
                    document.getElementById("chgtext").innerHTML = "S42.200x092	肱骨近端多发性骨折"
                }
                </script>
                
                <script>
                function myFunction_6() {
                    document.getElementById("chgtext").innerHTML = "S42.200x031	肱骨解剖颈骨折"
                }
                </script>
                
                <script>
                function myFunction_7() {
                    document.getElementById("chgtext").innerHTML = "S42.200x093	肱骨近端多发性骨折"
                }
                </script>
                
                <script>
                function myFunction_8() {
                    document.getElementById("chgtext").innerHTML = "S42.200x093	肱骨近端多发性骨折"
                }
                </script>
                
                <script>
                function myFunction_9() {
                    document.getElementById("chgtext").innerHTML = "S42.200x093	肱骨近端多发性骨折"
                }
                </script>
                </body>
                </html>
            """,
            height=900,
        )




