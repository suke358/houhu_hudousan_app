import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

# --- 1. 防府市のデータ定義 ---
# 防府市の都市計画に基づいた一般的な値を設定しています
hofu_city_data = {
    "第一種低層住居専用地域": {"kenpei": 50, "yoseki": 80},
    "第一種中高層住居専用地域": {"kenpei": 60, "yoseki": 150},
    "第二種中高層住居専用地域": {"kenpei": 60, "yoseki": 200},
    "第一種住居地域": {"kenpei": 60, "yoseki": 200},
    "第二種住居地域": {"kenpei": 60, "yoseki": 200},
    "準住居地域": {"kenpei": 60, "yoseki": 200},
    "近隣商業地域": {"kenpei": 80, "yoseki": 200},
    "商業地域": {"kenpei": 80, "yoseki": 400},
    "準工業地域": {"kenpei": 60, "yoseki": 200},
    "工業地域": {"kenpei": 60, "yoseki": 200},
    "工業専用地域": {"kenpei": 60, "yoseki": 200},
    "指定のない区域（白地地域）": {"kenpei": 60, "yoseki": 200}
}

st.set_page_config(page_title="防府市 建築制限マップ", layout="wide")
st.title("🏗️ 住所検索付き！建築制限シミュレーター")

# --- 2. 住所検索機能 ---
st.header("1. 住所から検索")
address_input = st.text_input("防府市の住所を入力してください（例：防府市寿町）", "防府市")

geolocator = Nominatim(user_agent="my_real_estate_app")
location = geolocator.geocode(address_input)

if location:
    # 地図を表示
    m = folium.Map(location=[location.latitude, location.longitude], zoom_start=16)
    folium.Marker([location.latitude, location.longitude], tooltip=address_input).add_to(m)
    st_folium(m, width=700, height=400)
    
    # 本来はここで緯度経度から用途地域を判定しますが、今回は選択式にします
    selected_zone = st.selectbox("その場所の「用途地域」を選択してください", list(hofu_city_data.keys()))
    
    info = hofu_city_data[selected_zone]
    st.info(f"📍 この場所の基本設定：建ぺい率 {info['kenpei']}% / 容積率 {info['yoseki']}%")

# --- 3. 計算シミュレーション機能 ---
st.divider()
st.header("2. 建築可能面積の計算")

col1, col2 = st.columns(2)

with col1:
    land_area = st.number_input("敷地面積 (㎡)", min_value=0.0, value=100.0)
    building_area = st.number_input("建物の面積 (㎡)", min_value=0.0, value=50.0)
    total_floor_area = st.number_input("延べ床面積 (㎡)", min_value=0.0, value=80.0)

# 計算処理
calc_kenpei = (building_area / land_area) * 100 if land_area > 0 else 0
calc_yoseki = (total_floor_area / land_area) * 100 if land_area > 0 else 0

with col2:
    st.subheader("計算結果")
    st.write(f"現在の建ぺい率: **{calc_kenpei:.2f}%**")
    st.write(f"現在の容積率: **{calc_yoseki:.2f}%**")
    
    if location:
        if calc_kenpei <= info['kenpei'] and calc_yoseki <= info['yoseki']:
            st.success("✅ 建築制限をクリアしています！")
        else:
            st.error("⚠️ 制限を超えています！計画を見直してください。")