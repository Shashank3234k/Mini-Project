import streamlit as st
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
from pathlib import Path
from io import BytesIO
import datetime

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ModuleNotFoundError:
    REPORTLAB_AVAILABLE = False

# Ensure project root is on sys.path so sibling package `chatbot` can be imported
THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from chatbot.data_loader import DiseaseDataLoader
from chatbot.chatbot_engine import OfflineHealthChatbot

def generate_pdf(disease, confidence, risk, health_score, top3_predictions, disease_clean, disease_data, latest_chatbot_response=None):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=40, leftMargin=40,
                            topMargin=40, bottomMargin=40)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=colors.HexColor('#1b4332'),
        spaceAfter=15
    )
    h2_style = ParagraphStyle(
        'DocH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        textColor=colors.HexColor('#2d6a4f'),
        spaceBefore=10,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#2b2b2b'),
        spaceAfter=5
    )
    disclaimer_style = ParagraphStyle(
        'DocDisclaimer',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#a8201a'),
        spaceBefore=15,
        spaceAfter=6
    )
    
    story.append(Paragraph("AI Disease Prediction Report", title_style))
    
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    story.append(Paragraph(f"<b>Date & Time:</b> {current_time}", body_style))
    story.append(Spacer(1, 10))
    
    table_data = [
        [Paragraph("<b>Predicted Disease:</b>", body_style), Paragraph(disease, body_style)],
        [Paragraph("<b>Confidence Score:</b>", body_style), Paragraph(f"{confidence:.2f}%", body_style)],
        [Paragraph("<b>Risk Level:</b>", body_style), Paragraph(risk, body_style)],
        [Paragraph("<b>Health Risk Score:</b>", body_style), Paragraph(f"{health_score} / 100", body_style)]
    ]
    t = Table(table_data, colWidths=[150, 350])
    t.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#2b2b2b')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#dddddd')),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("🏆 Top 3 Disease Predictions", h2_style))
    for i, (name, p) in enumerate(top3_predictions, 1):
        story.append(Paragraph(f"{i}. {name} — {p:.1f}%", body_style))
    story.append(Spacer(1, 10))
    
    try:
        fig, ax = plt.subplots(figsize=(3, 2))
        top3_names = [name for name, p in top3_predictions]
        top3_probs = [p for name, p in top3_predictions]
        wedges, texts, autotexts = ax.pie(
            top3_probs,
            labels=top3_names,
            autopct='%1.1f%%',
            startangle=90,
            colors=['#FF6B6B', '#4D96FF', '#6BCB77'],
            wedgeprops=dict(width=0.4, edgecolor='white', linewidth=1.5)
        )
        plt.setp(texts, size=7, weight="bold")
        plt.setp(autotexts, size=6, color="white", weight="bold")
        fig.patch.set_alpha(0.0)
        ax.patch.set_alpha(0.0)
        ax.axis('equal')
        plt.tight_layout()
        
        img_buf = BytesIO()
        fig.savefig(img_buf, format='png', bbox_inches='tight', dpi=150)
        img_buf.seek(0)
        plt.close(fig)
        
        img_flowable = Image(img_buf, width=150, height=100)
        story.append(Paragraph("📊 Disease Probability Distribution", h2_style))
        story.append(img_flowable)
        story.append(Spacer(1, 10))
    except Exception as e:
        pass

    story.append(Paragraph("🛡️ Precautions", h2_style))
    precautions = disease_data.get("precautions", [])
    if precautions:
        for p in precautions:
            story.append(Paragraph(f"• {p}", body_style))
    else:
        local_precs = disease_info.get(disease_clean, [])
        if local_precs:
            for p in local_precs:
                story.append(Paragraph(f"• {p}", body_style))
        else:
            story.append(Paragraph("No specific precautions available.", body_style))
            
    story.append(Paragraph("<b>General Care:</b>", body_style))
    for g in general_precautions:
        story.append(Paragraph(f"- {g}", body_style))
    story.append(Spacer(1, 10))
    
    diet = disease_data.get("diet")
    treatment = disease_data.get("treatment")
    if diet or treatment:
        story.append(Paragraph("🩺 Recommendations & Suggestions", h2_style))
        if diet:
            story.append(Paragraph(f"<b>Diet Suggestions:</b> {diet}", body_style))
        if treatment:
            story.append(Paragraph(f"<b>Treatment Suggestions:</b> {treatment}", body_style))
        story.append(Spacer(1, 10))
        
    if latest_chatbot_response:
        story.append(Paragraph("🤖 Offline Chatbot Summary", h2_style))
        clean_response = latest_chatbot_response.replace("\n", "<br/>")
        story.append(Paragraph(clean_response, body_style))
        story.append(Spacer(1, 10))
        
    story.append(Paragraph("<b>Medical Disclaimer:</b>", disclaimer_style))
    story.append(Paragraph("This report is generated by an AI-assisted disease prediction system and should not be considered a substitute for professional medical advice.", disclaimer_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# ================================
# PAGE CONFIG
# ================================
st.set_page_config(page_title="Disease Prediction System", layout="wide")

# ================================
# PREMIUM UI CSS
# ================================
st.markdown("""
<style>
body {
    background: linear-gradient(to right, #eef2f3, #dfe9f3);
}
h1 {
    text-align: center;
    color: #1b4332;
}
.stButton>button {
    background: linear-gradient(45deg, #2d6a4f, #40916c);
    color: white;
    border-radius: 10px;
    height: 3em;
    width: 100%;
    font-size: 16px;
    transition: 0.3s;
}
.stButton>button:hover {
    transform: scale(1.05);
}
.card {
    padding: 25px;
    border-radius: 15px;
    background: white;
    box-shadow: 0px 6px 25px rgba(0,0,0,0.1);
    animation: fadeIn 0.8s ease-in-out;
}
@keyframes fadeIn {
    from {opacity:0; transform: translateY(20px);}
    to {opacity:1; transform: translateY(0);}
}
</style>
""", unsafe_allow_html=True)

# ================================
# LOAD MODEL FILES (robust)
# ================================
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent

# Load model artifacts (do not fail the whole app if disease JSON is missing)
MODEL_LOADED = True
model = None
encoder = None
features = []
missing_files = []
try:
    model = pickle.load(open(str(APP_DIR / "ensemble_model.pkl"), "rb"))
    encoder = pickle.load(open(str(APP_DIR / "label_encoder.pkl"), "rb"))
    features = pickle.load(open(str(APP_DIR / "feature_names.pkl"), "rb"))
except FileNotFoundError as e:
    MODEL_LOADED = False
    missing_files.append(getattr(e, "filename", str(e)))

# Load disease_info.json from project root first, then app dir
JSON_PATH = PROJECT_ROOT / "disease_info.json"
if not JSON_PATH.exists():
    JSON_PATH = APP_DIR / "disease_info.json"

if JSON_PATH.exists():
    try:
        loader = DiseaseDataLoader(str(JSON_PATH))
    except Exception:
        loader = None
        st.error(f"Failed to load disease info from: {JSON_PATH}")
else:
    loader = None
    st.warning(f"disease_info.json not found at {PROJECT_ROOT} or {APP_DIR}")

if not MODEL_LOADED:
    st.error(f"Model file(s) not found: {missing_files}")
    st.error(f"Expected model files in: {APP_DIR}")

# ================================
# DATA (PRECAUTIONS)
# ================================
disease_info = {
    "fungal infection": ["Keep skin dry", "Maintain hygiene"],
    "dengue": ["Avoid mosquitoes", "Drink fluids"],
    "malaria": ["Use mosquito nets", "Take medicine"],
    "typhoid": ["Drink clean water", "Avoid outside food"],
    "diabetes": ["Monitor sugar", "Exercise"],
    "heart attack": ["Avoid stress", "Take medication"],
    "common cold": ["Rest", "Drink warm fluids"]
}

general_precautions = [
    "Take rest",
    "Stay hydrated",
    "Maintain hygiene",
    "Avoid self-medication"
]

# ================================
# SIDEBAR
# ================================
st.sidebar.title("🏥 Navigation")
page = st.sidebar.radio("Go to", ["Manual Prediction", "CSV Prediction"])

# ================================
# TITLE
# ================================
st.markdown("<h1>🩺 Multi-Disease Prediction System</h1>", unsafe_allow_html=True)

# ================================
# MANUAL INPUT
# ================================
if page == "Manual Prediction":

    st.subheader("🔍 Select Symptoms")

    selected = st.multiselect("Choose symptoms", features)

    if st.button("Predict Disease"):

        if not MODEL_LOADED:
            st.error("Models not loaded; cannot predict. Check the app logs above for missing files.")

        else:

            input_data = [0]*len(features)

            for s in selected:
                input_data[features.index(s)] = 1

            arr = np.array(input_data).reshape(1, -1)

            pred = model.predict(arr)
            prob = model.predict_proba(arr)

            disease = encoder.inverse_transform(pred)[0]
            confidence = np.max(prob)*100

            # Risk level
            if confidence >= 85:
                risk = "HIGH"
            elif confidence >= 60:
                risk = "MODERATE"
            else:
                risk = "LOW"

            st.session_state["predicted_disease"] = disease
            st.session_state["confidence"] = confidence
            st.session_state["risk_level"] = risk
            
            # Save top 3
            class_probs = prob[0]
            top3_indices = np.argsort(class_probs)[::-1][:3]
            top3_predictions = []
            for idx in top3_indices:
                top3_predictions.append((encoder.classes_[idx], class_probs[idx] * 100))
            st.session_state["top3_predictions"] = top3_predictions
            
            # Reset latest chatbot response for new prediction
            st.session_state["latest_chatbot_response"] = None

    # 📄 Download Medical Report
    if REPORTLAB_AVAILABLE:
        if "predicted_disease" in st.session_state:
            disease = st.session_state["predicted_disease"]
            conf = st.session_state.get("confidence", 0.0)
            risk = st.session_state.get("risk_level", "LOW")
            top3 = st.session_state.get("top3_predictions", [])
            h_score = int(round(conf))
            latest_chat = st.session_state.get("latest_chatbot_response")
            
            if not loader:
                disease_info_data = None
            else:
                disease_info_data = loader.get_disease(disease)
                
            if disease_info_data:
                try:
                    pdf_buffer = generate_pdf(
                        disease=disease,
                        confidence=conf,
                        risk=risk,
                        health_score=h_score,
                        top3_predictions=top3,
                        disease_clean=disease.replace("_"," ").lower(),
                        disease_data=disease_info_data,
                        latest_chatbot_response=latest_chat
                    )
                    
                    date_str = datetime.datetime.now().strftime("%Y_%m_%d")
                    filename = f"medical_report_{date_str}.pdf"
                    
                    st.download_button(
                        label="📄 Download Medical Report",
                        data=pdf_buffer,
                        file_name=filename,
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"Error generating PDF report: {e}")
            else:
                st.warning("Disease information not found.")
        else:
            st.info("Generate a prediction to enable report download.")
            st.download_button(
                label="📄 Download Medical Report",
                data=b"",
                disabled=True
            )
    else:
        st.warning("⚠️ reportlab library is not installed. To download PDF reports, please run: pip install reportlab")

    if "predicted_disease" in st.session_state:
        disease = st.session_state["predicted_disease"]
        confidence = st.session_state["confidence"]
        risk = st.session_state["risk_level"]
        top3_predictions = st.session_state["top3_predictions"]
        
        disease_clean = disease.replace("_"," ").lower()

        # RESULT
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f"### 🧬 Disease: {disease}")
        st.markdown(f"### 📊 Confidence: {confidence:.2f}%")
        st.markdown(f"### ⚠️ Risk Level: {risk}")
        st.markdown('</div>', unsafe_allow_html=True)

        # 🩺 Health Risk Score
        health_score = int(round(confidence))
        if confidence >= 85:
            risk_category = "🔴 High Risk"
            risk_explanation = "Immediate medical consultation recommended."
        elif confidence >= 60:
            risk_category = "🟡 Moderate Risk"
            risk_explanation = "Monitor symptoms and seek medical advice if needed."
        else:
            risk_category = "🟢 Low Risk"
            risk_explanation = "Maintain precautions and observe symptoms."

        st.markdown("### 🩺 Health Risk Score")
        st.markdown(f"**Score:**\n{health_score} / 100")
        st.markdown(f"**Category:**\n{risk_category}")
        st.markdown(f"**Explanation:**\n{risk_explanation}")

        # 🏆 Top 3 Disease Predictions
        st.markdown("### 🏆 Top 3 Disease Predictions")
        top3_names = []
        top3_probs = []
        for i, (name, p) in enumerate(top3_predictions, 1):
            top3_names.append(name)
            top3_probs.append(p)
            st.markdown(f"{i}. {name} — {p:.1f}%")

        # 📊 Disease Probability Distribution
        st.markdown("### 📊 Disease Probability Distribution")
        fig, ax = plt.subplots(figsize=(2.2, 1.6))
        
        # Draw a ring (donut) chart using wedgeprops with distinct vibrant colors
        wedges, texts, autotexts = ax.pie(
            top3_probs,
            labels=top3_names,
            autopct='%1.1f%%',
            startangle=90,
            colors=['#FF6B6B', '#4D96FF', '#6BCB77'],
            wedgeprops=dict(width=0.4, edgecolor='white', linewidth=1.0)
        )
        
        # Format font styles to fit the smaller size
        plt.setp(texts, size=6, weight="bold")
        plt.setp(autotexts, size=5, color="white", weight="bold")
        
        # Keep chart backgrounds transparent
        fig.patch.set_alpha(0.0)
        ax.patch.set_alpha(0.0)
        ax.axis('equal')
        plt.tight_layout()
        
        st.pyplot(fig)
        plt.close(fig)

        # PRECAUTIONS
        st.subheader("🛡️ Precautions")

        if disease_clean in disease_info:
            for p in disease_info[disease_clean]:
                st.write("•", p)

        st.markdown("### General Care")
        for g in general_precautions:
            st.write("-", g)

        st.error("⚠️ Consult a doctor")

# ================================
# CSV MODE
# ================================
elif page == "CSV Prediction":

    st.subheader("📂 Upload CSV File")

    file = st.file_uploader("Upload CSV", type=["csv"])

    if file:
        df = pd.read_csv(file)

        st.dataframe(df.head())

        # If models not loaded, show error and skip processing
        if not MODEL_LOADED or not features:
            st.error("Models not loaded; cannot run CSV predictions. Check the app logs above for missing files.")
        else:

            # Fix missing columns
            for col in features:
                if col not in df.columns:
                    df[col] = 0

            df = df[features]

            preds = model.predict(df)
            labels = encoder.inverse_transform(preds)

            df["Predicted Disease"] = labels

        st.dataframe(df)

        # GRAPH
        st.subheader("📊 Graphs")

        counts = df["Predicted Disease"].value_counts()

        plt.figure()
        counts.plot(kind="bar")
        st.pyplot(plt)

        plt.figure()
        counts.plot(kind="pie", autopct="%1.1f%%")
        st.pyplot(plt)

# ================================
# SIDEBAR CHATBOT (Run at bottom to avoid lifecycle lag)
# ================================
st.sidebar.markdown("---")
st.sidebar.header("🤖 Offline Health Assistant")

if "predicted_disease" in st.session_state:
    disease = st.session_state["predicted_disease"]
    st.sidebar.write(f"**Current Disease:**\n{disease}")
    
    if not loader:
        st.sidebar.warning("Disease data not available. Ensure disease_info.json is present.")
        disease_info = None
    else:
        disease_info = loader.get_disease(disease)

    if disease_info:
        bot = OfflineHealthChatbot(disease_info)
        question = st.sidebar.text_input("Ask about your disease")
        if question:
            response = bot.answer(question)
            st.session_state["latest_chatbot_response"] = response
            st.sidebar.info(response)
    else:
        st.sidebar.warning("Disease information not found.")
else:
    st.sidebar.warning("Predict a disease first.")
