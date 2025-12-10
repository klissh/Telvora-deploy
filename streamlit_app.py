"""
Telvora - Telco ML Recommendation System (Streamlit Standalone)
Semua backend logic terintegrasi langsung (No FastAPI needed)
Deploy-ready untuk Streamlit Community Cloud
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional
from collections import Counter
import time
import os

# ML & Data
import joblib
from supabase import create_client, Client

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
</style>
""", unsafe_allow_html=True)

# ==================== CONFIGURATION ====================

# Paths
APP_DIR = Path(__file__).resolve().parent
MODEL_DIR = APP_DIR / "src" / "services" / "model"

# Constants
TOP_N_DEFAULT = 5

TARGET_TO_CATEGORY_MAP = {
    'Data Booster': 'Data',
    'Voice Bundle': 'Voice',
    'Streaming Partner Pack': 'VOD',
    'Family Plan Offer': 'Combo',
    'Retention Offer': 'Combo',
    'Top-up Promo': 'Data',
    'General Offer': 'Combo',
    'Roaming Pass': 'Roaming',
    'Device Upgrade Offer': 'DeviceBundle',
}

# ==================== LOAD RESOURCES ====================

@st.cache_resource
def load_ml_models():
    """Load ML models and artifacts (cached)"""
    try:
        model_path = MODEL_DIR / "model_dokter_rf.pkl"
        le_path = MODEL_DIR / "label_encoder.pkl"
        ga_path = MODEL_DIR / "global_averages.pkl"
        
        if not all([model_path.exists(), le_path.exists(), ga_path.exists()]):
            st.error(f"❌ Model files not found in: {MODEL_DIR}")
            st.stop()
        
        clf = joblib.load(model_path)
        label_encoder = joblib.load(le_path)
        global_averages = joblib.load(ga_path)
        
        return clf, label_encoder, global_averages
    except Exception as e:
        st.error(f"❌ Error loading models: {str(e)}")
        st.stop()

@st.cache_resource
def init_supabase():
    """Initialize Supabase client (cached)"""
    url = st.secrets.get("VITE_SUPABASE_URL", "")
    key = st.secrets.get("VITE_SUPABASE_ANON_KEY", "")
    
    if not url or not key:
        st.error("❌ Supabase credentials not found in secrets!")
        st.stop()
    
    return create_client(url, key)

# Load resources
clf, label_encoder, global_averages = load_ml_models()
supabase = init_supabase()

# ==================== HELPER FUNCTIONS ====================

def fetch_customer(customer_id: str) -> Dict[str, Any]:
    """Fetch customer profile from database"""
    try:
        res = supabase.table('customer_profile').select('*').eq('customer_id', customer_id).single().execute()
        if res.data is None:
            return None
        return res.data
    except Exception as e:
        st.error(f"Error fetching customer: {str(e)}")
        return None

def fetch_products() -> pd.DataFrame:
    """Fetch product catalog from database"""
    try:
        res = supabase.table('product_catalog').select('*').execute()
        products = res.data or []
        if not products:
            return pd.DataFrame()
        
        df = pd.DataFrame(products)
        # Add derived columns
        eps = 1e-6
        df['price_per_gb'] = df['price'] / (df.get('product_capacity_gb', 0) + eps)
        df['price_per_minute'] = df['price'] / (df.get('product_capacity_minutes', 0) + eps)
        df['price_per_sms'] = df['price'] / (df.get('product_capacity_sms', 0) + eps)
        df.replace([np.inf, -np.inf], np.nan, inplace=True)
        return df
    except Exception as e:
        st.error(f"Error fetching products: {str(e)}")
        return pd.DataFrame()

def fetch_all_users_paginated(page_size: int = 1000, max_attempts: int = 20) -> List[Dict[str, Any]]:
    """Fetch all customer profiles with pagination"""
    all_users = []
    attempt = 0
    empty_batches = 0
    
    while attempt < max_attempts:
        start_range = len(all_users)
        end_range = len(all_users) + page_size - 1
        
        try:
            res = supabase.table('customer_profile').select('*').range(start_range, end_range).execute()
            batch_size = len(res.data) if res.data else 0
            
            if batch_size > 0:
                all_users.extend(res.data)
                empty_batches = 0
            else:
                empty_batches += 1
            
            if empty_batches >= 2:
                break
            
            attempt += 1
        except Exception as e:
            st.warning(f"Pagination error: {str(e)}")
            break
    
    return all_users

def prepare_features(customer_row: Dict[str, Any]) -> pd.DataFrame:
    """Prepare features for ML model prediction"""
    df = pd.DataFrame([customer_row])
    
    numeric_features = [
        'avg_data_usage_gb', 'pct_video_usage', 'avg_call_duration', 'sms_freq',
        'monthly_spend', 'topup_freq', 'travel_score', 'complaint_count'
    ]
    
    for col in numeric_features:
        if col in df.columns:
            if isinstance(df[col].iloc[0], str):
                df[col] = df[col].astype(str).str.replace(',', '.')
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Fix negatives
    if 'avg_call_duration' in df.columns:
        df['avg_call_duration'] = df['avg_call_duration'].abs()
    if 'monthly_spend' in df.columns:
        df['monthly_spend'] = df['monthly_spend'].abs()
    
    # Drop ID columns
    for drop_col in ('customer_id', 'target_offer', 'target_encoded'):
        if drop_col in df.columns:
            df = df.drop(columns=[drop_col])
    
    return df

def compute_churn_bucket(pred_label: str, user_row: Dict[str, Any], global_avgs: Dict[str, float]) -> str:
    """Compute churn risk bucket using rules-based logic"""
    avg_data = float(global_avgs.get('avg_data_usage_gb', 0))
    avg_call = float(global_avgs.get('avg_call_duration', 0))
    avg_sms = float(global_avgs.get('sms_freq', 0))
    avg_topup = float(global_avgs.get('topup_freq', 0))
    
    usage_data = float(user_row.get('avg_data_usage_gb') or 0)
    usage_call = float(user_row.get('avg_call_duration') or 0)
    usage_sms = float(user_row.get('sms_freq') or 0)
    usage_topup = float(user_row.get('topup_freq') or 0)
    complaints = float(user_row.get('complaint_count') or 0)
    
    has_complaint = complaints > 0
    
    below_data = usage_data < avg_data
    below_call = usage_call < avg_call
    below_sms = usage_sms < avg_sms
    below_topup = usage_topup < avg_topup
    
    aboveeq_data = usage_data >= avg_data
    aboveeq_call = usage_call >= avg_call
    aboveeq_sms = usage_sms >= avg_sms
    aboveeq_topup = usage_topup >= avg_topup
    
    num_below_usage = sum([below_data, below_call, below_sms])
    num_above_usage = sum([aboveeq_data, aboveeq_call, aboveeq_sms])
    all_usage_above = aboveeq_data and aboveeq_call and aboveeq_sms
    
    # HIGH RISK
    if pred_label == 'Retention Offer':
        return 'high'
    
    # MEDIUM RISK
    if (not (pred_label == 'Retention Offer') and 
        has_complaint and 
        num_below_usage >= 2 and 
        below_topup):
        return 'medium'
    
    # LOW RISK (multiple cases)
    if not has_complaint and num_above_usage >= 2:
        return 'low'
    if has_complaint and aboveeq_topup:
        return 'low'
    if not has_complaint and all_usage_above:
        return 'low'
    if not has_complaint and usage_topup <= avg_topup and num_above_usage >= 1:
        return 'low'
    if not has_complaint and aboveeq_topup and all_usage_above:
        return 'low'
    
    return 'medium'

def recommend_products(pred_label: str, user_row: Dict[str, Any], products_df: pd.DataFrame, top_n: int) -> List[Dict]:
    """Generate product recommendations based on prediction"""
    recommendations = []
    seen = set()
    
    budget = float(user_row.get('monthly_spend') or 0.0)
    primary_category = TARGET_TO_CATEGORY_MAP.get(pred_label)
    
    def add_items(df: pd.DataFrame, desc: str, take: int):
        nonlocal recommendations, seen
        for _, row in df.head(take).iterrows():
            recommendations.append({
                'product_id': str(row.get('product_id') or ''),
                'product_name': str(row.get('product_name') or ''),
                'category': str(row.get('category') or ''),
                'price': float(row.get('price') or 0),
                'duration_days': int(row.get('duration_days') or 30),
                'reasons': [desc, f"Sesuai prediksi: {pred_label}"]
            })
            seen.add(row.get('product_name'))
    
    # Primary recommendations
    if primary_category:
        base = products_df[products_df['category'] == primary_category].copy()
        
        if primary_category == 'Retention Offer':
            top = base[base['price'] <= budget * 0.8].sort_values('price', ascending=True)
            if top.empty:
                top = base.sort_values('price', ascending=True)
            add_items(top, "Rekomendasi Utama (Retensi Hemat)", 3)
        elif primary_category == 'DeviceBundle':
            top = base[base['price'] <= budget].sort_values('price', ascending=False)
            if top.empty:
                top = base.sort_values('price', ascending=True)
            add_items(top, "Rekomendasi Utama (Upgrade Gadget)", 3)
        else:
            budget_ok = base[base['price'] <= budget].sort_values('price', ascending=False)
            top = budget_ok if not budget_ok.empty else base.sort_values('price', ascending=True)
            add_items(top, f"Rekomendasi Utama ({primary_category} Premium)", 3)
    
    # Secondary cross-sell
    remaining = top_n - len(recommendations)
    if remaining > 0 and global_averages is not None:
        scores = [
            ('Data', float(user_row.get('avg_data_usage_gb') or 0) / (global_averages['avg_data_usage_gb'] + 1e-6)),
            ('Voice', float(user_row.get('avg_call_duration') or 0) / (global_averages['avg_call_duration'] + 1e-6)),
            ('VOD', float(user_row.get('pct_video_usage') or 0) / (global_averages['pct_video_usage'] + 1e-6)),
            ('SMS', float(user_row.get('sms_freq') or 0) / (global_averages['sms_freq'] + 1e-6)),
        ]
        sorted_scores = sorted([s for s in scores if s[1] > 1.0], key=lambda x: x[1], reverse=True)
        
        for cat, _ in sorted_scores:
            if remaining <= 0:
                break
            if primary_category and cat == primary_category:
                continue
            
            filtered = products_df[
                (products_df['category'] == cat) &
                (products_df['price'] <= budget * 0.5) &
                (~products_df['product_name'].isin(seen))
            ].copy()
            
            if not filtered.empty:
                filtered['is_short'] = filtered['duration_days'].apply(lambda x: 1 if x <= 7 else 2)
                top_sec = filtered.sort_values(by=['is_short', 'price'], ascending=[True, True])
                add_items(top_sec, f"Rekomendasi Sekunder ({cat})", 1)
                remaining = top_n - len(recommendations)
    
    # Fillers
    if len(recommendations) < top_n:
        remaining = top_n - len(recommendations)
        fillers = products_df[(~products_df['product_name'].isin(seen)) & (products_df['price'] <= budget * 0.5)]
        fillers = fillers.sort_values('price', ascending=True)
        for _, row in fillers.head(remaining).iterrows():
            recommendations.append({
                'product_id': str(row.get('product_id') or ''),
                'product_name': str(row.get('product_name') or ''),
                'category': str(row.get('category') or ''),
                'price': float(row.get('price') or 0),
                'duration_days': int(row.get('duration_days') or 30),
                'reasons': [f"{row.get('category')}", "Filler value"]
            })
            if len(recommendations) >= top_n:
                break
    
    return recommendations[:top_n]

# ==================== SIDEBAR ====================

st.sidebar.title("📱 Telvora Navigation")
page = st.sidebar.radio(
    "Menu",
    ["Dashboard", "Customer Analytics", "Product Simulation", "System Info"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info(
    "Telvora adalah sistem rekomendasi produk telco berbasis Machine Learning "
    "yang membantu menganalisis perilaku pelanggan dan merekomendasikan produk yang tepat."
)

# ==================== PAGE: DASHBOARD ====================

if page == "Dashboard":
    st.markdown('<div class="main-header">📊 Telvora Dashboard</div>', unsafe_allow_html=True)
    
    st.success("✅ Sistem terhubung")
    
    with st.spinner("Memuat data analytics..."):
        all_users = fetch_all_users_paginated()
        
        if not all_users:
            st.error("❌ Tidak ada data user")
            st.stop()
        
        df_users = pd.DataFrame(all_users)
        
        # Prepare features
        numeric_features = [
            'avg_data_usage_gb', 'pct_video_usage', 'avg_call_duration', 'sms_freq',
            'monthly_spend', 'topup_freq', 'travel_score', 'complaint_count'
        ]
        
        X = df_users.copy()
        for col in numeric_features:
            if col in X.columns:
                X[col] = X[col].astype(str).str.replace(',', '.')
                X[col] = pd.to_numeric(X[col], errors='coerce').fillna(0)
        
        if 'avg_call_duration' in X.columns:
            X['avg_call_duration'] = X['avg_call_duration'].abs()
        if 'monthly_spend' in X.columns:
            X['monthly_spend'] = X['monthly_spend'].abs()
        
        for drop_col in ('customer_id', 'target_offer', 'target_encoded'):
            if drop_col in X.columns:
                X = X.drop(columns=[drop_col])
        
        # Predict
        all_preds_idx = clf.predict(X)
        all_labels = label_encoder.inverse_transform(all_preds_idx)
        
        total_users = len(df_users)
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Pengguna", f"{total_users:,}")
        
        with col2:
            if 'avg_data_usage_gb' in df_users.columns:
                q75 = df_users['avg_data_usage_gb'].quantile(0.75)
                high_data_count = int((df_users['avg_data_usage_gb'] >= max(10.0, q75)).sum())
                high_data_pct = (high_data_count / total_users * 100) if total_users else 0
                st.metric("High Data Users", f"{high_data_pct:.1f}%")
        
        with col3:
            prepaid_count = int((df_users['plan_type'] == 'Prepaid').sum()) if 'plan_type' in df_users.columns else 0
            st.metric("Prepaid Users", f"{prepaid_count:,}")
        
        with col4:
            postpaid_count = int((df_users['plan_type'] == 'Postpaid').sum()) if 'plan_type' in df_users.columns else 0
            st.metric("Postpaid Users", f"{postpaid_count:,}")
        
        st.markdown("---")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Spending by Plan Type")
            if 'plan_type' in df_users.columns:
                plan_data = df_users.groupby('plan_type')['monthly_spend'].mean().reset_index()
                plan_data.columns = ['Plan Type', 'Avg Spending']
                fig = px.bar(plan_data, x='Plan Type', y='Avg Spending', color='Plan Type')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("👥 User Behavior Segments")
            if 'pct_video_usage' in df_users.columns and 'avg_call_duration' in df_users.columns:
                video_pct = df_users['pct_video_usage'].values
                call_dur = df_users['avg_call_duration'].values
                median_call = float(np.median(call_dur)) if len(call_dur) else 0.0
                
                video_lovers = int((video_pct >= 0.6).sum())
                voice_lovers = int(((video_pct <= 0.4) & (call_dur >= median_call)).sum())
                balanced = total_users - video_lovers - voice_lovers
                
                behavior_data = pd.DataFrame({
                    'Segment': ['Video Lovers', 'Voice Lovers', 'Balanced'],
                    'Count': [video_lovers, voice_lovers, balanced]
                })
                fig = px.pie(behavior_data, values='Count', names='Segment')
                st.plotly_chart(fig, use_container_width=True)
        
        # Churn Composition
        st.markdown("---")
        st.subheader("⚠️ Churn Risk Composition")
        
        with st.spinner("Menghitung churn composition..."):
            churn_buckets = {'high': 0, 'medium': 0, 'low': 0}
            revenue_at_risk = 0
            
            for i, label in enumerate(all_labels):
                bucket = compute_churn_bucket(label, all_users[i], global_averages)
                churn_buckets[bucket] += 1
                if bucket == 'high':
                    revenue_at_risk += float(all_users[i].get('monthly_spend') or 0)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Users", f"{total_users:,}")
            with col2:
                high_pct = (churn_buckets['high'] / total_users * 100) if total_users else 0
                st.metric("🔴 High Risk", f"{high_pct:.1f}%")
            with col3:
                med_pct = (churn_buckets['medium'] / total_users * 100) if total_users else 0
                st.metric("🟡 Medium Risk", f"{med_pct:.1f}%")
            with col4:
                low_pct = (churn_buckets['low'] / total_users * 100) if total_users else 0
                st.metric("🟢 Low Risk", f"{low_pct:.1f}%")
            
            col1, col2 = st.columns(2)
            with col1:
                churn_pie = pd.DataFrame({
                    'Risk Level': ['High Risk', 'Medium Risk', 'Low Risk'],
                    'Count': [churn_buckets['high'], churn_buckets['medium'], churn_buckets['low']]
                })
                fig = px.pie(churn_pie, values='Count', names='Risk Level',
                            color='Risk Level',
                            color_discrete_map={'High Risk':'red', 'Medium Risk':'orange', 'Low Risk':'green'})
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.metric("💰 Revenue at Risk", f"Rp {revenue_at_risk:,.0f}")
                st.info(f"High risk users ({churn_buckets['high']:,}) berpotensi churn")

# ==================== PAGE: CUSTOMER ANALYTICS ====================

elif page == "Customer Analytics":
    st.markdown('<div class="main-header">👤 Customer Analytics</div>', unsafe_allow_html=True)
    
    st.write("Analisis individual customer dan rekomendasi produk personalized")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        customer_id = st.text_input("Customer ID", placeholder="Contoh: C0001")
    with col2:
        top_n = st.number_input("Top N Products", min_value=1, max_value=10, value=5)
    
    if st.button("🔍 Analyze Customer", type="primary"):
        if customer_id:
            with st.spinner("Menganalisis customer..."):
                customer_row = fetch_customer(customer_id)
                
                if not customer_row:
                    st.error("❌ Customer tidak ditemukan")
                else:
                    # Prepare features & predict
                    X = prepare_features(customer_row)
                    pred_idx = clf.predict(X)
                    pred_label = label_encoder.inverse_transform(pred_idx)[0]
                    user_category = TARGET_TO_CATEGORY_MAP.get(pred_label, "Unknown")
                    
                    # Churn probability
                    class_list = list(label_encoder.classes_)
                    try:
                        idx_ret = class_list.index('Retention Offer')
                        proba_all = clf.predict_proba(X)
                        churn_proba = float(proba_all[0][idx_ret])
                    except:
                        churn_proba = 0.0
                    
                    churn_label = compute_churn_bucket(pred_label, customer_row, global_averages)
                    
                    # Get recommendations
                    products_df = fetch_products()
                    recommendations = recommend_products(pred_label, customer_row, products_df, top_n)
                    
                    # Display results
                    st.subheader(f"📋 Analisis Customer: {customer_id}")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("User Category", user_category)
                    with col2:
                        churn_color = {"low": "🟢", "medium": "🟡", "high": "🔴"}
                        st.metric("Churn Risk", f"{churn_color.get(churn_label, '')} {churn_label.upper()}")
                    with col3:
                        st.metric("Churn Probability", f"{churn_proba*100:.1f}%")
                    
                    # Recommendations
                    st.markdown("---")
                    st.subheader("🎁 Recommended Products")
                    
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
        else:
            st.warning("⚠️ Masukkan Customer ID terlebih dahulu")

# ==================== PAGE: PRODUCT SIMULATION ====================

elif page == "Product Simulation":
    st.markdown('<div class="main-header">🧪 Product Simulation</div>', unsafe_allow_html=True)
    
    st.write("Simulasikan dampak produk baru terhadap customer base")
    
    with st.form("simulation_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            product_name = st.text_input("Product Name", placeholder="Unlimited Data 100GB")
            category = st.selectbox("Category", ["Data", "Voice", "VOD", "Combo", "Roaming", "DeviceBundle", "SMS"])
        
        with col2:
            price = st.number_input("Price (Rp)", min_value=0, value=100000, step=10000)
            duration_days = st.number_input("Duration (days)", min_value=1, value=30)
        
        submitted = st.form_submit_button("🚀 Run Simulation", type="primary")
    
    if submitted and product_name:
        with st.spinner("Menjalankan simulasi..."):
            all_users = fetch_all_users_paginated()
            
            if not all_users:
                st.error("❌ Tidak ada data user")
            else:
                df_users = pd.DataFrame(all_users)
                
                # Prepare features
                X = df_users.copy()
                numeric_features = ['avg_data_usage_gb', 'pct_video_usage', 'avg_call_duration', 'sms_freq',
                                  'monthly_spend', 'topup_freq', 'travel_score', 'complaint_count']
                
                for col in numeric_features:
                    if col in X.columns:
                        X[col] = X[col].astype(str).str.replace(',', '.')
                        X[col] = pd.to_numeric(X[col], errors='coerce').fillna(0)
                
                if 'avg_call_duration' in X.columns:
                    X['avg_call_duration'] = X['avg_call_duration'].abs()
                if 'monthly_spend' in X.columns:
                    X['monthly_spend'] = X['monthly_spend'].abs()
                
                for drop_col in ('customer_id', 'target_offer', 'target_encoded'):
                    if drop_col in X.columns:
                        X = X.drop(columns=[drop_col])
                
                # Predict
                all_preds_idx = clf.predict(X)
                all_labels = label_encoder.inverse_transform(all_preds_idx)
                
                # Simulate
                hits = 0
                revenue = 0.0
                segments = {}
                
                for i, label in enumerate(all_labels):
                    budget = float(all_users[i].get('monthly_spend') or 0)
                    cat = TARGET_TO_CATEGORY_MAP.get(label)
                    
                    if cat == category and price <= budget:
                        hits += 1
                        revenue += price
                        segments[label] = segments.get(label, 0) + 1
                
                total_users = len(all_users)
                conversion_rate = (hits / total_users * 100) if total_users else 0
                
                # Results
                st.success("✅ Simulasi selesai!")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Target Hits", f"{hits:,}")
                with col2:
                    st.metric("Conversion Rate", f"{conversion_rate:.1f}%")
                with col3:
                    st.metric("Potential Revenue", f"Rp {revenue:,.0f}")
                with col4:
                    st.metric("Total Users", f"{total_users:,}")
                
                # Recommendation
                st.markdown("---")
                st.subheader("📊 Recommendation")
                if conversion_rate > 20:
                    st.success(f"Produk ini memiliki potensi TINGGI dengan {hits} target user ({conversion_rate:.1f}%). Sangat direkomendasikan!")
                elif conversion_rate > 10:
                    st.warning(f"Produk ini memiliki potensi SEDANG dengan {hits} target user ({conversion_rate:.1f}%). Pertimbangkan optimasi.")
                else:
                    st.error(f"Produk ini memiliki potensi RENDAH dengan {hits} target user ({conversion_rate:.1f}%). Perlu evaluasi ulang.")
                
                # Segments
                if segments:
                    st.markdown("---")
                    st.subheader("🎯 Target Segments")
                    segments_df = pd.DataFrame([
                        {'Segment': k, 'Count': v}
                        for k, v in segments.items()
                    ]).sort_values('Count', ascending=False)
                    
                    fig = px.bar(segments_df, x='Segment', y='Count', text='Count')
                    fig.update_traces(texttemplate='%{text}', textposition='outside')
                    st.plotly_chart(fig, use_container_width=True)

# ==================== PAGE: SYSTEM INFO ====================

elif page == "System Info":
    st.markdown('<div class="main-header">ℹ️ System Information</div>', unsafe_allow_html=True)
    
    st.subheader("System Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**System Status:**")
        st.success("✅ ML Models Loaded")
        st.success("✅ Database Connected")
        st.success("✅ Streamlit Running")
    
    with col2:
        st.write("**Model Info:**")
        st.info(f"Classifier: Random Forest")
        st.info(f"Classes: {len(label_encoder.classes_)}")
        st.info(f"Features: {len(global_averages)} metrics")
    
    st.markdown("---")
    st.subheader("📚 About")
    
    st.markdown("""
    ### Telvora - Telco ML Recommendation System
    
    Sistem rekomendasi produk telco berbasis Machine Learning yang menganalisis:
    - ✅ Perilaku penggunaan customer (data, voice, video)
    - ✅ Risiko churn pelanggan
    - ✅ Rekomendasi produk personalized
    - ✅ Simulasi dampak produk baru
    
    **Tech Stack:**
    - Frontend: Streamlit
    - ML Model: scikit-learn (Random Forest)
    - Database: Supabase (PostgreSQL)
    - Deployment: Streamlit Community Cloud
    
    **Deployment:** Streamlit Community Cloud (Free Forever!)
    """)
    
    st.markdown("---")
    st.markdown("**Telvora v2.0 - Streamlit Standalone**")
    st.markdown("Deployed on Streamlit Community Cloud 🚀")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**Telvora v2.0**")
st.sidebar.markdown("Built with ❤️ using Streamlit")
