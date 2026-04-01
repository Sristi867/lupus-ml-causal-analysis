import streamlit as st
import numpy as np
import joblib
import datetime
import matplotlib.pyplot as plt
import time

# Load model
model = joblib.load("lupus_model.pkl")

st.set_page_config(page_title="Clinical Lupus System", layout="wide")

# 🎨 CLEAN WHITE MEDICAL THEME
st.markdown("""
<style>
.stApp {
    background-color: #ffffff;
    color: #1a1a1a;
}

/* TOP BAR */
.top-bar {
    background-color: #ffffff;
    padding: 22px 30px;
    border-bottom: 2px solid #c62828;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.top-title {
    font-size: 30px;
    font-weight: 700;
    color: #1a1a1a;
    letter-spacing: 1px;
}

.top-sub {
    font-size: 12px;
    color: #666;
}

/* NAV BAR */
.navbar {
    display: flex;
    gap: 30px;
    padding: 12px 30px;
    background-color: #f4f6f9;
    border-bottom: 1px solid #ddd;
}

/* Buttons */
.stButton>button {
    background-color: #c62828;
    color: white;
    border-radius: 6px;
    height: 3em;
    font-weight: 600;
}

/* Inputs */
input, textarea {
    background-color: #ffffff !important;
    color: #1a1a1a !important;
    border: 1px solid #ccc !important;
}

</style>
""", unsafe_allow_html=True)

# 🏥 TOP HEADER
st.markdown("""
<div class="top-bar">
    <div>
        <div class="top-title">Clinical Lupus Assessment System</div>
        <div class="top-sub">AI-based Gene Expression Analysis</div>
    </div>
    <div class="top-sub">
        Research Prototype • Not for Clinical Use
    </div>
</div>
""", unsafe_allow_html=True)

# 🧭 TOP NAVIGATION
if "page" not in st.session_state:
    st.session_state.page = "Analysis"

col1, col2, col3 = st.columns([1,1,1])

with col1:
    if st.button("Analysis"):
        st.session_state.page = "Analysis"

with col2:
    if st.button("Visual Insights"):
        st.session_state.page = "Visual Insights"

with col3:
    if st.button("Clinical Report"):
        st.session_state.page = "Clinical Report"

page = st.session_state.page

st.divider()

# =========================
# 🧬 ANALYSIS PAGE
# =========================
if page == "Analysis":

    st.header("Patient Information")

    colA, colB, colC = st.columns(3)
    with colA:
        patient_name = st.text_input("Patient Name")
    with colB:
        patient_id = st.text_input("Patient ID")
    with colC:
        st.text_input("Date", datetime.datetime.now().strftime("%Y-%m-%d"), disabled=True)

    st.divider()

    st.subheader("Biomarker Input")

    c1, c2, c3 = st.columns(3)

    with c1:
        g1 = st.number_input("IFI44L", 0.0, 15.0, 5.0)
        g2 = st.number_input("IFIT1", 0.0, 15.0, 5.0)

    with c2:
        g3 = st.number_input("MX1", 0.0, 15.0, 5.0)
        g4 = st.number_input("SIGLEC1", 0.0, 15.0, 5.0)

    with c3:
        g5 = st.number_input("LY6E", 0.0, 15.0, 5.0)

    inputs = [g1, g2, g3, g4, g5]

    sample = np.array(inputs * (model.n_features_in_ // 5 + 1))[:model.n_features_in_]
    sample = sample.reshape(1, -1)

    if st.button("Run Clinical Analysis"):

        with st.spinner("Analyzing genomic signals..."):
            time.sleep(1)

        prob = model.predict_proba(sample)[0][1]
        prob_percent = prob * 100

        if prob >= 0.7:
            diagnosis = "Lupus Detected"
            risk = "High Risk"
        elif prob >= 0.4:
            diagnosis = "Possible Lupus"
            risk = "Moderate Risk"
        else:
            diagnosis = "No Lupus Detected"
            risk = "Low Risk"

        st.session_state["result"] = {
            "name": patient_name,
            "id": patient_id,
            "prob": prob,
            "prob_percent": prob_percent,
            "risk": risk,
            "diagnosis": diagnosis,
            "genes": inputs,
            "date": datetime.datetime.now().strftime("%Y-%m-%d")
        }

        st.success("Analysis Complete. Go to Clinical Report.")

# =========================
# 📊 VISUAL INSIGHTS
# =========================
elif page == "Visual Insights":

    st.header("Visual Clinical Insights")

    if "result" not in st.session_state:
        st.warning("Run analysis first.")
    else:
        data = st.session_state["result"]
        prob = data["prob"]
        inputs = data["genes"]

        st.subheader("Risk Progression")

        progress_bar = st.progress(0)
        for i in range(int(prob * 100)):
            time.sleep(0.01)
            progress_bar.progress(i + 1)

        st.caption(f"Final Probability: {data['prob_percent']:.1f}%")

        st.divider()

        st.subheader("Gene Expression Trend")

        genes = ["IFI44L", "IFIT1", "MX1", "SIGLEC1", "LY6E"]

        fig, ax = plt.subplots()
        ax.plot(genes, inputs, marker='o', linewidth=2)
        ax.set_ylabel("Expression Level")

        st.pyplot(fig)

# =========================
# 📄 CLINICAL REPORT
# =========================
elif page == "Clinical Report":

    st.header("Clinical Report")

    if "result" not in st.session_state:
        st.warning("Run analysis first.")
    else:
        data = st.session_state["result"]

        st.subheader("Patient Details")
        st.write(f"Name: {data['name']}")
        st.write(f"ID: {data['id']}")
        st.write(f"Date: {data['date']}")

        st.divider()

        st.subheader("Assessment")

        st.metric("Probability", f"{data['prob_percent']:.1f}%")
        st.metric("Diagnosis", data["diagnosis"])
        st.metric("Risk Level", data["risk"])

        st.markdown(f"""
        <div style='background:#f4f6f9;padding:20px;border-left:5px solid #c62828;border-radius:6px'>
        <b>Clinical Interpretation:</b> {data['diagnosis']} with probability {data['prob_percent']:.1f}%
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        st.subheader("Gene Values")

        genes = ["IFI44L", "IFIT1", "MX1", "SIGLEC1", "LY6E"]

        for g, v in zip(genes, data["genes"]):
            st.write(f"{g}: {v}")

        report = f"""
        CLINICAL REPORT

        Patient: {data['name']}
        ID: {data['id']}
        Date: {data['date']}

        Diagnosis: {data['diagnosis']}
        Probability: {data['prob_percent']:.1f}%
        Risk Level: {data['risk']}

        Gene Values:
        {data['genes']}
        """

        st.download_button("Download Report", report, file_name="clinical_report.txt")