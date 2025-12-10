"""
Telvora - Telco ML Recommendation System (Streamlit App)
Aplikasi ini mengintegrasikan frontend dan backend untuk deployment di Streamlit Cloud
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Telvora - Telco Analytics",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .product-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin: 0.5rem 0;
    }
    .stAlert {
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Backend URL (Railway akan run FastAPI & Streamlit di same container)
# Jika BACKEND_URL tidak diset, gunakan localhost (Railway internal)
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = "Dashboard"

# Sidebar Navigation
st.sidebar.title("📱 Telvora Navigation")
page = st.sidebar.radio(
    "Menu",
    ["Dashboard", "Customer Analytics", "Product Simulation", "System Info"]
)
st.session_state.page = page

st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info(
    "Telvora adalah sistem rekomendasi produk telco berbasis Machine Learning "
    "yang membantu menganalisis perilaku pelanggan dan merekomendasikan produk yang tepat."
)

# Helper Functions
def check_backend_health():
    """Check if backend is running"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_customer_analytics(customer_id, top_n=5):
    """Get customer analytics from backend"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/infer/analytic",
            json={"customer_id": customer_id, "top_n": top_n},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def simulate_product(product_name, category, price, duration_days=30):
    """Simulate product impact"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/infer/simulate-product",
            json={
                "product_name": product_name,
                "category": category,
                "price": price,
                "duration_days": duration_days
            },
            timeout=60
        )
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def get_overview_analytics():
    """Get overview analytics"""
    try:
        response = requests.get(f"{BACKEND_URL}/analytics/overview", timeout=120)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def get_churn_composition():
    """Get churn composition data"""
    try:
        response = requests.get(f"{BACKEND_URL}/analytics/churn-composition", timeout=120)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

# Page: Dashboard
if page == "Dashboard":
    st.markdown('<div class="main-header">📊 Telvora Dashboard</div>', unsafe_allow_html=True)
    
    # Check backend health
    if not check_backend_health():
        st.error("⚠️ Backend tidak tersedia. Pastikan FastAPI server berjalan di " + BACKEND_URL)
        st.info("Jalankan backend dengan: `uvicorn src.services.recsys_agentic.main:app --reload`")
        st.stop()
    
    st.success("✅ Backend terhubung")
    
    # Load overview analytics
    with st.spinner("Memuat data analytics..."):
        overview = get_overview_analytics()
    
    if overview:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Pengguna", f"{overview['total_users']:,}")
        
        with col2:
            high_data_pct = overview['high_data']['percentage']
            st.metric("High Data Users", f"{high_data_pct}%")
        
        with col3:
            prepaid_count = overview['plan_counts']['Prepaid']
            st.metric("Prepaid Users", f"{prepaid_count:,}")
        
        with col4:
            postpaid_count = overview['plan_counts']['Postpaid']
            st.metric("Postpaid Users", f"{postpaid_count:,}")
        
        st.markdown("---")
        
        # Model Performance
        if overview.get('model_performance'):
            st.subheader("🎯 Model Performance")
            col1, col2 = st.columns(2)
            with col1:
                accuracy = overview['model_performance'].get('accuracy')
                if accuracy is not None:
                    st.metric("Model Accuracy", f"{accuracy}%")
                else:
                    st.info("Model accuracy tidak tersedia (tidak ada ground truth)")
            with col2:
                st.metric("Total Classes", overview['model_performance']['total_classes'])
        
        st.markdown("---")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Spending by Plan Type")
            plan_data = pd.DataFrame({
                'Plan Type': ['Prepaid', 'Postpaid'],
                'Avg Spending': [
                    overview['plan_spend']['Prepaid'],
                    overview['plan_spend']['Postpaid']
                ]
            })
            fig = px.bar(plan_data, x='Plan Type', y='Avg Spending', 
                        color='Plan Type',
                        title="Average Monthly Spending")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("👥 User Behavior Segments")
            behavior_data = pd.DataFrame({
                'Segment': ['Video Lovers', 'Voice Lovers', 'Balanced'],
                'Count': [
                    overview['video_voice']['video_lovers'],
                    overview['video_voice']['voice_lovers'],
                    overview['video_voice']['balanced']
                ]
            })
            fig = px.pie(behavior_data, values='Count', names='Segment',
                        title="User Behavior Distribution")
            st.plotly_chart(fig, use_container_width=True)
        
        # Top Products
        st.subheader("🏆 Top 10 Recommended Products")
        if overview['top_products']:
            top_prod_df = pd.DataFrame(overview['top_products'])
            fig = px.bar(top_prod_df, x='product_name', y='count',
                        text='percentage',
                        title="Most Recommended Products",
                        labels={'count': 'Recommendation Count', 'product_name': 'Product'})
            fig.update_traces(texttemplate='%{text}%', textposition='outside')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Tidak ada data produk tersedia")
        
        # Churn Composition
        st.markdown("---")
        st.subheader("⚠️ Churn Risk Composition")
        with st.spinner("Menghitung churn composition..."):
            churn_data = get_churn_composition()
        
        if churn_data:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Users", f"{churn_data['total_users']:,}")
            with col2:
                st.metric("🔴 High Risk", f"{churn_data['composition']['high']['percentage']}%")
            with col3:
                st.metric("🟡 Medium Risk", f"{churn_data['composition']['medium']['percentage']}%")
            with col4:
                st.metric("🟢 Low Risk", f"{churn_data['composition']['low']['percentage']}%")
            
            col1, col2 = st.columns(2)
            with col1:
                # Pie chart
                churn_pie_data = pd.DataFrame({
                    'Risk Level': ['High Risk', 'Medium Risk', 'Low Risk'],
                    'Count': [
                        churn_data['composition']['high']['count'],
                        churn_data['composition']['medium']['count'],
                        churn_data['composition']['low']['count']
                    ]
                })
                fig = px.pie(churn_pie_data, values='Count', names='Risk Level',
                            title="Churn Risk Distribution",
                            color='Risk Level',
                            color_discrete_map={'High Risk':'red', 'Medium Risk':'orange', 'Low Risk':'green'})
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.metric("💰 Revenue at Risk", f"Rp {churn_data['revenue_at_risk']:,.0f}")
                st.info(f"High risk users ({churn_data['composition']['high']['count']:,} users) berpotensi churn dengan total revenue Rp {churn_data['revenue_at_risk']:,.0f}")

# Page: Customer Analytics
elif page == "Customer Analytics":
    st.markdown('<div class="main-header">👤 Customer Analytics</div>', unsafe_allow_html=True)
    
    # Check backend health
    if not check_backend_health():
        st.error("⚠️ Backend tidak tersedia. Pastikan FastAPI server berjalan.")
        st.stop()
    
    st.write("Analisis individual customer dan rekomendasi produk personalized")
    
    # Input
    col1, col2 = st.columns([3, 1])
    with col1:
        customer_id = st.text_input("Customer ID", placeholder="Contoh: C0001")
    with col2:
        top_n = st.number_input("Top N Products", min_value=1, max_value=10, value=5)
    
    if st.button("🔍 Analyze Customer", type="primary"):
        if customer_id:
            with st.spinner("Menganalisis customer..."):
                result = get_customer_analytics(customer_id, top_n)
            
            if result:
                # Customer Info
                st.subheader(f"📋 Analisis Customer: {customer_id}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("User Category", result['user_category'])
                with col2:
                    churn_label = result['churn']['label'].upper()
                    churn_color = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🔴"}
                    st.metric("Churn Risk", f"{churn_color.get(churn_label, '')} {churn_label}")
                with col3:
                    churn_prob = result['churn']['probability'] * 100
                    st.metric("Churn Probability", f"{churn_prob:.1f}%")
                
                # AI Insights (jika ada)
                if result.get('ai_insights'):
                    st.markdown("---")
                    st.subheader("🤖 AI Insights")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Product Recommendation Insight:**")
                        st.info(result['ai_insights'].get('product_recommendation', 'N/A'))
                    
                    with col2:
                        st.markdown("**Churn Analysis Insight:**")
                        st.warning(result['ai_insights'].get('churn_analysis', 'N/A'))
                
                # Recommendations
                st.markdown("---")
                st.subheader("🎁 Recommended Products")
                
                recommendations = result['recommendations']['items']
                for idx, item in enumerate(recommendations, 1):
                    with st.expander(f"{idx}. {item['product_name']} - Rp {item['price']:,.0f}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Category:** {item['category']}")
                            st.write(f"**Price:** Rp {item['price']:,.0f}")
                        with col2:
                            st.write(f"**Duration:** {item['duration_days']} days")
                        
                        st.write("**Reasons:**")
                        for reason in item['reasons']:
                            st.write(f"- {reason}")
                
                st.caption(f"Generated at: {result['generated_at']}")
            else:
                st.error("❌ Customer tidak ditemukan atau terjadi error")
        else:
            st.warning("⚠️ Masukkan Customer ID terlebih dahulu")

# Page: Product Simulation
elif page == "Product Simulation":
    st.markdown('<div class="main-header">🧪 Product Simulation</div>', unsafe_allow_html=True)
    
    # Check backend health
    if not check_backend_health():
        st.error("⚠️ Backend tidak tersedia. Pastikan FastAPI server berjalan.")
        st.stop()
    
    st.write("Simulasikan dampak produk baru terhadap customer base")
    
    # Input Form
    with st.form("simulation_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            product_name = st.text_input("Product Name", placeholder="Contoh: Unlimited Data 100GB")
            category = st.selectbox(
                "Category",
                ["Data", "Voice", "VOD", "Combo", "Roaming", "DeviceBundle", "SMS"]
            )
        
        with col2:
            price = st.number_input("Price (Rp)", min_value=0, value=100000, step=10000)
            duration_days = st.number_input("Duration (days)", min_value=1, value=30, step=1)
        
        submitted = st.form_submit_button("🚀 Run Simulation", type="primary")
    
    if submitted:
        if product_name:
            with st.spinner("Menjalankan simulasi... (ini mungkin memakan waktu 30-60 detik)"):
                result = simulate_product(product_name, category, price, duration_days)
            
            if result:
                st.success("✅ Simulasi selesai!")
                
                # Metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Target Hits", f"{result['hits']:,}")
                with col2:
                    st.metric("Conversion Rate", f"{result['conversion_rate']:.1f}%")
                with col3:
                    st.metric("Potential Revenue", f"Rp {result['revenue']:,.0f}")
                with col4:
                    total = result.get('total_users', 0)
                    st.metric("Total Users Analyzed", f"{total:,}")
                
                # Recommendation
                st.markdown("---")
                st.subheader("📊 Recommendation")
                if result['conversion_rate'] > 20:
                    st.success(result['recommendation'])
                elif result['conversion_rate'] > 10:
                    st.warning(result['recommendation'])
                else:
                    st.error(result['recommendation'])
                
                # Segments Breakdown
                if result.get('segments'):
                    st.markdown("---")
                    st.subheader("🎯 Target Segments Breakdown")
                    segments_df = pd.DataFrame([
                        {'Segment': k, 'Count': v}
                        for k, v in result['segments'].items()
                    ]).sort_values('Count', ascending=False)
                    
                    fig = px.bar(segments_df, x='Segment', y='Count',
                                title="Target Users by Segment",
                                text='Count')
                    fig.update_traces(texttemplate='%{text}', textposition='outside')
                    st.plotly_chart(fig, use_container_width=True)
                
                st.caption(f"Generated at: {result['generated_at']}")
            else:
                st.error("❌ Simulasi gagal")
        else:
            st.warning("⚠️ Masukkan nama produk terlebih dahulu")

# Page: System Info
elif page == "System Info":
    st.markdown('<div class="main-header">ℹ️ System Information</div>', unsafe_allow_html=True)
    
    st.subheader("Backend Configuration")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Backend URL:**")
        st.code(BACKEND_URL)
        
        st.write("**Backend Status:**")
        if check_backend_health():
            st.success("✅ Connected")
        else:
            st.error("❌ Disconnected")
    
    with col2:
        st.write("**Environment Variables:**")
        env_vars = {
            "BACKEND_URL": os.getenv("BACKEND_URL", "Not set"),
            "VITE_SUPABASE_URL": "***" if os.getenv("VITE_SUPABASE_URL") else "Not set",
            "VITE_SUPABASE_ANON_KEY": "***" if os.getenv("VITE_SUPABASE_ANON_KEY") else "Not set",
            "GEMINI_API_KEY": "***" if os.getenv("GEMINI_API_KEY") else "Not set",
            "OLLAMA_MODEL": os.getenv("OLLAMA_MODEL", "Not set"),
        }
        for key, value in env_vars.items():
            st.text(f"{key}: {value}")
    
    st.markdown("---")
    st.subheader("📚 Documentation")
    
    st.markdown("""
    ### Cara Menjalankan Aplikasi
    
    #### 1. Setup Backend (FastAPI)
    ```bash
    # Aktifkan virtual environment
    .venv310\\Scripts\\Activate.ps1
    
    # Install dependencies
    pip install -r src/services/recsys_agentic/requirements.txt
    
    # Jalankan backend
    uvicorn src.services.recsys_agentic.main:app --reload --host 0.0.0.0 --port 8000
    ```
    
    #### 2. Setup Frontend (Streamlit)
    ```bash
    # Install Streamlit
    pip install streamlit
    
    # Jalankan Streamlit
    streamlit run streamlit_app.py
    ```
    
    #### 3. Environment Variables
    Buat file `.env.local` di root project dengan isi:
    ```
    VITE_SUPABASE_URL=your_supabase_url
    VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
    GEMINI_API_KEY=your_gemini_api_key (optional)
    OLLAMA_MODEL=your_ollama_model (optional)
    BACKEND_URL=http://localhost:8000
    ```
    
    ### Deployment ke Streamlit Cloud
    
    1. Push code ke GitHub repository
    2. Buka [streamlit.io/cloud](https://streamlit.io/cloud)
    3. Connect repository Anda
    4. Set environment variables di Streamlit Cloud settings
    5. Deploy!
    
    **Catatan:** Untuk deployment, Anda perlu:
    - Deploy backend FastAPI ke layanan terpisah (Railway, Render, dll)
    - Update `BACKEND_URL` di Streamlit secrets ke URL backend production
    """)
    
    st.markdown("---")
    st.subheader("🔧 Technical Stack")
    st.markdown("""
    - **Frontend:** Streamlit
    - **Backend:** FastAPI + Uvicorn
    - **ML Models:** scikit-learn (Random Forest)
    - **Database:** Supabase (PostgreSQL)
    - **AI:** Google Gemini / Ollama (optional)
    - **Visualization:** Plotly
    """)

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**Telvora v1.0**")
st.sidebar.markdown("Built with ❤️ using Streamlit")
