# ============================================================
#   ResumeIQ — Smart Resume Analyser
#   Developed by: PAKKI BONISHA SIVANI
#   Description : AI-powered resume analyser with skill
#                 recommendations, course suggestions, and
#                 an admin analytics dashboard.
# ============================================================

import streamlit as st
import nltk
import spacy

nltk.download('stopwords')
spacy.load('en_core_web_sm')

import pandas as pd
import base64
import random
import time
import datetime
import io

from pyresparser import ResumeParser
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer3.converter import TextConverter
from streamlit_tags import st_tags
from PIL import Image
import pymysql
import plotly.express as px
import plotly.graph_objects as go

from Courses import (
    ds_course, web_course, android_course,
    ios_course, uiux_course, resume_videos, interview_videos,
)

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="ResumeIQ · Smart Resume Analyser",
    page_icon="📄",
    layout="wide",
)

# ── Global CSS — modern dark-gradient theme ───────────────────
st.markdown("""
<style>
  /* ---- base ---- */
  html, body, [class*="css"] {
      font-family: 'Segoe UI', sans-serif;
  }
  .main { background: #0f0f1a; color: #e0e0f0; }

  /* ---- hero banner ---- */
  .hero {
      background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
      border-radius: 16px;
      padding: 2.5rem 2rem;
      margin-bottom: 1.5rem;
      border: 1px solid #1e3a5f;
      text-align: center;
  }
  .hero h1 { font-size: 2.6rem; font-weight: 800;
      background: linear-gradient(90deg, #e94560, #0f3460, #533483);
      -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
  .hero p  { color: #a0aec0; font-size: 1.05rem; margin-top: 0.4rem; }

  /* ---- metric cards ---- */
  .metric-card {
      background: linear-gradient(135deg, #1a1a2e, #16213e);
      border: 1px solid #1e3a5f;
      border-radius: 12px;
      padding: 1.2rem 1.4rem;
      text-align: center;
      transition: transform .2s;
  }
  .metric-card:hover { transform: translateY(-3px); }
  .metric-card h3 { font-size: 2rem; font-weight: 700; color: #e94560; margin: 0; }
  .metric-card p  { color: #a0aec0; margin: 0; font-size: .85rem; }

  /* ---- section headings ---- */
  .section-title {
      font-size: 1.3rem; font-weight: 700;
      color: #e94560; margin: 1.5rem 0 .6rem;
      border-left: 4px solid #e94560; padding-left: .6rem;
  }

  /* ---- skill pill ---- */
  .skill-pill {
      display: inline-block;
      background: linear-gradient(135deg, #e94560, #533483);
      color: #fff; border-radius: 20px;
      padding: .25rem .75rem; margin: .2rem;
      font-size: .8rem; font-weight: 600;
  }

  /* ---- tip cards ---- */
  .tip-card {
      border-radius: 10px; padding: .8rem 1rem;
      margin: .4rem 0; font-size: .9rem;
  }
  .tip-pass { background: #0d2b1a; border-left: 4px solid #22c55e; color: #4ade80; }
  .tip-fail { background: #2b1010; border-left: 4px solid #ef4444; color: #fca5a5; }

  /* ── score gauge wrapper ── */
  .score-wrap { text-align: center; padding: 1rem 0; }
  .score-num  { font-size: 3.5rem; font-weight: 800; color: #e94560; }
  .score-lbl  { color: #a0aec0; font-size: .85rem; }

  /* ---- sidebar ---- */
  section[data-testid="stSidebar"] {
      background: #0a0a14 !important;
      border-right: 1px solid #1e3a5f;
  }

  /* ---- upload area ---- */
  [data-testid="stFileUploader"] {
      background: #1a1a2e !important;
      border: 2px dashed #e94560 !important;
      border-radius: 12px !important;
  }

  /* ---- buttons ---- */
  .stButton > button {
      background: linear-gradient(135deg, #e94560, #533483) !important;
      color: #fff !important; border: none !important;
      border-radius: 8px !important; font-weight: 600 !important;
  }

  /* ---- footer ---- */
  .footer {
      text-align: center; color: #4a5568;
      font-size: .8rem; padding: 2rem 0 1rem;
      border-top: 1px solid #1e3a5f; margin-top: 2rem;
  }
  .footer span { color: #e94560; }
</style>
""", unsafe_allow_html=True)


# ── DB helpers ────────────────────────────────────────────────
@st.cache_resource
def get_connection():
    return pymysql.connect(host='localhost', user='root', password='')

connection = get_connection()
cursor = connection.cursor()


def init_db():
    cursor.execute("CREATE DATABASE IF NOT EXISTS ResumeIQ;")
    connection.select_db("resumeiq")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_data (
            ID INT NOT NULL AUTO_INCREMENT,
            Name VARCHAR(100) NOT NULL,
            Email_ID VARCHAR(50) NOT NULL,
            resume_score VARCHAR(8) NOT NULL,
            Timestamp VARCHAR(50) NOT NULL,
            Page_no VARCHAR(5) NOT NULL,
            Predicted_Field VARCHAR(25) NOT NULL,
            User_level VARCHAR(30) NOT NULL,
            Actual_skills VARCHAR(300) NOT NULL,
            Recommended_skills VARCHAR(300) NOT NULL,
            Recommended_courses VARCHAR(600) NOT NULL,
            PRIMARY KEY (ID)
        );
    """)


def insert_data(name, email, res_score, timestamp, no_of_pages,
                reco_field, cand_level, skills, recommended_skills, courses):
    sql = """INSERT INTO user_data VALUES
             (0,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    cursor.execute(sql, (name, email, str(res_score), timestamp,
                         str(no_of_pages), reco_field, cand_level,
                         skills, recommended_skills, courses))
    connection.commit()


# ── Utility helpers ───────────────────────────────────────────
def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
            page_interpreter.process_page(page)
    text = fake_file_handle.getvalue()
    converter.close()
    fake_file_handle.close()
    return text


def show_pdf(file_path):
    with open(file_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = (
        f'<iframe src="data:application/pdf;base64,{b64}" '
        f'width="100%" height="700" type="application/pdf" '
        f'style="border-radius:10px;border:1px solid #1e3a5f;"></iframe>'
    )
    st.markdown(pdf_display, unsafe_allow_html=True)


def get_table_download_link(df, filename, text):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="{filename}" style="color:#e94560;font-weight:600;">{text}</a>'


def course_recommender(course_list):
    st.markdown('<div class="section-title">🎓 Recommended Courses & Certificates</div>', unsafe_allow_html=True)
    no_of_reco = st.slider('Number of course recommendations:', 1, 10, 4, key='course_slider')
    random.shuffle(course_list)
    rec_course = []
    cols = st.columns(2)
    for idx, (c_name, c_link) in enumerate(course_list[:no_of_reco]):
        with cols[idx % 2]:
            st.markdown(
                f'<div class="metric-card" style="text-align:left;padding:.8rem 1rem;">'
                f'<a href="{c_link}" target="_blank" style="color:#e94560;text-decoration:none;font-weight:600;">'
                f'📚 {c_name}</a></div>',
                unsafe_allow_html=True,
            )
        rec_course.append(c_name)
    return rec_course


def level_badge(level):
    colours = {'Fresher': '#3b82f6', 'Intermediate': '#22c55e', 'Experienced': '#f59e0b'}
    colour = colours.get(level, '#a0aec0')
    return (
        f'<span style="background:{colour};color:#fff;padding:.3rem .9rem;'
        f'border-radius:20px;font-weight:700;font-size:.85rem;">{level}</span>'
    )


# ── Score donut chart ─────────────────────────────────────────
def score_gauge(score):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Resume Score", 'font': {'color': '#a0aec0', 'size': 18}},
        number={'font': {'color': '#e94560', 'size': 52}},
        gauge={
            'axis': {'range': [0, 100], 'tickcolor': '#a0aec0'},
            'bar': {'color': '#e94560'},
            'bgcolor': '#1a1a2e',
            'bordercolor': '#1e3a5f',
            'steps': [
                {'range': [0, 40],  'color': '#2b1010'},
                {'range': [40, 70], 'color': '#2b2010'},
                {'range': [70, 100],'color': '#0d2b1a'},
            ],
            'threshold': {'line': {'color': '#e94560', 'width': 4}, 'thickness': .75, 'value': score},
        },
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#a0aec0',
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
    )
    return fig


# ── Main app ──────────────────────────────────────────────────
def run():
    init_db()

    # ── Sidebar ──
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;padding:1rem 0;">
          <div style="font-size:2.5rem;">📄</div>
          <div style="font-weight:800;font-size:1.2rem;color:#e94560;">ResumeIQ</div>
          <div style="color:#a0aec0;font-size:.75rem;">Smart Resume Analyser</div>
        </div>
        <hr style="border-color:#1e3a5f;">
        """, unsafe_allow_html=True)

        mode = st.selectbox("🔐 Select Mode", ["👤 User", "🛡️ Admin"])

        st.markdown("""
        <hr style="border-color:#1e3a5f;">
        <div style="color:#4a5568;font-size:.75rem;text-align:center;">
          Developed by<br>
          <span style="color:#e94560;font-weight:700;">PAKKI BONISHA SIVANI</span>
        </div>
        """, unsafe_allow_html=True)

    # ── Hero ──
    st.markdown("""
    <div class="hero">
      <h1>📄 ResumeIQ</h1>
      <p>Upload your resume and get AI-powered skill recommendations, course suggestions & a personalised score</p>
    </div>
    """, unsafe_allow_html=True)

    # ══════════════════ USER MODE ══════════════════
    if mode == "👤 User":
        st.markdown('<div class="section-title">📤 Upload Your Resume (PDF)</div>', unsafe_allow_html=True)
        pdf_file = st.file_uploader("", type=["pdf"], label_visibility="collapsed")

        if pdf_file is not None:
            save_path = f'./Uploaded_Resumes/{pdf_file.name}'
            with open(save_path, "wb") as f:
                f.write(pdf_file.getbuffer())

            with st.spinner("🔍 Analysing your resume…"):
                resume_data = ResumeParser(save_path).get_extracted_data()
                resume_text = pdf_reader(save_path)

            if not resume_data:
                st.error("⚠️ Could not parse resume. Please ensure it contains readable text.")
                return

            # ── PDF Preview ──
            with st.expander("📄 Resume Preview", expanded=False):
                show_pdf(save_path)

            # ── Basic info ──
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#1a1a2e,#16213e);
                        border:1px solid #1e3a5f;border-radius:12px;padding:1.2rem 1.5rem;margin:.8rem 0;">
              <h3 style="color:#e94560;margin:0 0 .6rem;">👋 Hello, {resume_data.get('name','Candidate')}!</h3>
              <p style="margin:.2rem 0;color:#a0aec0;">📧 {resume_data.get('email','—')}</p>
              <p style="margin:.2rem 0;color:#a0aec0;">📱 {resume_data.get('mobile_number','—')}</p>
              <p style="margin:.2rem 0;color:#a0aec0;">📃 Pages: {resume_data.get('no_of_pages','—')}</p>
            </div>
            """, unsafe_allow_html=True)

            # Candidate level
            pages = resume_data.get('no_of_pages', 1)
            if pages == 1:
                cand_level = "Fresher"
            elif pages == 2:
                cand_level = "Intermediate"
            else:
                cand_level = "Experienced"

            st.markdown(f'<p>Experience Level: {level_badge(cand_level)}</p>', unsafe_allow_html=True)

            # ── Skills ──
            st.markdown('<div class="section-title">💡 Your Skills</div>', unsafe_allow_html=True)
            skills = resume_data.get('skills', [])
            keywords = st_tags(label='', text='Skills detected from your resume',
                               value=skills, key='usr_skills')

            # ── Recommendation logic ──
            ds_kw      = ['tensorflow','keras','pytorch','machine learning','deep learning','flask','streamlit']
            web_kw     = ['react','django','node js','react js','php','laravel','magento','wordpress','javascript','angular js','c#','flask']
            android_kw = ['android','android development','flutter','kotlin','xml','kivy']
            ios_kw     = ['ios','ios development','swift','cocoa','cocoa touch','xcode']
            uiux_kw    = ['ux','adobe xd','figma','zeplin','balsamiq','ui','prototyping','wireframes',
                          'storyframes','adobe photoshop','photoshop','editing','adobe illustrator',
                          'illustrator','adobe after effects','after effects','adobe premier pro',
                          'premier pro','adobe indesign','indesign','wireframe','solid','grasp',
                          'user research','user experience']

            reco_field = ''
            recommended_skills = []
            rec_course = ''

            field_map = {
                'Data Science':      (ds_kw,      ds_course,
                                      ['Data Visualization','Predictive Analysis','Statistical Modeling',
                                       'Data Mining','Clustering & Classification','Data Analytics',
                                       'Quantitative Analysis','Web Scraping','ML Algorithms','Keras',
                                       'Pytorch','Probability','Scikit-learn','Tensorflow','Flask','Streamlit']),
                'Web Development':   (web_kw,     web_course,
                                      ['React','Django','Node JS','React JS','PHP','Laravel','Magento',
                                       'WordPress','JavaScript','Angular JS','C#','Flask','SDK']),
                'Android Dev':       (android_kw, android_course,
                                      ['Android','Android Development','Flutter','Kotlin','XML','Java',
                                       'Kivy','GIT','SDK','SQLite']),
                'iOS Development':   (ios_kw,     ios_course,
                                      ['iOS','Swift','Cocoa','Cocoa Touch','Xcode','Objective-C',
                                       'SQLite','Plist','StoreKit','UI-Kit','AV Foundation','Auto-Layout']),
                'UI/UX Design':      (uiux_kw,    uiux_course,
                                      ['UI','User Experience','Adobe XD','Figma','Zeplin','Balsamiq',
                                       'Prototyping','Wireframes','Adobe Photoshop','Illustrator',
                                       'After Effects','Premier Pro','Indesign','User Research']),
            }

            for field, (kw_list, course_list, reco) in field_map.items():
                if any(s.lower() in kw_list for s in skills):
                    reco_field = field
                    recommended_skills = reco
                    st.success(f"🎯 Our analysis suggests you are targeting **{field}** roles.")
                    st.markdown('<div class="section-title">⭐ Recommended Skills to Add</div>', unsafe_allow_html=True)
                    st_tags(label='', text='Add these to boost your resume',
                            value=recommended_skills, key='reco_skills')
                    st.info("💡 Adding these skills will significantly improve your chances of landing the job!")
                    rec_course = course_recommender(course_list)
                    break

            if not reco_field:
                st.warning("🔍 Could not detect a specific domain. Try adding more technical skills to your resume.")

            # ── Resume Tips ──
            st.markdown('<div class="section-title">📝 Resume Writing Tips</div>', unsafe_allow_html=True)
            resume_score = 0
            checks = [
                ('Objective',    'Career Objective',    'Add a career objective to show your intent to recruiters.'),
                ('Declaration',  'Declaration',         'Add a declaration to assure recruiters everything is authentic.'),
                ('Hobbies',      'Hobbies / Interests', 'Add hobbies to show your personality and cultural fit.'),
                ('Achievements', 'Achievements',        'Add achievements to prove your capability for the role.'),
                ('Projects',     'Projects',            'Add projects to demonstrate hands-on experience.'),
            ]
            for keyword, label, advice in checks:
                if keyword in resume_text:
                    resume_score += 20
                    st.markdown(f'<div class="tip-card tip-pass">✅ <b>{label}</b> — Great, found in your resume!</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="tip-card tip-fail">❌ <b>{label}</b> — {advice}</div>', unsafe_allow_html=True)

            # ── Score gauge ──
            st.markdown('<div class="section-title">📊 Resume Score</div>', unsafe_allow_html=True)
            col_g, col_msg = st.columns([1, 1])
            with col_g:
                st.plotly_chart(score_gauge(resume_score), use_container_width=True)
            with col_msg:
                st.markdown('<br><br>', unsafe_allow_html=True)
                if resume_score >= 80:
                    st.success(f"🏆 Excellent! Your score is **{resume_score}/100**. Your resume is well-structured.")
                elif resume_score >= 60:
                    st.warning(f"📈 Good effort! Score: **{resume_score}/100**. A few more additions will make it stronger.")
                elif resume_score >= 40:
                    st.warning(f"🔧 Score: **{resume_score}/100**. There's room for improvement — follow the tips above.")
                else:
                    st.error(f"⚠️ Score: **{resume_score}/100**. Please add the missing sections to improve your resume.")
                st.markdown(f'<p style="color:#a0aec0;font-size:.85rem;">Score is based on the presence of key sections: Objective, Declaration, Hobbies, Achievements, and Projects.</p>', unsafe_allow_html=True)

            st.balloons()

            # ── DB insert ──
            ts        = time.time()
            timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H:%M:%S')
            try:
                insert_data(
                    resume_data.get('name',''),
                    resume_data.get('email',''),
                    str(resume_score), timestamp,
                    str(pages), reco_field, cand_level,
                    str(skills), str(recommended_skills), str(rec_course),
                )
            except Exception:
                pass   # DB optional in demo; don't crash the app

            # ── Bonus videos ──
            st.markdown('<div class="section-title">🎬 Bonus: Resume Writing Tips (Video)</div>', unsafe_allow_html=True)
            st.video(random.choice(resume_videos))

            st.markdown('<div class="section-title">🎬 Bonus: Interview Preparation (Video)</div>', unsafe_allow_html=True)
            st.video(random.choice(interview_videos))

    # ══════════════════ ADMIN MODE ══════════════════
    else:
        st.markdown('<div class="section-title">🛡️ Admin Login</div>', unsafe_allow_html=True)

        col_u, col_p, col_b = st.columns([2, 2, 1])
        with col_u:
            ad_user = st.text_input("Username", placeholder="Enter username")
        with col_p:
            ad_password = st.text_input("Password", type='password', placeholder="Enter password")
        with col_b:
            st.markdown('<br>', unsafe_allow_html=True)
            login_btn = st.button("🔓 Login")

        if login_btn:
            # Default credentials — change for production
            if ad_user == 'sivani_admin' and ad_password == 'resumeiq2024':
                st.success("✅ Welcome, Sivani! Admin dashboard loaded.")

                try:
                    cursor.execute("SELECT * FROM user_data")
                    data = cursor.fetchall()
                except Exception:
                    st.warning("⚠️ No data yet — database is empty or not connected.")
                    return

                df = pd.DataFrame(data, columns=[
                    'ID', 'Name', 'Email', 'Resume Score', 'Timestamp',
                    'Total Pages', 'Predicted Field', 'User Level',
                    'Actual Skills', 'Recommended Skills', 'Recommended Course'
                ])

                # KPI row
                total = len(df)
                avg_score = round(df['Resume Score'].astype(float).mean(), 1) if total else 0
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f'<div class="metric-card"><h3>{total}</h3><p>Total Resumes Analysed</p></div>', unsafe_allow_html=True)
                with col2:
                    st.markdown(f'<div class="metric-card"><h3>{avg_score}</h3><p>Average Resume Score</p></div>', unsafe_allow_html=True)
                with col3:
                    fields = df['Predicted Field'].value_counts()
                    top_field = fields.index[0] if len(fields) else "—"
                    st.markdown(f'<div class="metric-card"><h3 style="font-size:1.2rem;">{top_field}</h3><p>Most Common Field</p></div>', unsafe_allow_html=True)

                st.markdown('<div class="section-title">📋 All User Data</div>', unsafe_allow_html=True)
                st.dataframe(df, use_container_width=True)
                st.markdown(get_table_download_link(df, 'ResumeIQ_Report.csv', '⬇️ Download CSV Report'),
                            unsafe_allow_html=True)

                # Charts
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    st.markdown('<div class="section-title">📈 Predicted Field Distribution</div>', unsafe_allow_html=True)
                    fig1 = px.pie(df, names='Predicted Field',
                                  title='Candidate Field Distribution',
                                  color_discrete_sequence=px.colors.sequential.RdBu)
                    fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#a0aec0')
                    st.plotly_chart(fig1, use_container_width=True)

                with col_c2:
                    st.markdown('<div class="section-title">📈 Experience Level Distribution</div>', unsafe_allow_html=True)
                    fig2 = px.pie(df, names='User Level',
                                  title='User Experience Level Distribution',
                                  color_discrete_sequence=['#e94560','#533483','#0f3460'])
                    fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#a0aec0')
                    st.plotly_chart(fig2, use_container_width=True)

                # Score histogram
                st.markdown('<div class="section-title">📊 Resume Score Distribution</div>', unsafe_allow_html=True)
                fig3 = px.histogram(df, x='Resume Score', nbins=10,
                                    color_discrete_sequence=['#e94560'],
                                    title='Resume Score Histogram')
                fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#a0aec0',
                                   plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig3, use_container_width=True)

            else:
                st.error("❌ Invalid credentials. Please try again.")

    # ── Footer ──
    st.markdown("""
    <div class="footer">
      Built with ❤️ by <span>PAKKI BONISHA SIVANI</span> &nbsp;|&nbsp;
      ResumeIQ — Smart Resume Analyser &nbsp;|&nbsp;
      Powered by Python · Streamlit · NLP
    </div>
    """, unsafe_allow_html=True)


run()
