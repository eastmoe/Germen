import streamlit as st

# 初始化状态变量
if 'coords' not in st.session_state:
    st.session_state.coords = None

# 上传图片
uploaded_file = st.file_uploader("上传一张图片", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # 读取图片并显示
    img_url = f"data:image/jpeg;base64,{uploaded_file.getvalue().hex()}"

    # 嵌入HTML和JavaScript
    st.markdown(f"""
    <style>
    #image-container {{
        position: relative;
        display: inline-block;
    }}
    #selection-box {{
        position: absolute;
        border: 2px dashed red;
        display: none;
    }}
    </style>
    <div id="image-container">
        <img id="image" src="{img_url}" width="600">
        <div id="selection-box"></div>
    </div>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script>
    $(document).ready(function() {{
        var startX, startY, endX, endY;
        var isSelecting = false;

        $('#image').mousedown(function(e) {{
            startX = e.pageX - $(this).offset().left;
            startY = e.pageY - $(this).offset().top;
            isSelecting = true;
            $('#selection-box').css({{
                'left': startX,
                'top': startY,
                'width': 0,
                'height': 0
            }}).show();
        }});

        $('#image').mousemove(function(e) {{
            if (isSelecting) {{
                endX = e.pageX - $(this).offset().left;
                endY = e.pageY - $(this).offset().top;
                $('#selection-box').css({{
                    'left': Math.min(startX, endX),
                    'top': Math.min(startY, endY),
                    'width': Math.abs(endX - startX),
                    'height': Math.abs(endY - startY)
                }});
            }});
        }});

        $('#image').mouseup(function(e) {{
            if (isSelecting) {{
                isSelecting = false;
                endX = e.pageX - $(this).offset().left;
                endY = e.pageY - $(this).offset().top;
                var coords = {{
                    startX: startX,
                    startY: startY,
                    endX: endX,
                    endY: endY
                }};
                Streamlit.setComponentValue(coords);
            }});
        }});
    }});
    </script>
    """, unsafe_allow_html=True)

    # 获取JavaScript返回的坐标
    coords = st.session_state.get('coords', None)
    if coords:
        st.write(f"框选的起始坐标: ({coords['startX']}, {coords['startY']})")
        st.write(f"框选的结束坐标: ({coords['endX']}, {coords['endY']})")

# 初始化Streamlit组件
st.components.v1.html("", height=0)