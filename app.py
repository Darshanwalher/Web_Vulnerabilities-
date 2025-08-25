import os
import traceback
import streamlit as st
from helper import WebScanner, save_report, save_json_report, process_with_ai
from fpdf import FPDF
import json
import datetime
import time

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="CyberGen | Web Security Scanner",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------ CUSTOM CSS (Dark Bleacish) ------------------
st.markdown("""
<style>
    .stApp {
        background: #10121a; /* Very dark bleacish (blue-black) */
        color: #fafafa;
    }
    .main .block-container {
        background-color: #10121a;
        color: #fafafa;
        padding-top: 2rem;
    }
    /* Sidebar styling */
    .css-1d391kg, .css-1cypcdb, .css-17lntkn {
        background-color: #0a0d13 !important;  /* sidebar dark bleacish */
        color: #fafafa !important;
    }
    .css-1d391kg .stMarkdown, .css-1cypcdb .stMarkdown, .css-17lntkn .stMarkdown {
        color: #fafafa !important;
    }
    .main-header {
        font-size: 2.9rem;
        color: #00d4ff;
        text-align: center;
        font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
        letter-spacing: 2.5px;
        font-weight: 700;
        border-bottom: 2px solid #00d4ff;
        padding-bottom: 0.7rem;
        margin-bottom: 2.2rem;
        text-shadow: 0 4px 24px rgba(0,212,255,0.18);
    }
    .section-header {
        font-size: 1.45rem;
        color: #00ffb3;
        margin: 1.5rem 0 1.1rem 0;
        padding: 0.7rem 1.2rem;
        background: linear-gradient(90deg, rgba(0,255,136,0.13), transparent 80%);
        border-left: 5px solid #00ffb3;
        border-radius: 5px;
        font-weight: 500;
        letter-spacing: 1.1px;
    }
    .info-card {
        background: rgba(26,34,54,0.92);
        border-radius: 10px;
        margin-bottom: 20px;
        border: 1px solid #25344a;
        box-shadow: 0 2px 16px 0 rgba(0,212,255,0.06);
        padding: 1.3rem 1.2rem 1.1rem 1.2rem;
    }
    .success-box {
        background: linear-gradient(90deg, #1a5d1a 60%, #112b15 100%);
        color: #4ade80;
        padding: 1rem 1.3rem;
        border-radius: 9px;
        border: 1px solid #22c55e;
        margin-bottom: 1.1rem;
        font-weight: 500;
    }
    .warning-box {
        background: linear-gradient(90deg, #5d4037 60%, #3d2821 100%);
        color: #fbbf24;
        padding: 1rem 1.3rem;
        border-radius: 9px;
        border: 1px solid #f59e0b;
        margin-bottom: 1.1rem;
        font-weight: 500;
    }
    .info-box {
        background: linear-gradient(90deg, #1e3a8a 60%, #283d59 100%);
        color: #93c5fd;
        padding: 1rem 1.3rem;
        border-radius: 9px;
        border: 1px solid #3b82f6;
        margin-bottom: 1.1rem;
        font-weight: 500;
    }
    .port-info {
        background: rgba(26,26,46,0.98);
        padding: 0.8rem 1rem;
        border-radius: 6px;
        margin: 0.3rem 0;
        border: 1px solid #333;
        color: #fafafa;
        font-size: 1.04rem;
        font-weight: 400;
        letter-spacing: .6px;
    }
    .stButton button {
        background: linear-gradient(135deg, #00d4ff 60%, #0099cc 100%);
        color: #181f2a;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        padding: 0.52rem 1.35rem;
        font-size: 1.12rem;
        margin-right: 0.3rem;
        transition: all 0.14s;
        box-shadow: 0 2px 10px rgba(0,212,255,.08);
    }
    .stButton button:hover {
        background: linear-gradient(135deg, #0099cc 60%, #007399 100%);
        color: #fff;
        box-shadow: 0 4px 24px rgba(0,212,255,.17);
    }
    .stTextInput input, .stTextArea textarea {
        background: #232946;
        color: #fafafa;
        border: 1.5px solid #222d3b;
        border-radius: 6px;
        font-size: 1.04rem;
    }
    .stJson {
        background: #1a1a2e;
        border: 1px solid #333;
        border-radius: 8px;
    }
    .stTabs [data-baseweb="tab-list"] {
        background: #232946;
        border-radius: 8px;
        margin-bottom: 0.7rem;
    }
    .stTabs [data-baseweb="tab"] {
        background: #1a1a2e;
        color: #fafafa;
        border-radius: 7px 7px 0 0;
        padding: 0.6rem 1.2rem;
        margin-right: 0.15rem;
        font-size: 1.08rem;
    }
    .stTabs [aria-selected="true"] {
        background: #00d4ff;
        color: #181f2a;
        font-weight: bold;
    }
    .stCode {
        background: #1a1a2e;
        border: 1px solid #333;
        color: #fafafa;
        font-size: 1.09rem;
    }
    .download-section {
        background: #222d3b;
        padding: 1.4rem 1.2rem;
        border-radius: 8px;
        margin-top: 1.5rem;
        border: 1px solid #334661;
        box-shadow: 0 2px 14px 0 rgba(0,212,255,0.09);
    }
    .scan-loading {
        text-align: center;
        color: #00d4ff;
        font-size: 1.2rem;
        padding: 1rem;
    }
    .streamlit-expanderHeader {
        background: #232946;
        color: #00d4ff;
        border: 1px solid #333;
        border-radius: 6px 6px 0 0;
        font-weight: 500;
    }
    .streamlit-expanderContent {
        background: #181f2a;
        border: 1px solid #333;
        border-radius: 0 0 6px 6px;
    }
</style>
""", unsafe_allow_html=True)

# The rest of your main code below remains unchanged...
# [rest of your code continues here...]

# ------------------ HEADER ------------------
st.markdown('<div class="main-header">🛡️ CyberGen</div>', unsafe_allow_html=True)
st.caption("Comprehensive web application security scanning with AI-powered analysis")

# ------------------ SESSION INIT ------------------
for key in ["scan_results", "json_path", "pdf_path"]:
    if key not in st.session_state:
        st.session_state[key] = None

# ------------------ SIDEBAR NAVIGATION ------------------
with st.sidebar:
    st.header("🚀 Navigation")
    st.info("""
    **How to use:**
    1. 🔍 Enter target URL  
    2. ⚡ Launch security scan  
    3. 📊 Analyze results  
    4. 🤖 Deploy AI analysis  
    5. 📥 Download reports
    """)
    st.divider()
    st.header("📡 Scan Status")
    if st.session_state["scan_results"]:
        st.success("✅ Scan completed successfully")
        target = st.session_state["scan_results"]["target"]
        st.markdown(f"**Target:** `{target}`")
        st.markdown(f"**Time:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
        vuln_count = len(st.session_state["scan_results"]["results"])
        open_ports = len(st.session_state["scan_results"]["open_ports"]) if st.session_state["scan_results"]["open_ports"] else 0
        st.markdown(f"""
        **Metrics:**
        - 🚨 Vulnerabilities: `{vuln_count}`
        - 🔓 Open Ports: `{open_ports}`
        - 🛡️ Threat Level: {'HIGH' if vuln_count > 5 else 'MEDIUM' if vuln_count > 0 else 'LOW'}
        """)
    else:
        st.warning("⚠️ No scan data available")

# ------------------ MAIN CONTENT LAYOUT ------------------
col1, col2 = st.columns([2.2, 0.98])

with col1:
    st.markdown('<div class="section-header">🎯 Target Information</div>', unsafe_allow_html=True)
    target_url = st.text_input(
        "**Website URL**", 
        placeholder="https://example.com",
        help="Enter the full URL including http:// or https://"
    )
    button_col1, button_col2 = st.columns(2)
    with button_col1:
        run_scan = st.button("🚀 Run Security Scan", use_container_width=True)
    with button_col2:
        run_ai = st.button("🤖 Run AI Analysis", use_container_width=True, disabled=not st.session_state.get("scan_results"))

# ------------------ RUN SCAN ------------------
if run_scan:
    if not target_url or not (target_url.startswith("http://") or target_url.startswith("https://")):
        st.error("❌ Please enter a valid URL with protocol (http:// or https://)")
    else:
        with st.spinner("🔍 Scanning target website... This may take several minutes."):
            try:
                scanner = WebScanner(target_url.strip())
                results, open_ports, closed_ports, filtered_ports, service_versions, os_info = scanner.scan()
                st.session_state["scan_results"] = {
                    "results": results,
                    "open_ports": open_ports,
                    "closed_ports": closed_ports,
                    "filtered_ports": filtered_ports,
                    "service_versions": service_versions,
                    "os_info": os_info,
                    "target": target_url.strip(),
                }
                # Save reports
                try:
                    pdf_path = save_report(results, open_ports, closed_ports, filtered_ports, service_versions, os_info)
                except Exception as pdf_error:
                    st.warning(f"PDF generation issue: {pdf_error}")
                    pdf_path = None
                try:
                    json_path = save_json_report(results, open_ports, closed_ports, filtered_ports, service_versions, os_info, target_url.strip())
                except Exception as json_error:
                    st.warning(f"JSON generation issue: {json_error}")
                    json_path = None
                st.session_state["pdf_path"] = pdf_path if isinstance(pdf_path, str) and os.path.exists(pdf_path) else None
                st.session_state["json_path"] = json_path if isinstance(json_path, str) and os.path.exists(json_path) else None
                st.success("✅ Security scan completed successfully!")
            except Exception as e:
                st.error(f"❌ Scan failed: {str(e)}")
                with st.expander("🔍 Error Details"):
                    st.code(traceback.format_exc())

# ------------------ RESULTS RENDERING ------------------
if st.session_state["scan_results"]:
    data = st.session_state["scan_results"]
    with col2:
        st.markdown('<div class="section-header">📊 Scan Summary</div>', unsafe_allow_html=True)
        vuln_count = len(data["results"])
        if vuln_count == 0:
            st.markdown('<div class="success-box"><strong>🛡️ No vulnerabilities detected</strong><br>Target appears secure</div>', unsafe_allow_html=True)
        else:
            threat_level = "🚨 CRITICAL" if vuln_count > 10 else "⚠️ HIGH" if vuln_count > 5 else "🔶 MEDIUM"
            st.markdown(f'<div class="warning-box"><strong>{threat_level}</strong><br>{vuln_count} potential vulnerabilities found</div>', unsafe_allow_html=True)
        open_count = len(data["open_ports"]) if data["open_ports"] else 0
        port_status = "🔓 EXPOSED" if open_count > 5 else "🔐 SECURED" if open_count == 0 else "🔒 MONITORED"
        st.markdown(f'<div class="info-box"><strong>{port_status}</strong><br>Open ports: {open_count}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-header">📋 Detailed Results</div>', unsafe_allow_html=True)
    # --- Vulnerabilities ---
    if data["results"]:
        tab1, tab2, tab3, tab4 = st.tabs(["🚨 Vulnerabilities", "🔍 Port Scan", "⚙️ Services", "🖥️ OS Detection"])
        with tab1:
            st.subheader("🚨 Detected Vulnerabilities")
            for i, (vuln, url, guide) in enumerate(data["results"]):
                with st.expander(f"🔴 Vulnerability #{i+1}: {vuln}", expanded=True):
                    severity = "HIGH" if "injection" in vuln.lower() or "xss" in vuln.lower() else "MEDIUM"
                    st.markdown(f"""
                    **Type:** {vuln}  
                    **Location:** `{url}`  
                    **Severity:** {severity}  
                    **Guidance:** [Remediation Guide]({guide})
                    """)
        with tab2:
            st.subheader("🔍 Port Scanning Results")
            port_col1, port_col2, port_col3 = st.columns(3)
            with port_col1:
                st.markdown("**🔓 Open Ports**")
                if data["open_ports"]:
                    for port in data["open_ports"]:
                        st.markdown(f'<div class="port-info">🟢 {port}</div>', unsafe_allow_html=True)
                else:
                    st.info("🔒 No open ports found")
            with port_col2:
                st.markdown("**🔒 Closed Ports**")
                if data["closed_ports"]:
                    for port in data["closed_ports"]:
                        st.markdown(f'<div class="port-info">🔴 {port}</div>', unsafe_allow_html=True)
                else:
                    st.info("🔍 No closed ports found")
            with port_col3:
                st.markdown("**🛡️ Filtered Ports**")
                if data["filtered_ports"]:
                    for port in data["filtered_ports"]:
                        st.markdown(f'<div class="port-info">🟡 {port}</div>', unsafe_allow_html=True)
                else:
                    st.info("🔍 No filtered ports found")
        with tab3:
            st.subheader("⚙️ Service Version Detection")
            if data["service_versions"]:
                st.json(data["service_versions"])
            else:
                st.info("🔍 No service information detected")
        with tab4:
            st.subheader("🖥️ Operating System Detection")
            if data["os_info"]:
                st.markdown(f"**Detected OS:** {data['os_info']}")
                if "windows" in data["os_info"].lower():
                    st.markdown("🪟 **Microsoft Windows Environment**")
                elif "linux" in data["os_info"].lower():
                    st.markdown("🐧 **Linux Environment**")
                elif "unix" in data["os_info"].lower():
                    st.markdown("🔧 **Unix Environment**")
            else:
                st.info("🔍 OS detection inconclusive")
    else:
        st.markdown('<div class="success-box">🛡️ <strong>Secure Target</strong><br>No vulnerabilities detected</div>', unsafe_allow_html=True)

    # --- Download Section ---
    st.markdown('<div class="section-header">📥 Download Reports</div>', unsafe_allow_html=True)
    st.markdown('<div class="download-section">', unsafe_allow_html=True)
    dl_col1, dl_col2 = st.columns(2)
    with dl_col1:
        if st.session_state["pdf_path"]:
            with open(st.session_state["pdf_path"], "rb") as f:
                st.download_button(
                    "📄 Download PDF Report", 
                    f, 
                    file_name="security_scan_report.pdf",
                    help="Comprehensive PDF report",
                    use_container_width=True
                )
        else:
            st.warning("⚠️ PDF report not available")
    with dl_col2:
        if st.session_state["json_path"]:
            with open(st.session_state["json_path"], "rb") as f:
                st.download_button(
                    "📊 Download JSON Report", 
                    f, 
                    file_name="scan_data.json",
                    help="Raw JSON data",
                    use_container_width=True
                )
        else:
            st.warning("⚠️ JSON report not available")
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------ AI ANALYSIS ------------------
if run_ai:
    if not st.session_state.get("json_path"):
        st.warning("⚠️ Please run a scan first to generate data for AI analysis")
    else:
        with st.spinner("🤖 AI is analyzing security findings..."):
            try:
                ai_output = process_with_ai(st.session_state["json_path"])
                st.markdown('<div class="section-header">🤖 AI Security Analysis</div>', unsafe_allow_html=True)
                if isinstance(ai_output, dict):
                    st.json(ai_output)
                else:
                    st.text_area("Analysis Results", ai_output, height=300)
                output_dir = "ai_reports"
                os.makedirs(output_dir, exist_ok=True)
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                # Save JSON
                json_path = os.path.join(output_dir, f"ai_analysis_{timestamp}.json")
                with open(json_path, "w", encoding="utf-8") as jf:
                    json.dump({
                        "timestamp": datetime.datetime.now().isoformat(),
                        "target": st.session_state["scan_results"]["target"],
                        "ai_analysis": ai_output
                    }, jf, indent=4, ensure_ascii=False)
                # Save PDF
                pdf_path = os.path.join(output_dir, f"ai_analysis_{timestamp}.pdf")
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                today = datetime.datetime.now().strftime("%A, %d %B %Y at %H:%M")
                pdf.cell(0, 10, txt=f"AI Analysis Report - {today}", ln=True, align='C')
                pdf.ln(10)
                if isinstance(ai_output, (dict, list)):
                    ai_output_str = json.dumps(ai_output, indent=4, ensure_ascii=False)
                else:
                    ai_output_str = str(ai_output)
                pdf.multi_cell(0, 10, ai_output_str)
                pdf.output(pdf_path)
                st.success("🎉 AI analysis completed successfully!")
                ai_col1, ai_col2 = st.columns(2)
                with ai_col1:
                    with open(json_path, "r", encoding="utf-8") as f:
                        st.download_button(
                            "📊 Download AI Analysis (JSON)", 
                            f, 
                            file_name=f"ai_analysis_{timestamp}.json",
                            use_container_width=True
                        )
                with ai_col2:
                    with open(pdf_path, "rb") as f:
                        st.download_button(
                            "📄 Download AI Analysis (PDF)", 
                            f, 
                            file_name=f"ai_analysis_{timestamp}.pdf",
                            use_container_width=True
                        )
            except Exception as e:
                st.error("❌ AI analysis failed")
                with st.expander("🔍 Error Details"):
                    st.code(traceback.format_exc())

# ------------------ FOOTER ------------------
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #4ade80; font-weight: 600; margin-top: 18px;'>🛡️ Advanced Web Vulnerability Scanner • <span style='color: #00d4ff;'>AI-Powered Security Intelligence</span></div>",
    unsafe_allow_html=True)