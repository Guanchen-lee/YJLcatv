import streamlit as st
import math

# 設定網頁標題與排版
st.set_page_config(page_title="CATV 現場工程訊號計算器", page_icon="📡", layout="centered")

st.title("📡 YJL 工程訊號計算器")
st.markdown("支援起點設備、主線混用距離、被動元件(DC)、多顆 TAP 智慧串接與儀表逆向回推")
st.markdown("---")

# 選擇計算模式
calc_mode = st.radio("選擇計算模式", ["🚀 線上預估 (起點 終端)", "🔍 訊號回推 (儀表量測 回推起點)"], horizontal=True)

st.markdown("---")

# DC 被動元件對照表函數
def get_passive_loss(passive_type, selected_port):
    if passive_type == "DC2 (兩路)":
        return 3.5, 3.5, 3.5
    elif passive_type == "DC3 (三路)":
        if "3.5" in selected_port:
            return 3.5, 3.8, 3.5
        else:
            return 7.0, 7.5, 7.0
    elif passive_type == "DC8 (兩路不平衡)":
        if "8" in selected_port:
            return 8.0, 8.5, 8.0
        else:
            return 1.0, 1.5, 1.0
    return 0.0, 0.0, 0.0

# 共用 TAP 資料庫
tap_options = ["8-23", "8-20", "8-17", "8-14", "8-11", "8-8",
               "4-23", "4-20", "4-17", "4-14", "4-11", "4-8"]

tap_db_table = {
    "8-23": (22.5, 23.5, 38.0), "8-20": (19.5, 20.5, 35.0), 
    "8-17": (16.5, 17.5, 32.0), "8-14": (13.5, 14.5, 29.0), 
    "8-11": (10.5, 11.5, 26.0), "8-8":  (7.5,  8.5,  23.0),
    "4-23": (22.5, 23.5, 38.0), "4-20": (19.5, 20.5, 35.0), 
    "4-17": (16.5, 17.5, 32.0), "4-14": (13.5, 14.5, 29.0), 
    "4-11": (10.5, 11.5, 26.0), "4-8":  (7.5,  8.5,  23.0)
}

if calc_mode == "🚀 線上預估 (起點 終端)":
    st.subheader("1. 選擇起點設備與基準值")
    device_type = st.selectbox(
        "設備型號", 
        [
            "請選擇設備型號...",
            "光機 (下行 95/104 | 上行 35)", 
            "大通幹線放大器 (下行 95/104 | 上行 35)", 
            "大通延伸放大器 (下行 91/100 | 上行 35)", 
            "兆赫幹線放大器 (下行 95/104 | 上行 35)", 
            "兆赫延伸放大器 (下行 95/104 | 上行 31)", 
            "手動自訂"
        ]
    )

    base_down_low, base_down_high, base_up = 0.0, 0.0, 35.0
    if "大通延伸" in device_type:
        base_down_low, base_down_high, base_up = 91.0, 100.0, 35.0
    elif "兆赫延伸" in device_type:
        base_down_low, base_down_high, base_up = 91.0, 100.0, 35.0
    elif "光機" in device_type or "幹線放大器" in device_type:
        base_down_low, base_down_high, base_up = 95.0, 104.0, 35.0

    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1:
        orig_low = st.number_input("起點下行低頻 (dBμV)", value=base_down_low, step=0.5)
    with col_d2:
        orig_high = st.number_input("起點下行高頻 (dBμV)", value=base_down_high, step=0.5)
    with col_d3:
        orig_up = st.number_input("起點上行基準 (dBμV)", value=base_up, step=0.5)

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        target_low_freq = st.number_input("目標低頻頻率 (MHz)", value=261.0, step=1.0)
    with col_f2:
        target_high_freq = st.number_input("目標高頻頻率 (MHz)", value=975.0, step=1.0)

    st.markdown("---")
    st.subheader("2. 主幹線線材與混合距離 (500P3 / 7C)")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        dist_500 = st.number_input("500P3 同軸幹線距離 (公尺)", value=0.0, step=10.0)
    with col_c2:
        dist_7c = st.number_input("7C 同軸電纜距離 (公尺)", value=0.0, step=10.0)

    loss_500_low = (2.5 / 100.0) * math.sqrt(target_low_freq / 750.0) * dist_500
    loss_500_high = (5.5 / 100.0) * math.sqrt(target_high_freq / 750.0) * dist_500
    loss_500_up = (0.8 / 100.0) * dist_500

    loss_7c_low = (4.5 / 100.0) * math.sqrt(target_low_freq / 750.0) * dist_7c
    loss_7c_high = (14.0 / 100.0) * math.sqrt(target_high_freq / 750.0) * dist_7c
    loss_7c_up = (1.5 / 100.0) * dist_7c

    total_main_loss_low = loss_500_low + loss_7c_low
    total_main_loss_high = loss_500_high + loss_7c_high
    total_main_loss_up = loss_500_up + loss_7c_up

    st.markdown("---")
    st.subheader("3. 外部被動元件選擇 (DC2 / DC3 / DC8)")
    has_passive = st.checkbox("是否經過主線被動元件 (DC)", value=False)
    passive_loss_low, passive_loss_high, passive_up_effect = 0.0, 0.0, 0.0
    passive_port_desc = "無"

    if has_passive:
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            passive_type = st.selectbox("被動元件型號", ["DC2 (兩路)", "DC3 (三路)", "DC8 (兩路特殊)"])
        with col_p2:
            if passive_type == "DC2 (兩路)":
                passive_port_desc = "3.5dB 埠"
            elif passive_type == "DC3 (三路)":
                passive_port_desc = st.selectbox("選擇 DC3 輸出埠", ["3.5dB 埠", "7dB 埠 (A)", "7dB 埠 (B)"])
            elif passive_type == "DC8 (兩路不平衡)":
                passive_port_desc = st.selectbox("選擇 DC8 輸出埠", ["8dB 埠", "1dB 埠"])
        passive_loss_low, passive_loss_high, passive_up_effect = get_passive_loss(passive_type, passive_port_desc)

    st.markdown("---")
    st.subheader("4. TAP 串接選擇")
    num_taps = st.number_input("這條路徑總共經過幾顆 TAP？ (設為 0 則不經過 TAP)", min_value=0, max_value=10, value=0, step=1)
    total_tap_loss_low, total_tap_loss_high = 0.0, 0.0
    final_tap_up_val = orig_up

    for i in range(int(num_taps)):
        st.write(f"**第 {i+1} 顆 TAP**")
        col_t1, col_t2 = st.columns([2, 1])
        with col_t1:
            t_model = st.selectbox(f"選擇第 {i+1} 顆 TAP 型號", tap_options, key=f"tap_model_{i}", index=0)
        with col_t2:
            is_target = st.checkbox(f"這是目標測量點？", value=(i == num_taps - 1), key=f"is_target_{i}")
        
        t_low, t_high, t_up = tap_db_table[t_model][:3]
        if is_target:
            total_tap_loss_low += t_low
            total_tap_loss_high += t_high
            final_tap_up_val = t_up
        else:
            total_tap_loss_low += 1.5
            total_tap_loss_high += 2.0

    st.markdown("---")
    st.subheader("5. 用戶端室內線與室內分配器")
    col_in1, col_in2 = st.columns(2)
    with col_in1:
        indoor_splitter = st.selectbox("室內分配器選擇", ["無", "DC2 (二分配)", "DC3 (三分配 - 3.5dB埠)", "DC3 (三分配 - 7dB埠)"])
    with col_in2:
        indoor_length = st.number_input("室內 5C 線長 (公尺)", value=0.0, step=5.0)

    splitter_low, splitter_high, splitter_up = 0.0, 0.0, 0.0
    if indoor_splitter == "DC2 (二分配)":
        splitter_low, splitter_high, splitter_up = 3.5, 3.8, 3.5
    elif indoor_splitter == "DC3 (三分配 - 3.5dB埠)":
        splitter_low, splitter_high, splitter_up = 3.5, 3.8, 3.5
    elif indoor_splitter == "DC3 (三分配 - 7dB埠)":
        splitter_low, splitter_high, splitter_up = 7.0, 7.5, 7.0

    indoor_loss_low = (6.7 / 100.0) * math.sqrt(target_low_freq / 750.0) * indoor_length
    indoor_loss_high = (21.4 / 100.0) * math.sqrt(target_high_freq / 750.0) * indoor_length
    indoor_loss_up = (2.0 / 100.0) * indoor_length

    if device_type == "請選擇設備型號..." or orig_low == 0.0:
        final_low, final_high, final_up = 0.0, 0.0, 0.0
    else:
        final_low = orig_low - total_main_loss_low - passive_loss_low - total_tap_loss_low - splitter_low - indoor_loss_low
        final_high = orig_high - total_main_loss_high - passive_loss_high - total_tap_loss_high - splitter_high - indoor_loss_high
        final_up = final_tap_up_val + splitter_up + indoor_loss_up + passive_up_effect + total_main_loss_up

    st.markdown("---")
    st.subheader("🎯 預期量測結果 (dBμV)")
    col_r1, col_r2, col_r3 = st.columns(3)
    col_r1.metric(label=f"📺 下行低頻", value=f"{final_low:.1f} dBμV")
    col_r2.metric(label=f"📺 下行高頻", value=f"{final_high:.1f} dBμV")
    col_r3.metric(label=f"🔄 上行回傳預估", value=f"{final_up:.1f} dBμV")

    with st.expander("🔍 檢視詳細損耗與各段明細"):
        st.write(f"**【下行傳輸明細】**")
        st.write(f"- 設備起點: 下行低 {orig_low} dBμV / 高 {orig_high} dBμV")
        if dist_500 > 0:
            st.write(f"- 500P3 幹線損耗 ({dist_500}m): 低頻 {loss_500_low:.2f} dB / 高頻 {loss_500_high:.2f} dB")
        if dist_7c > 0:
            st.write(f"- 7C 電纜損耗 ({dist_7c}m): 低頻 {loss_7c_low:.2f} dB / 高頻 {loss_7c_high:.2f} dB")
        if has_passive:
            st.write(f"- 外部被動元件 ({passive_type} - {passive_port_desc}): 下行扣除低 {passive_loss_low} dB / 高 {passive_loss_high} dB")
        if num_taps > 0:
            st.write(f"- TAP 串接累計扣除總量: 低頻 {total_tap_loss_low:.1f} dB / 高頻 {total_tap_loss_high:.1f} dB")
        if indoor_splitter != "無":
            st.write(f"- 室內分配器 ({indoor_splitter}): 扣除 {splitter_low} dB")
        if indoor_length > 0:
            st.write(f"- 室內 5C 線損 ({indoor_length}m): 下行低 {indoor_loss_low:.2f} dB / 高 {indoor_loss_high:.2f} dB")
        
        st.markdown("---")
        st.write(f"**【上行回傳明細 (由內往外反推)】**")
        st.write(f"- 目標 TAP 上行基準: {final_tap_up_val} dBμV")
        if indoor_splitter != "無":
            st.write(f"- 室內分配器補償 ({indoor_splitter}): +{splitter_up} dB")
        if indoor_length > 0:
            st.write(f"- 室內 5C 線長損耗補償 ({indoor_length}m): +{indoor_loss_up:.2f} dB")
        if has_passive:
            st.write(f"- 外部被動元件補償 ({passive_type}): +{passive_up_effect} dB")
        if dist_500 > 0 or dist_7c > 0:
            st.write(f"- 主線路回傳補償總計: +{total_main_loss_up:.2f} dB")

else:
    # 現場逆向回推模式 (放寬容許誤差至 10 dB，工程實務更輕鬆)
    st.subheader("🔍 現場儀表量測值 往回推算起點訊號與狀態診斷")
    st.write("請選擇來源設備標準輸出，輸入現場量測值，並設定經過的 TAP 總數量與型號（系統會自動計算前面過路 TAP 與目標 TAP 的總損失）：")

    ref_device = st.selectbox(
        "選擇來源設備標準輸出基準",
        [
            "光機 / 幹線放大器 (標準: 下行 95.0 / 104.0 dBμV)",
            "延伸放大器 (標準: 下行 91.0 / 100.0 dBμV)",
            "手動自訂標準"
        ]
    )

    if "光機" in ref_device:
        std_low, std_high = 95.0, 104.0
    elif "延伸" in ref_device:
        std_low, std_high = 91.0, 100.0
    else:
        col_std1, col_std2 = st.columns(2)
        with col_std1:
            std_low = st.number_input("標準起點低頻 (dBμV)", value=95.0, step=0.5)
        with col_std2:
            std_high = st.number_input("標準起點高頻 (dBμV)", value=104.0, step=0.5)

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        measured_low = st.number_input("儀表量測下行低頻 (dBμV)", value=0.0, step=0.5)
    with col_m2:
        measured_high = st.number_input("儀表量測下行高頻 (dBμV)", value=0.0, step=0.5)

    st.markdown("---")
    st.write("**【設定測量點的 TAP 串接結構】**")
    back_num_taps = st.number_input("這條路徑總共經過幾顆 TAP？ (例如在第 5 顆量測則填 5)", min_value=1, max_value=10, value=3, step=1, key="back_num_taps")
    
    total_back_tap_loss_l = 0.0
    total_back_tap_loss_h = 0.0
    back_target_tap_name = ""

    for i in range(int(back_num_taps)):
        st.write(f"**第 {i+1} 顆 TAP**")
        col_bt1, col_bt2 = st.columns([2, 1])
        with col_bt1:
            bt_model = st.selectbox(f"選擇第 {i+1} 顆 TAP 型號", tap_options, key=f"back_tap_model_{i}", index=1 if i == back_num_taps - 1 else 0)
        with col_bt2:
            bt_is_target = st.checkbox(f"這是量測點？", value=(i == back_num_taps - 1), key=f"back_is_target_{i}")
        
        bt_l, bt_h = tap_db_table[bt_model][:2]
        if bt_is_target:
            total_back_tap_loss_l += bt_l
            total_back_tap_loss_h += bt_h
            back_target_tap_name = bt_model
        else:
            total_back_tap_loss_l += 1.5
            total_back_tap_loss_h += 2.0

    st.markdown("---")
    st.write("反推主線混用距離：")
    col_bc1, col_bc2 = st.columns(2)
    with col_bc1:
        back_dist_500 = st.number_input("500P3 距離 (公尺)", value=0.0, step=10.0, key="back_500")
    with col_bc2:
        back_dist_7c = st.number_input("7C 距離 (公尺)", value=0.0, step=10.0, key="back_7c")

    back_has_passive = st.checkbox("有經過 DC 被動元件", value=False, key="back_passive")
    b_pass_l, b_pass_h = 0.0, 0.0
    b_p_type, b_p_port = "無", ""
    if back_has_passive:
        b_p_type = st.selectbox("被動元件型號", ["DC2 (兩路)", "DC3 (三路)", "DC8 (兩路特殊)"], key="back_p_type")
        b_p_port = st.selectbox("埠選擇", ["3.5dB 埠", "7dB 埠"], key="back_p_port")
        b_pass_l, b_pass_h, _ = get_passive_loss(b_p_type, b_p_port)

    b_loss_500_l = (2.5 / 100.0) * math.sqrt(261.0 / 750.0) * back_dist_500
    b_loss_500_h = (5.5 / 100.0) * math.sqrt(975.0 / 750.0) * back_dist_500
    b_loss_7c_l = (4.5 / 100.0) * math.sqrt(261.0 / 750.0) * back_dist_7c
    b_loss_7c_h = (14.0 / 100.0) * math.sqrt(975.0 / 750.0) * back_dist_7c

    total_back_main_loss_l = b_loss_500_l + b_loss_7c_l
    total_back_main_loss_h = b_loss_500_h + b_loss_7c_h

    if measured_low == 0.0 and measured_high == 0.0:
        implied_orig_low, implied_orig_high = 0.0, 0.0
        diff_low, diff_high = 0.0, 0.0
    else:
        implied_orig_low = measured_low + total_back_tap_loss_l + b_pass_l + total_back_main_loss_l
        implied_orig_high = measured_high + total_back_tap_loss_h + b_pass_h + total_back_main_loss_h
        diff_low = std_low - implied_orig_low
        diff_high = std_high - implied_orig_high

    st.markdown("---")
    st.subheader("🎯 往回推算與設備標準比對結果")
    col_br1, col_br2 = st.columns(2)
    col_br1.metric(label="🚀 推算起點低頻", value=f"{implied_orig_low:.1f} dBμV", delta=f"標準差: {-diff_low:+.1f} dB" if measured_low > 0 else None, delta_color="inverse")
    col_br2.metric(label="🚀 推算起點高頻", value=f"{implied_orig_high:.1f} dBμV", delta=f"標準差: {-diff_high:+.1f} dB" if measured_high > 0 else None, delta_color="inverse")

    if measured_low > 0 or measured_high > 0:
        st.markdown("### 📋 現場智能診斷與巡查建議")
        # 將異常門檻從 5 dB 放寬至 10 dB，避免一般線路微幅誤差就頻繁跳出警告
        if diff_low > 10.0 or diff_high > 10.0:
            st.error(f"⚠️ **【顯著衰減警告】** 推算起點訊號低於設備標準輸出超過 10 dB（低頻落差 {diff_low:.1f} dB / 高頻落差 {diff_high:.1f} dB）。中間段落可能有非預期的較大損耗，建議留意！")
        else:
            st.success("✅ **【訊號正常】** 推算起點訊號與設備標準輸出落差在 10 dB 容許範圍內，線路與接頭狀況良好。")

    with st.expander("🔍 檢視逆向回推明細"):
        st.write(f"- 來源設備標準: 低頻 {std_low} / 高頻 {std_high} dBμV")
        st.write(f"- 儀表量測值: 低頻 {measured_low} / 高頻 {measured_high} dBμV")
        st.write(f"- 總經過 TAP 數量: {int(back_num_taps)} 顆 (目標量測 TAP: {back_target_tap_name})")
        st.write(f"- TAP 串接累計補回損耗: 低頻 {total_back_tap_loss_l:.1f} dB / 高頻 {total_back_tap_loss_h:.1f} dB")
        if back_has_passive:
            st.write(f"- DC 被動元件 ({b_p_type} - {b_p_port}): 補回 {b_pass_l} / {b_pass_h} dB")
        st.write(f"- 混用主線損耗補回: 500P3 ({back_dist_500}m) + 7C ({back_dist_7c}m) -> 低頻 +{total_back_main_loss_l:.2f} dB / 高頻 +{total_back_main_loss_h:.2f} dB")

# 頁面最下方正式著作宣告
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray; font-size: 0.85em;'>"
    "© 2026 CATV Engineering Tool | Architecture & Concept by Guan-Chen"
    "</div>", 
    unsafe_allow_html=True
)
