import streamlit as st


def show_sidebar():
    with st.sidebar:
        st.markdown("### ℹ️ About This Assistant")
        st.write(
            "This tool provides information on registration of **births, marriages, and deaths in Sri Lanka**."
        )
        st.markdown("**Purpose:** Quick, AI-assisted access to procedures and requirements.")
        st.markdown("**Data Source:** [Registrar General's Department (RGD)](https://www.rgd.gov.lk)")
        st.markdown(
            "**Disclaimer:** This is an unofficial assistant. For official information, contact RGD directly."
        )

        st.markdown("---")
        st.markdown("### 📞 RGD Contact Information")
        st.markdown("""
        **Address:**
        Registrar General’s Department
        No. 234/A3, Denzil Kobbekaduwa Mawatha,
        Battaramulla, Sri Lanka

        **Phone:** +94 112 039 039
        **Fax:** +94 112 039 036
        **Email:** info@rgd.gov.lk
        **Website:** [www.rgd.gov.lk](https://www.rgd.gov.lk)
        """)


def select_language():
    language = st.radio(
        "",
        ("English", "தமிழ்", "සිංහල"),
        horizontal=True
    )

    placeholder = "Ask your question"
    title = "Civil Registration Assistant - Srilanka"

    if language == "සිංහල":
        placeholder = "ඔබේ ප්‍රශ්නය අසන්න"
        title = "සිවිල් ලියාපදිංචි සහකාර - ශ්‍රී ලංකාව"
    elif language == "தமிழ்":
        placeholder = "உங்கள் கேள்வியைக் கேளுங்கள்"
        title = "சிவில் பதிவு உதவியாளர் - இலங்கை"

    return language, placeholder, title


def show_title(title):
    st.markdown(f"""<h1 style='font-size: 25px; text-align: center'>{title}</h1>""", unsafe_allow_html=True)
