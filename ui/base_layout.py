import streamlit as st


def style_background_home():

    st.markdown('''
                    <style>
                        .stApp{
                            background:
                                radial-gradient(circle at 15% 10%, rgba(255,255,255,0.18) 0, transparent 40%),
                                radial-gradient(circle at 85% 90%, rgba(235,69,158,0.35) 0, transparent 45%),
                                linear-gradient(160deg, #5865F2 0%, #6E5BF0 55%, #9B4FD8 100%) !important;
                        }
                    </style>
                ''', unsafe_allow_html=True
                )


def style_base_layout():

    st.markdown('''
                    <style>
                        @import url('https://fonts.googleapis.com/css2?family=Climate+Crisis&family=Outfit:wght@300..800&display=swap');

                        :root{
                            --sc-primary: #5865F2;
                            --sc-primary-dark: #4752C4;
                            --sc-pink: #EB459E;
                            --sc-ink: #1E293B;
                            --sc-muted: #64748B;
                            --sc-line: #E2E8F0;
                            --sc-soft: #EEF0FF;
                            --sc-shadow: 0 10px 30px rgba(30, 41, 59, 0.08);
                        }

                        /* Hide Streamlit chrome */
                        #MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"]{
                            display: none !important;
                        }
                        header[data-testid="stHeader"]{
                            background: transparent !important;
                        }

                        .block-container{
                            padding-top: 2rem !important;
                            padding-bottom: 3rem !important;
                            max-width: 1000px !important;
                        }

                        /* Typography (never target span: it breaks Material icons) */
                        .stApp, .stApp p, .stApp label, .stApp li,
                        .stApp input, .stApp textarea, .stApp button{
                            font-family: 'Outfit', sans-serif !important;
                        }
                        .stApp h1, .stApp h2, .stApp h3, .stApp h4{
                            font-family: 'Outfit', sans-serif !important;
                            font-weight: 700 !important;
                            letter-spacing: -0.02em;
                            color: var(--sc-ink) !important;
                        }

                        /* Buttons */
                        .stButton > button, [data-testid="stFormSubmitButton"] > button,
                        [data-testid="stPopover"] button{
                            border-radius: 999px !important;
                            padding: 0.55rem 1.25rem !important;
                            font-weight: 600 !important;
                            transition: transform .15s ease, box-shadow .15s ease, background .15s ease, color .15s ease !important;
                        }
                        button[data-testid="stBaseButton-primary"],
                        button[data-testid="stBaseButton-primaryFormSubmit"]{
                            background: linear-gradient(135deg, #5865F2, #7C86F7) !important;
                            color: #fff !important;
                            border: none !important;
                            box-shadow: 0 6px 16px rgba(88, 101, 242, 0.30) !important;
                        }
                        button[data-testid="stBaseButton-primary"]:hover:not(:disabled),
                        button[data-testid="stBaseButton-primaryFormSubmit"]:hover:not(:disabled){
                            transform: translateY(-1px);
                            box-shadow: 0 10px 22px rgba(88, 101, 242, 0.38) !important;
                        }
                        button[data-testid="stBaseButton-secondary"],
                        button[data-testid="stBaseButton-secondaryFormSubmit"]{
                            background: #fff !important;
                            color: var(--sc-ink) !important;
                            border: 1px solid var(--sc-line) !important;
                        }
                        button[data-testid="stBaseButton-secondary"]:hover:not(:disabled){
                            border-color: var(--sc-primary) !important;
                            color: var(--sc-primary) !important;
                        }
                        button[data-testid="stBaseButton-tertiary"]{
                            color: var(--sc-muted) !important;
                        }
                        button[data-testid="stBaseButton-tertiary"]:hover:not(:disabled){
                            color: var(--sc-pink) !important;
                        }
                        .stApp button:disabled{
                            opacity: 0.5 !important;
                            box-shadow: none !important;
                        }

                        /* Inputs */
                        [data-baseweb="input"], [data-baseweb="select"] > div{
                            border-radius: 12px !important;
                            background: #fff !important;
                        }
                        [data-testid="stTextInput"] input::placeholder{
                            color: #94A3B8 !important;
                            opacity: 1 !important;
                        }

                        /* Cards: containers created with key="card_..." */
                        [class*="st-key-card"]{
                            background: #fff;
                            border: 1px solid var(--sc-line);
                            border-radius: 20px;
                            padding: 1.5rem;
                            box-shadow: var(--sc-shadow);
                        }

                        /* Landing portal cards */
                        [class*="st-key-portal"]{
                            background: rgba(255, 255, 255, 0.96);
                            border-radius: 28px;
                            padding: 2rem 1.75rem;
                            box-shadow: 0 20px 45px rgba(20, 16, 70, 0.25);
                            transition: transform .2s ease;
                        }
                        [class*="st-key-portal"]:hover{
                            transform: translateY(-4px);
                        }

                        /* Metric tiles */
                        [data-testid="stMetric"]{
                            background: #fff;
                            border: 1px solid var(--sc-line);
                            border-radius: 18px;
                            padding: 1rem 1.25rem;
                            box-shadow: var(--sc-shadow);
                        }
                        [data-testid="stMetricValue"]{
                            color: var(--sc-primary) !important;
                            font-weight: 700 !important;
                        }

                        /* Dialogs, tables, camera */
                        div[role="dialog"]{
                            border-radius: 24px !important;
                        }
                        [data-testid="stDataFrame"], [data-testid="stCameraInput"] video,
                        [data-testid="stCameraInput"] img, [data-testid="stImage"] img{
                            border-radius: 16px !important;
                        }

                        /* Brand */
                        .sc-logo-container{
                            display: flex;
                            flex-direction: column;
                            align-items: center;
                            margin: 1rem 0 2.5rem;
                            text-align: center;
                        }
                        .sc-logo{
                            font-family: 'Climate Crisis', sans-serif !important;
                            font-size: 3.4rem;
                            line-height: 0.9;
                            color: #fff;
                            margin: 0.5rem 0 0;
                        }
                        .sc-tagline{
                            color: rgba(255, 255, 255, 0.88);
                            font-size: 1.15rem;
                            margin-top: 1rem;
                        }
                        .sc-brand{
                            display: flex;
                            align-items: center;
                            gap: 10px;
                        }
                        .sc-brand-name{
                            font-family: 'Climate Crisis', sans-serif !important;
                            font-size: 1.45rem;
                            line-height: 0.95;
                            color: var(--sc-primary);
                        }

                        /* Shared HTML pieces */
                        .sc-portal{ text-align: center; }
                        .sc-portal img{ height: 120px; margin-bottom: 0.75rem; }
                        .sc-portal h3{ margin: 0 0 0.35rem; font-size: 1.5rem; }
                        .sc-portal p{ color: var(--sc-muted); margin: 0 0 1rem; }
                        .sc-chips{
                            display: flex;
                            gap: 10px;
                            flex-wrap: wrap;
                            justify-content: center;
                            margin-top: 2rem;
                        }
                        .sc-chip{
                            background: rgba(255, 255, 255, 0.16);
                            border: 1px solid rgba(255, 255, 255, 0.3);
                            color: #fff;
                            padding: 6px 14px;
                            border-radius: 999px;
                            font-size: 0.95rem;
                        }
                        .sc-auth-head{ text-align: center; margin-bottom: 0.5rem; }
                        .sc-auth-head h2{ margin: 0; font-size: 1.75rem; }
                        .sc-auth-head p{ color: var(--sc-muted); margin: 0.35rem 0 0; }
                        .sc-greeting{ color: var(--sc-muted); margin: 0; }
                        .sc-greeting b{ color: var(--sc-ink); }
                        .sc-empty{
                            text-align: center;
                            padding: 2.5rem 1rem;
                            color: var(--sc-muted);
                        }
                        .sc-empty h4{ margin: 0 0 0.35rem; }
                    </style>
                ''', unsafe_allow_html=True
                )


def style_background_dashboard():

    st.markdown('''
                    <style>
                        .stApp{
                            background:
                                radial-gradient(circle at 100% 0%, rgba(88,101,242,0.10) 0, transparent 35%),
                                #F5F6FF !important;
                        }
                    </style>
                ''', unsafe_allow_html=True
                )
