import streamlit as st
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt

# Konfigurasi Halaman Web
st.set_page_config(
    page_title="Pemilah Barang Fuzzy Sugeno",
    page_icon="📦",
    layout="wide"
)

# Judul Aplikasi
st.title("📦 Dashboard Pemilahan Barang Otomatis")
st.subheader("Metode Fuzzy Sugeno Berbasis Python")
st.markdown("---")

# ==========================================
# 1. SETUP LOGIKA FUZZY SUGENO
# ==========================================
@st.cache_resource
def init_fuzzy():
    red = ctrl.Antecedent(np.arange(0, 256, 1), 'red')
    green = ctrl.Antecedent(np.arange(0, 256, 1), 'green')
    kategori = ctrl.Consequent(np.arange(1, 4, 1), 'kategori')

    # Fungsi Keanggotaan
    red['rendah'] = fuzz.trimf(red.universe, [0, 0, 128])
    red['sedang'] = fuzz.trimf(red.universe, [64, 128, 192])
    red['tinggi'] = fuzz.trimf(red.universe, [128, 255, 255])

    green['rendah'] = fuzz.trimf(green.universe, [0, 0, 128])
    green['sedang'] = fuzz.trimf(green.universe, [64, 128, 192])
    green['tinggi'] = fuzz.trimf(green.universe, [128, 255, 255])

    kategori['kategori_merah'] = fuzz.trimf(kategori.universe, [1, 1, 1.8])
    kategori['kategori_hijau'] = fuzz.trimf(kategori.universe, [1.5, 2, 2.5])
    kategori['kategori_lain']  = fuzz.trimf(kategori.universe, [2.2, 3, 3])

    # Aturan Fuzzy
    rule1 = ctrl.Rule(red['tinggi'] & green['rendah'], kategori['kategori_merah'])
    rule2 = ctrl.Rule(red['rendah'] & green['tinggi'], kategori['kategori_hijau'])
    rule3 = ctrl.Rule(red['rendah'] & green['rendah'], kategori['kategori_lain'])
    rule4 = ctrl.Rule(red['tinggi'] & green['tinggi'], kategori['kategori_lain'])
    rule5 = ctrl.Rule(red['sedang'] | green['sedang'], kategori['kategori_lain'])

    system = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5])
    return system, red, green

system_ctrl, red, green = init_fuzzy()

# ==========================================
# 2. TAMPILAN INTERAKTIF
# ==========================================
col_input, col_graph = st.columns([1, 1.2])

with col_input:
    st.header("🎮 Panel Input Warna")
    
    input_red = st.slider("Komponen Warna Red (R):", 0, 255, 210)
    input_green = st.slider("Komponen Warna Green (G):", 0, 255, 30)

    # Preview Warna
    st.write("**Pratinjau Warna Input:**")
    color_hex = f"#{input_red:02x}{input_green:02x}00"
    st.markdown(
        f'<div style="background-color: {color_hex}; height: 50px; border-radius: 8px; border: 1px solid #ccc;"></div>',
        unsafe_allow_html=True
    )

    st.markdown("---")
    st.header("📊 Hasil Keputusan Fuzzy")

    # Komputasi Fuzzy
    simulasi = ctrl.ControlSystemSimulation(system_ctrl)
    simulasi.input['red'] = input_red
    simulasi.input['green'] = input_green

    try:
        simulasi.compute()
        hasil = simulasi.output['kategori']
        st.metric("Skor Defuzzifikasi", f"{hasil:.2f}")

        if hasil < 1.6:
            st.success("🔴 **Barang Kategori MERAH (Lolos Seleksi A)**")
        elif hasil < 2.3:
            st.success("🟢 **Barang Kategori HIJAU (Lolos Seleksi B)**")
        else:
            st.error("⚪ **Barang Kategori LAIN / AFKIR (Ditolak)**")

    except Exception:
        st.warning("Kombinasi warna termasuk Kategori Afkir/Lainnya.")

with col_graph:
    st.header("📈 Visualisasi Kurva Keanggotaan")
    
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(red.universe, fuzz.trimf(red.universe, [0, 0, 128]), 'r', label='R-Rendah')
    ax.plot(red.universe, fuzz.trimf(red.universe, [128, 255, 255]), 'r--', label='R-Tinggi')
    ax.plot(green.universe, fuzz.trimf(green.universe, [0, 0, 128]), 'g', label='G-Rendah')
    ax.plot(green.universe, fuzz.trimf(green.universe, [128, 255, 255]), 'g--', label='G-Tinggi')

    ax.axvline(x=input_red, color='red', linestyle=':', linewidth=2, label=f'Input R ({input_red})')
    ax.axvline(x=input_green, color='green', linestyle=':', linewidth=2, label=f'Input G ({input_green})')

    ax.set_title("Posisi Input pada Fungsi Keanggotaan")
    ax.set_xlabel("Nilai Komponen Warna (0-255)")
    ax.set_ylabel("Derajat Keanggotaan (μ)")
    ax.legend(loc='lower right', fontsize=8)
    
    st.pyplot(fig)