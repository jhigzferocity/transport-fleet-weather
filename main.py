import streamlit as st
import streamlit.components.v1 as components
import requests
from datetime import datetime, timedelta
import io
from xhtml2pdf import pisa
import base64
import os

st.set_page_config(page_title="Titan Fleet Weather System", layout="wide")

# ==========================================
# CUSTOM CSS PARA SA WEBSITE DASHBOARD
# ==========================================
st.markdown("""
<style>
.report-wrapper { background-color: #ffffff; color: #1e293b; padding: 30px; border-radius: 8px; border-top: 5px solid #0b6623; }
.report-header { background-color: #0b6623; color: #ffffff; padding: 25px; border-radius: 4px; margin-bottom: 20px; }
.report-header h1 { margin: 0; font-size: 24px; font-weight: bold; }
.report-header p { margin: 5px 0 0 0; font-size: 14px; color: #a7f3d0; }
.section-title { font-size: 18px; color: #0b6623; border-left: 4px solid #16a34a; padding-left: 10px; margin-top: 30px; margin-bottom: 15px; font-weight: bold; }
.summary-box { border: 1px solid #e2e8f0; border-radius: 4px; padding: 15px; background-color: #f8fafc; color: #0f172a; }
.script-box { background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 4px; padding: 20px; font-style: italic; color: #166534; }
table.custom-table { width: 100%; border-collapse: collapse; margin-bottom: 20px; color: #0f172a; background-color: #ffffff; }
table.custom-table th, table.custom-table td { border: 1px solid #cbd5e1; padding: 12px; text-align: left; }
table.custom-table th { background-color: #f0fdf4; color: #0b6623; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# FUNCTION PARA SA PROFESSIONAL PDF GENERATOR
# ==========================================
def generate_pdf(html_content):
    # Ito ang eksklusibong CSS Template para maging perpekto ang layout ng PDF
    pdf_template = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @page {{ size: A4; margin: 1cm; }}
            body {{ font-family: Helvetica, Arial, sans-serif; font-size: 11pt; color: #0f172a; }}
            .header {{ background-color: #0b6623; color: #ffffff; padding: 15px; text-align: left; }}
            .header h1 {{ margin: 0; font-size: 18pt; }}
            .header p {{ margin: 5px 0 0 0; font-size: 10pt; color: #a7f3d0; }}
            .info-table {{ width: 100%; margin-top: 15px; margin-bottom: 20px; }}
            .info-table td {{ padding: 5px 0; font-size: 11pt; }}
            .section-title {{ color: #0b6623; font-size: 12pt; font-weight: bold; margin-top: 20px; margin-bottom: 10px; border-bottom: 1px solid #0b6623; padding-bottom: 3px; }}
            .summary-box {{ border: 1px solid #cbd5e1; background-color: #f8fafc; padding: 12px; margin-bottom: 15px; text-align: justify; line-height: 1.5; }}
            .custom-table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
            .custom-table th, .custom-table td {{ border: 1px solid #cbd5e1; padding: 8px; text-align: left; font-size: 10pt; }}
            .custom-table th {{ background-color: #f0fdf4; color: #0b6623; font-weight: bold; }}
            .script-box {{ background-color: #f0fdf4; border: 1px solid #bbf7d0; padding: 12px; font-style: italic; color: #166534; text-align: justify; line-height: 1.5; }}
            .footer {{ margin-top: 30px; border-top: 1px solid #cbd5e1; padding-top: 15px; }}
            .footer p {{ margin: 3px 0; font-size: 10pt; }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    pdf_buffer = io.BytesIO()
    pisa.CreatePDF(io.StringIO(pdf_template), dest=pdf_buffer)
    return pdf_buffer.getvalue()

if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", use_column_width=True)

st.sidebar.title("🧭 Transport Navigator")
menu = st.sidebar.radio("Pumili ng View:", ["📊 Report Status", "🗺️ Interactive Map"])
st.sidebar.markdown("---")

st.sidebar.markdown("### 👨‍💼 System Author")
st.sidebar.markdown("**Jigger Coyoca**")
st.sidebar.markdown("*Group Transport Manager*")
st.sidebar.markdown("Consistent Frozen Solutions Corp.")
st.sidebar.markdown("Titan Transnational")

ph_cities = [
    "Angeles City", "Antipolo", "Bacolod", "Bacoor", "Baguio", 
    "Batangas City", "Binan, Laguna", "Butuan City", "Cabuyao, Laguna", 
    "Cagayan de Oro", "Calamba, Laguna", "Caloocan", "Cebu City", 
    "Dasmarinas", "Davao City", "General Santos", "Iloilo City", 
    "Imus", "Las Pinas", "Lipa", "Lucena", "Makati", "Malabon", 
    "Malolos, Bulacan", "Mandaluyong", "Manila", "Marikina", 
    "Marilao, Bulacan", "Meycauayan, Bulacan", "Muntinlupa", 
    "Navotas", "Paranaque", "Pasay", "Pasig", "Quezon City", 
    "San Fernando, Pampanga", "San Juan", "San Pablo, Laguna", 
    "San Pedro, Laguna", "Santa Rosa, Laguna", "Taguig", "Valenzuela", 
    "Zamboanga City"
]

if menu == "📊 Report Status":
    st.title("🚛 Transport Weather Intelligence")
    
    st.markdown("### 🎛️ Command Center Controls")
    colA, colB = st.columns(2)
    
    today = datetime.today()
    max_date = today + timedelta(days=2)
    
    target_date = colA.date_input("🗓️ Petsa ng Biyahe (Forecast):", today, min_value=today, max_value=max_date)
    target_time = colB.time_input("⏰ Oras ng Biyahe:", datetime.now())
    
    selected_routes = st.multiselect(
        "📍 Pumili ng mga Ruta at Hubs para sa ulat:", 
        ph_cities,
        default=["Binan, Laguna", "Manila", "Marilao, Bulacan", "Butuan City"]
    )
    st.markdown("---")

    if selected_routes:
        api_key = "1a45afafbda94c0baf173125261207" 
        
        target_date_str = target_date.strftime('%Y-%m-%d')
        target_hour_str = target_time.strftime('%H:00')
        
        # Paghihiwalayin natin ang rows ng Website at ng PDF
        web_report_rows = ""
        pdf_report_rows = ""
        go_routes, caution_routes, stop_routes = [], [], []
        
        with st.spinner('Kumukuha ng forecast data para sa napiling oras...'):
            for lokasyon in selected_routes:
                url = f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={lokasyon}&days=3&aqi=no"
                try:
                    response = requests.get(url)
                    data = response.json()
                    
                    if "error" not in data:
                        hour_data = None
                        for day in data['forecast']['forecastday']:
                            if day['date'] == target_date_str:
                                for hour in day['hour']:
                                    if hour['time'].endswith(target_hour_str):
                                        hour_data = hour
                                        break
                                break
                        
                        if hour_data:
                            kondisyon = hour_data['condition']['text']
                            hangin = hour_data['wind_kph']
                            ulan = hour_data['precip_mm']
                            
                            # Para sa Website (May kulay na box)
                            if ulan >= 10.0 or hangin >= 60.0:
                                web_status = "<span style='background-color:#fee2e2; color:#991b1b; padding:4px 8px; font-weight:bold;'>STOP / HOLD</span>"
                                pdf_status = "<span style='color:#991b1b; font-weight:bold;'>STOP / HOLD</span>"
                                stop_routes.append(lokasyon)
                            elif ulan >= 1.0 or hangin >= 30.0:
                                web_status = "<span style='background-color:#fef9c3; color:#854d0e; padding:4px 8px; font-weight:bold;'>CAUTION</span>"
                                pdf_status = "<span style='color:#854d0e; font-weight:bold;'>CAUTION</span>"
                                caution_routes.append(lokasyon)
                            else:
                                web_status = "<span style='background-color:#dcfce7; color:#166534; padding:4px 8px; font-weight:bold;'>GO / CLEAR</span>"
                                pdf_status = "<span style='color:#166534; font-weight:bold;'>GO / CLEAR</span>"
                                go_routes.append(lokasyon)
                                
                            web_report_rows += f"<tr><td><strong>{lokasyon}</strong></td><td>{kondisyon}</td><td>{hangin} kph</td><td>{ulan} mm</td><td>{web_status}</td></tr>\n"
                            pdf_report_rows += f"<tr><td><strong>{lokasyon}</strong></td><td>{kondisyon}</td><td>{hangin} kph</td><td>{ulan} mm</td><td>{pdf_status}</td></tr>\n"
                except Exception as e:
                    pass
        
        display_date = target_date.strftime("%B %d, %Y")
        display_time = target_time.strftime("%I:%M %p")
        
        if stop_routes:
            overall_status = "CRITICAL WEATHER OPERATIONS"
            status_color = "#991b1b"
            status_bg = "#fee2e2"
            summary_text = f"Nakataas ang matinding babala para sa mga rutang inaasahang makakaranas ng malakas na ulan at hangin pagsapit ng {display_time}, partikular sa {', '.join(stop_routes)}. I-hold ang mga biyahe sa mga lugar na ito."
        elif caution_routes:
            overall_status = "ACTIVE MONITORING"
            status_color = "#854d0e"
            status_bg = "#fef9c3"
            summary_text = f"Inaasahan ang kalat-kalat na pag-ulan sa pagsapit ng {display_time}, lalo na sa {', '.join(caution_routes)}. Ligtas ang mga malalaking sasakyan, ngunit asahan ang madulas na kalsada."
        else:
            overall_status = "NORMAL OPERATIONS"
            status_color = "#166534"
            status_bg = "#dcfce7"
            summary_text = f"Maaliwalas ang inaasahang lagay ng panahon sa pagsapit ng {display_time} sa lahat ng binabantayang ruta at hubs. Maaaring magpatuloy ang normal na operasyon at pag-dispatch ng lahat ng Titan logistics fleet."

        script_text = f"Magandang araw mula sa Titan Transnational! Narito ang forecast para sa ating mga logistics hubs ngayong {display_date}, bandang {display_time}. "
        if go_routes: script_text += f"Inaasahan natin ang magandang panahon kaya't ligtas at maaliwalas ang biyahe patungo sa {', '.join(go_routes)}. "
        if caution_routes: script_text += f"Pinag-iingat ang mga dadaan sa {', '.join(caution_routes)} dahil sa inaasahang madulas na kalsada. "
        if stop_routes: script_text += f"Isang seryosong babala naman para sa {', '.join(stop_routes)} dahil sa banta ng baha. Ipinagbabawal muna ang pagbiyahe sa mga lugar na ito. "
        script_text += "Manatiling ligtas at nakatutok para sa mga susunod pang ulat!"

        # ==========================================
        # 1. HTML PARA SA WEBSITE DASHBOARD
        # ==========================================
        web_html = f"""<div class="report-wrapper">
        <div style="background-color: #0b6623; color: #ffffff; padding: 25px; border-radius: 4px; margin-bottom: 20px;">
        <h1 style="margin: 0; font-size: 24px; font-weight: bold;">TRANSPORT WEATHER ADVISORY</h1>
        <p style="margin: 5px 0 0 0; font-size: 14px; color: #a7f3d0;">Automated Logistics Intelligence & Operations Report</p>
        </div>
        <table style="width: 100%; border: none; margin-bottom: 30px; color: #0f172a; background-color: transparent;">
        <tr style="border: none;">
        <td style="border: none;"><strong>Petsa ng Biyahe:</strong> {display_date}</td>
        <td style="border: none;"><strong>Oras ng Biyahe:</strong> {display_time}</td>
        <td style="border: none;"><strong>Status:</strong> <span style="background-color: {status_bg}; color: {status_color}; padding: 4px 8px; font-weight: bold;">{overall_status}</span></td>
        </tr>
        </table>
        <h3 style="color: #0b6623; border-left: 4px solid #16a34a; padding-left: 10px;">1. Pangkalahatang Lagay ng Panahon (Executive Summary)</h3>
        <div style="border: 1px solid #e2e8f0; border-radius: 4px; padding: 15px; background-color: #f8fafc; color: #0f172a; margin-bottom: 20px;">
        <p style="margin: 0;">{summary_text}</p>
        </div>
        <h3 style="color: #0b6623; border-left: 4px solid #16a34a; padding-left: 10px;">2. Katayuan ng mga Pangunahing Ruta at Hubs</h3>
        <table class="custom-table" style="width: 100%; border-collapse: collapse; margin-bottom: 20px; color: #0f172a; background-color: #ffffff;">
        <tr>
        <th style="border: 1px solid #cbd5e1; padding: 12px; text-align: left; background-color: #f0fdf4; color: #0b6623; font-weight: bold;">📍 Lokasyon / Hub</th>
        <th style="border: 1px solid #cbd5e1; padding: 12px; text-align: left; background-color: #f0fdf4; color: #0b6623; font-weight: bold;">🌦️ Inaasahang Panahon</th>
        <th style="border: 1px solid #cbd5e1; padding: 12px; text-align: left; background-color: #f0fdf4; color: #0b6623; font-weight: bold;">💨 Hangin</th>
        <th style="border: 1px solid #cbd5e1; padding: 12px; text-align: left; background-color: #f0fdf4; color: #0b6623; font-weight: bold;">🌧️ Ulan</th>
        <th style="border: 1px solid #cbd5e1; padding: 12px; text-align: left; background-color: #f0fdf4; color: #0b6623; font-weight: bold;">🚦 Operational Status</th>
        </tr>
        {web_report_rows}
        </table>
        <h3 style="color: #0b6623; border-left: 4px solid #16a34a; padding-left: 10px;">3. Ready-to-Publish Weather News Script (Pang-Balita)</h3>
        <div style="background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 4px; padding: 20px; font-style: italic; color: #166534; margin-bottom: 30px;">
        "{script_text}"
        </div>
        <div style="border-top: 2px solid #e2e8f0; padding-top: 15px; margin-top: 20px;">
            <p style="margin: 0; font-size: 14px; color: #475569;"><strong>Inihanda ni:</strong></p>
            <p style="margin: 2px 0; font-size: 16px; font-weight: bold; color: #0f172a;">Jigger Coyoca</p>
            <p style="margin: 0; font-size: 14px; color: #475569;">Group Transport Manager | Titan Transnational</p>
        </div>
        </div>"""

        # ==========================================
        # 2. HTML EKSKLUSIBO PARA SA DOWNLOADABLE PDF
        # ==========================================
        pdf_html = f"""
        <div class="header">
            <h1>TRANSPORT WEATHER ADVISORY</h1>
            <p>Automated Logistics Intelligence & Operations Report</p>
        </div>
        <table class="info-table">
            <tr>
                <td width="35%"><strong>Petsa ng Biyahe:</strong><br/>{display_date}</td>
                <td width="30%"><strong>Oras ng Biyahe:</strong><br/>{display_time}</td>
                <td width="35%"><strong>Status:</strong><br/><span style="color: {status_color}; font-weight: bold;">{overall_status}</span></td>
            </tr>
        </table>
        <div class="section-title">1. Pangkalahatang Lagay ng Panahon (Executive Summary)</div>
        <div class="summary-box">
            {summary_text}
        </div>
        <div class="section-title">2. Katayuan ng mga Pangunahing Ruta at Hubs</div>
        <table class="custom-table">
            <tr>
                <th>Lokasyon / Hub</th>
                <th>Inaasahang Panahon</th>
                <th>Hangin</th>
                <th>Ulan</th>
                <th>Operational Status</th>
            </tr>
            {pdf_report_rows}
        </table>
        <div class="section-title">3. Ready-to-Publish Weather News Script (Pang-Balita)</div>
        <div class="script-box">
            "{script_text}"
        </div>
        <div class="footer">
            <p><strong>Inihanda ni:</strong></p>
            <p style="font-size: 12pt; font-weight: bold; color: #0f172a;">Jigger Coyoca</p>
            <p>Group Transport Manager | Titan Transnational</p>
        </div>
        """

        # Ipakita ang Web version sa browser
        st.markdown(web_html, unsafe_allow_html=True)
        
        # Gamitin ang PDF version para sa download button
        pdf_file = generate_pdf(pdf_html)
        st.download_button(
            label="📄 I-download ang Opisyal na Report (PDF)",
            data=pdf_file,
            file_name=f"Titan_Fleet_Advisory_{target_date_str}_{target_hour_str[:2]}.pdf",
            mime="application/pdf"
        )

elif menu == "🗺️ Interactive Map":
    st.title("🗺️ Live Weather Map & Forecast")
    
    windy_iframe = """<iframe width="100%" height="650" src="https://embed.windy.com/embed.html?type=map&location=coordinates&metricRain=mm&metricTemp=°C&metricWind=km/h&zoom=6&overlay=rain&product=ecmwf&level=surface&lat=14.33&lon=121.08" frameborder="0"></iframe>"""
    components.html(windy_iframe, height=650)
