# 📄 ResumeIQ — Smart Resume Analyser

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/Streamlit-1.32-red?style=for-the-badge&logo=streamlit" />
  <img src="https://img.shields.io/badge/NLP-spaCy-green?style=for-the-badge" />
  <img src="https://img.shields.io/badge/ML-PyResparser-orange?style=for-the-badge" />
</p>

> **Developed by:** PAKKI BONISHA SIVANI  
> An AI-powered web application that analyses resumes, recommends skills, suggests courses, and scores your resume — all in a modern, interactive UI.

---

## 🚀 Features

| Feature | Description |
|---|---|
| 📤 **Resume Upload** | Upload PDF resumes and get instant analysis |
| 🧠 **AI Skill Detection** | NLP-powered extraction of skills from resume text |
| 🎯 **Domain Prediction** | Detects target field: Data Science, Web Dev, Android, iOS, UI/UX |
| 💡 **Skill Recommendations** | Suggests missing in-demand skills to add |
| 🎓 **Course Recommendations** | Curated courses from Udemy, Coursera, Udacity & more |
| 📊 **Resume Score Gauge** | Interactive Plotly gauge showing resume quality score (0–100) |
| 📝 **Writing Tips** | Section-by-section tips (Objective, Projects, Achievements…) |
| 🎬 **Video Recommendations** | YouTube resume & interview prep videos |
| 🛡️ **Admin Dashboard** | Analytics with charts, user data table, and CSV export |

---

## 🖥️ Tech Stack

- **Frontend / UI:** Streamlit with custom CSS theming
- **NLP / Parsing:** spaCy, NLTK, PyResparser, PDFMiner3
- **Charts:** Plotly Express & Graph Objects
- **Database:** MySQL (via PyMySQL)
- **Language:** Python 3.9+

---

## ⚙️ Setup & Installation

### 1. Clone this repository
```bash
git clone https://github.com/YOUR_USERNAME/ResumeIQ.git
cd ResumeIQ
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 3. Set up MySQL
- Install [XAMPP](https://www.apachefriends.org/) or any MySQL server
- Start Apache & MySQL services
- The app will auto-create the database and table on first run

### 4. Run the app
```bash
streamlit run App.py
```

---

## 🔐 Admin Login
- **Username:** `sivani_admin`
- **Password:** `resumeiq2024`

---

## 📁 Project Structure

```
ResumeIQ/
├── App.py               # Main Streamlit application
├── Courses.py           # Course & video recommendation data
├── requirements.txt     # Python dependencies
├── Uploaded_Resumes/    # Stores user-uploaded resume PDFs
└── README.md
```

---

## 📸 Screenshots

### User Side — Resume Analysis
> Modern dark-themed UI with score gauge, skill pills, and course cards

### Admin Side — Analytics Dashboard
> KPI cards, pie charts for field & experience distribution, score histogram, and downloadable CSV

---

## 🌟 Key Improvements Over Base Version

- ✅ Complete UI redesign with dark gradient theme
- ✅ Interactive Plotly gauge for resume score (vs plain progress bar)
- ✅ Card-based course recommendations (vs plain links)
- ✅ Admin KPI dashboard with 3 analytics charts
- ✅ Colour-coded tip cards for resume writing suggestions
- ✅ Experience level badges
- ✅ Responsive 2-column layout throughout
- ✅ Cleaner, modular code structure

---

## 🙋‍♀️ About the Developer

**PAKKI BONISHA SIVANI**  
B.Tech Computer Science & Engineering  
Passionate about building intelligent web applications using Python, NLP, and Machine Learning.

---

*⭐ If you found this project useful, please star the repository!*
