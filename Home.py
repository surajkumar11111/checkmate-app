import streamlit as st
from streamlit_option_menu import option_menu
from utils.constants import *
from streamlit_tailwind import st_tw
from streamlit_lottie import st_lottie # type: ignore
import json
import streamlit.components.v1 as components
from streamlit_javascript import st_javascript

st.set_page_config(page_title='Checkmate', layout="wide", initial_sidebar_state="auto", page_icon='')

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("styles/styles_main.css")

# get screen width dynamically using JavaScript
screen_width = st_javascript("window.innerWidth")

# store width in session state (default: 1200px for first load)
if screen_width:
    st.session_state["viewport_width"] = int(screen_width)
elif "viewport_width" not in st.session_state:
    st.session_state["viewport_width"] = 1200  # default 

hide_animations = st.session_state["viewport_width"] <= 480

with st.sidebar:
    st.title("How CheckMate Works")
    with st.expander("Click here to know"):
        st.info(
            """
            -  **Step 1:** Upload your cheque
            -  **Step 2:** GEMINI extracts details
            -  **Step 3:** View structured cheque data
            -  **Step 4:** Analyze via Dashboard
            -  **Step 5:** Export results (CSV, Excel, PDF, and more.)
            """
        )
    st.caption("© CheckMate. All rights reserved.")

def hero(content1, content2):
    st.markdown(
        f'<h1 style="text-align:center;font-size:60px;border-radius:2%;">'
        f'<span>{content1}</span><br>'
        f'<span style="color:black;font-size:22px;">{content2}</span></h1>',
        unsafe_allow_html=True
    )

with st.container():
    col1, col2 = st.columns([8, 3])

    with col1:
        st.header("CheckMate")
        st.subheader("Automated Bank Check Processor")
        st.write(info['About'])

        from streamlit_extras.switch_page_button import switch_page
        col_1, col_2, temp = st.columns([0.35, 0.2, 0.45])
        with col_1:
            btn1 = st.button("Get Started")
            if btn1:
                switch_page("Upload")
        with col_2:
            btn2 = st.button("Dashboard")
            if btn2:
                switch_page("Dashboard")


    def change_button_color(widget_label, background_color='transparent'):
        htmlstr = f"""
            <script>
                var elements = window.parent.document.querySelectorAll('button');
                for (var i = 0; i < elements.length; ++i) {{ 
                    if (elements[i].innerText == '{widget_label}') {{ 
                    elements[i].style.background = '{background_color}'
                    }}
                }}
            </script>
            """
        components.html(f"{htmlstr}", height=0, width=0)

    change_button_color('Get Started', '#0cc789')


    with col2:
        if not hide_animations:
            def load_lottiefile(filepath: str):
                with open(filepath, "r") as f:
                    return json.load(f)
            
            first_anim_lottie = load_lottiefile("images/Animation.json")
            st_lottie(
                first_anim_lottie,
                speed=1,
                loop=True,
                quality="low",
                height=None,
                width=250,
                key="first"
            )

st.write("---")
st.subheader('🚀 Features')

cols = st.columns(3)  
for i, feature in enumerate(FEATURES):
    with cols[i % 3]:
        st_tw(
            text=f"""
            <div class="bg-white p-6 shadow-lg rounded-lg flex flex-col justify-between h-48">
                <div class="text-4xl text-center">{feature['icon']}</div>
                <h3 class="text-lg font-bold text-center">{feature['title']}</h3>
                <p class="text-sm text-center">{feature['description']}</p>
            </div>
            """,
            height=200
        )

st.write("---")

if st.session_state["viewport_width"] > 480:
    col1, col2 = st.columns(2)
    col1, col2 = st.columns(2)

    with col1:
        email_anim_lottie = load_lottiefile("images/email.json")
        st_lottie(
            email_anim_lottie,
            speed=1,
            loop=True,
            quality="low",
            height=None,
            width=470 if st.session_state["viewport_width"] > 1024 else 350,
            key="email_anim"
        )

    with col2:
        st.subheader("📨 Contact Me")
        email = "e5137e4a06ff277dd5bf7c7fa0c088ed"
        st_tw(
            text=f"""
            <div class="bg-white p-6 shadow-lg rounded-lg">
                <form action="https://formsubmit.co/{email}" method="POST">
                    <input type="hidden" name="_captcha" value="false">
                    <input class="w-full p-2 border rounded mb-2" type="text" name="name" placeholder="Your name" required>
                    <input class="w-full p-2 border rounded mb-2" type="email" name="email" placeholder="Your email" required>
                    <textarea class="w-full p-2 border rounded mb-2" name="message" placeholder="Your message here" required></textarea>
                    <button id="submit-btn" 
                    class="w-auto bg-[#0cc789] text-black text-sm rounded-md px-3 py-1.5 transition duration-300 hover:bg-[#D1D5DB]">
                    Submit
                </button>
                </form>
            </div>
            """,
            height=250
        )
else:
    st.subheader("📨 Contact Me")
    email = "e5137e4a06ff277dd5bf7c7fa0c088ed"
    st_tw(
        text=f"""
        <div class="bg-white p-6 shadow-lg rounded-lg">
            <form action="https://formsubmit.co/{email}" method="POST">
                <input type="hidden" name="_captcha" value="false">
                <input class="w-full p-2 border rounded mb-2" type="text" name="name" placeholder="Your name" required>
                <input class="w-full p-2 border rounded mb-2" type="email" name="email" placeholder="Your email" required>
                <textarea class="w-full p-2 border rounded mb-2" name="message" placeholder="Your message here" required></textarea>
                <button id="submit-btn" 
                    class="w-auto bg-[#0cc789] text-black text-sm rounded-md px-3 py-1.5 transition duration-300 hover:bg-[#D1D5DB]">
                    Submit
                </button>
            </form>
        </div>
        """,
        height=250
    )
