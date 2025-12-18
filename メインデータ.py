import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import altair as alt
from geopy.geocoders import Nominatim # 住所検索用の道具

# --- 1. データ定義（省略なし） ---
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
st.title("🗺️ 住所検索付き！建築制限シミュレーター")

# --- 2. 住所検索機能 ---
st.sidebar.header("🔍 住所で検索")
address_input = st.sidebar.text_input("防府市の住所を入力してください", "山口県防府市寿町7-1") # 防府市役所を初期値に

# 住所を緯度経度に変換する処理
geolocator = Nominatim(user_agent="my_building_app")
location = geolocator.geocode(address_input)

if location:
    lat, lng = location.latitude, location.longitude
else:
    # 住所が見つからない場合は市役所の位置
    lat, lng = 34.053, 131.570

# --- 3. その他の設定 ---
st.sidebar.divider()
select_zone = st.sidebar.selectbox("用途地域を選択", list(hofu_city_data.keys()))
land_size = st.sidebar.slider("敷地面積 (㎡)", 10, 1000, 150)
is_corner = st.sidebar.checkbox("角地緩和を適用する (+10%)")

# --- 4. 地図の表示 ---
col_map, col_res = st.columns([2, 1])

with col_map:
    st.write(f"### 📍 表示中: {address_input}")
    # locationを指定することで、入力された住所に地図がジャンプする
    m = folium.Map(location=[lat, lng], zoom_start=17)
    folium.Marker([lat, lng], tooltip=address_input).add_to(m) # ピンを立てる
    map_data = st_folium(m, width=700, height=450, key="address_map")

# --- 5. 計算と表示（前回と同じ） ---
base_kenpei = hofu_city_data[select_zone]["kenpei"]
yoseki_rate = hofu_city_data[select_zone]["yoseki"]
final_kenpei = base_kenpei + 10 if is_corner else base_kenpei

max_building_area = land_size * (final_kenpei / 100)
max_total_floor_area = land_size * (yoseki_rate / 100)

with col_res:
    st.write("### 🏠 判定結果")
    st.metric("建築面積 (1階)", f"{max_building_area:.2f} ㎡")
    st.metric("延べ床面積 (合計)", f"{max_total_floor_area:.2f} ㎡")
    if is_corner: st.success("角地緩和適用中")

# グラフ表示
st.divider()
chart_data = pd.DataFrame({
    "項目": ["1.敷地面積", "2.1階上限", "3.延べ床上限"],
    "面積(㎡)": [land_size, max_building_area, max_total_floor_area]
})
chart = alt.Chart(chart_data).mark_bar().encode(
    x=alt.X('項目', axis=alt.Axis(labelAngle=-45)),
    y='面積(㎡)',
    color='項目'
).properties(height=300)
st.altair_chart(chart, use_container_width=True)