import streamlit as st
import math

# 設定網頁標題與排版
st.set_page_config(page_title="永佳樂 CATV 現場工程訊號計算器", page_icon="📺", layout="centered")

st.title("📺 永佳樂 CATV 工程訊號計算器")
st.markdown("5C/7C/500P3 線損、8路/4路 TAP、 DC 串接與訊號回推")
st.markdown("---")

# 選擇計算模式
calc_mode = st.radio("選擇計算模式", ["⚙️ 線上預估 (起點 終端)", "🔍 訊號回推 (儀表量測 回推起點)"], horizontal=True)

st.markdown("---")

def get_freq_col_index(freq):
    if freq <= 15: return 0
    elif freq <= 40: return 1
    elif freq <= 250: return 2
    elif freq <= 550: return 3
    elif freq <= 750: return 4
    elif freq <= 862: return 5
    elif freq <= 1006: return 6
    else: return 7

def get_cable_loss_per_100m(cable_type, freq):
    if cable_type == "500P3":
        if freq <= 55: return 0.52 + (1.80 - 0.52) * (freq / 55.0)
        elif freq <= 211: return 1.80 + (3.55 - 1.80) * ((freq - 55) / (211 - 55))
        elif freq <= 300: return 3.55 + (4.30 - 3.55) * ((freq - 211) / (300 - 211))
        elif freq <= 500: return 4.30 + (5.68 - 4.30) * ((freq - 300) / (500 - 300))
        elif freq <= 750: return 5.68 + (7.09 - 5.68) * ((freq - 500) / (750 - 500))
        elif freq <= 870: return 7.09 + (7.69 - 7.09) * ((freq - 750) / (870 - 750))
        elif freq <= 1000: return 7.69 + (8.30 - 7.69) * ((freq - 870) / (1000 - 870))
        else: return 8.30 * math.sqrt(freq / 1000.0)
    elif cable_type == "7C":
        if freq <= 55: return 1.18 + (3.12 - 1.18) * (freq / 55.0)
        elif freq <= 211: return 3.12 + (5.95 - 3.12) * ((freq - 55) / (211 - 55))
        elif freq <= 300: return 5.95 + (7.12 - 5.95) * ((freq - 211) / (300 - 211))
        elif freq <= 500: return 7.12 + (9.35 - 7.12) * ((freq - 300) / (500 - 300))
        elif freq <= 750: return 9.35 + (11.75 - 9.35) * ((freq - 500) / (750 - 500))
        elif freq <= 870: return 11.75 + (12.80 - 11.75) * ((freq - 750) / (870 - 750))
        elif freq <= 1000: return 12.80 + (13.88 - 12.80) * ((freq - 870) / (1000 - 870))
        else: return 13.88 * math.sqrt(freq / 1000.0)
    else: # 5C
        if freq <= 55: return 1.87 + (4.94 - 1.87) * (freq / 55.0)
        elif freq <= 211: return 4.94 + (9.43 - 4.94) * ((freq - 55) / (211 - 55))
        elif freq <= 300: return 9.43 + (11.25 - 9.43) * ((freq - 211) / (300 - 211))
        elif freq <= 500: return 11.25 + (14.80 - 11.25) * ((freq - 300) / (500 - 300))
        elif freq <= 750: return 14.80 + (18.44 - 14.80) * ((freq - 500) / (750 - 500))
        elif freq <= 870: return 18.44 + (19.99 - 18.44) * ((freq - 750) / (870 - 750))
        elif freq <= 1000: return 19.99 + (21.46 - 19.99) * ((freq - 870) / (1000 - 870))
        else: return 21.46 * math.sqrt(freq / 1000.0)

# TAP 插入損失
tap8_insertion_table = {
    11: [0.0, 3.6, 4.0, 4.2, 4.7, 4.9, 5.2, 5.7],
    14: [3.6, 3.6, 2.0, 2.0, 2.8, 3.5, 3.7, 4.0],
    17: [1.9, 1.9, 2.0, 2.0, 2.4, 2.4, 3.2, 3.5],
    20: [1.4, 1.4, 1.4, 1.8, 2.4, 2.4, 3.0, 3.5],
    23: [1.2, 1.2, 1.2, 1.3, 1.7, 2.2, 2.5, 2.6]
}

tap4_insertion_table = {
    8:  [1.1, 1.1, 1.1, 1.4, 1.6, 1.8, 2.4, 2.6],
    11: [3.5, 3.5, 3.9, 4.3, 4.8, 5.1, 5.1, 5.7],
    14: [1.9, 1.9, 2.0, 2.3, 2.8, 3.0, 3.9, 4.0],
    17: [1.2, 1.2, 1.3, 1.6, 2.0, 2.2, 2.7, 2.9],
    20: [1.1, 1.1, 1.1, 1.4, 1.6, 1.8, 2.4, 2.6],
    23: [0.8, 0.8, 0.9, 1.2, 1.4, 1.6, 2.0, 2.4]
}

tap_branch_table = {
    "23": (22.5, 23.5, 38.0), "20": (19.5, 20.5, 35.0), 
    "17": (16.5, 17.5, 32.0), "14": (13.5, 14.5, 29.0), 
    "11": (10.5, 11.5, 26.0), "8":  (7.5,  8.5,  23.0)
}

def get_tap_insertion_loss(tap_type, tap_db_val, freq):
    col_idx = get_freq_col_index(freq)
    if "8路" in tap_type:
        return tap8_insertion_table.get(tap_db_val, [1.5]*8)[col_idx]
    else:
        return tap4_insertion_table.get(tap_db_val, [1.5]*8)[col_idx]

def get_single_dc_loss(passive_type, selected_port, freq):
    if "DC2" in passive_type:
        return 3.5, 3.5, 3.5
    elif "DC3" in passive_type:
        if "3.5" in selected_port:
            return 3.5, 3.8, 3.5
        else:
            return 7.0, 7.5, 7.0
    elif "DC8" in passive_type:
        if "8" in selected_port:
            return 8.0, 8.5, 8.0
        else:
            return 1.0, 1.5, 1.0
    return 0.0, 0.0, 0.0

if calc_mode == "⚙️ 線上預估 (起點 終端)":
    st.subheader("1. 選擇主動元件")
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
        ],
        index=0
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

    target_low_freq = 261.0
    target_high_freq = 975.0

    st.markdown("---")
    st.subheader("2. 主幹線線材 (500P3 / 7C)")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        dist_500 = st.number_input("500P3 同軸幹線距離 (公尺)", value=0.0, step=10.0)
    with col_c2:
        dist_7c = st.number_input("7C 同軸電纜距離 (公尺)", value=0.0, step=10.0)

    loss_500_low = (get_cable_loss_per_100m("500P3", target_low_freq) / 100.0) * dist_500
    loss_500_high = (get_cable_loss_per_100m("500P3", target_high_freq) / 100.0) * dist_500
    loss_500_up = (0.8 / 100.0) * dist_500

    loss_7c_low = (get_cable_loss_per_100m("7C", target_low_freq) / 100.0) * dist_7c
    loss_7c_high = (get_cable_loss_per_100m("7C", target_high_freq) / 100.0) * dist_7c
    loss_7c_up = (1.5 / 100.0) * dist_7c

    total_main_loss_low = loss_500_low + loss_7c_low
    total_main_loss_high = loss_500_high + loss_7c_high
    total_main_loss_up = loss_500_up + loss_7c_up

    st.markdown("---")
    st.subheader("3. 外部 DC 被動元件選擇（支援混合型多顆串接）")
    has_passive = st.checkbox("是否經過主線 DC 被動元件", value=False)
    total_passive_loss_low, total_passive_loss_high, total_passive_up_effect = 0.0, 0.0, 0.0
    dc_summary_list = []

    if has_passive:
        num_dcs = st.number_input("總共經過幾顆 DC？", min_value=1, max_value=10, value=1, step=1, key="num_dcs")
        for j in range(int(num_dcs)):
            st.write(f"**第 {j+1} 顆 DC**")
            d_col1, d_col2 = st.columns(2)
            with d_col1:
                dc_model = st.selectbox(f"型號 #{j+1}", ["DC2 (兩路)", "DC3 (三路)", "DC8 (兩路不平衡)"], key=f"dc_model_{j}", index=0)
            with d_col2:
                if "DC2" in dc_model:
                    dc_port = "3.5dB 埠"
                elif "DC3" in dc_model:
                    dc_port = st.selectbox(f"埠 #{j+1}", ["3.5dB 埠", "7dB 埠"], key=f"dc_port_3_{j}", index=0)
                else:
                    dc_port = st.selectbox(f"埠 #{j+1}", ["8dB 埠", "1dB 埠"], key=f"dc_port_8_{j}", index=0)
            
            pl_l, pl_h, pl_up = get_single_dc_loss(dc_model, dc_port, target_low_freq)
            _, ph_h, _ = get_single_dc_loss(dc_model, dc_port, target_high_freq)
            
            total_passive_loss_low += pl_l
            total_passive_loss_high += ph_h
            total_passive_up_effect += pl_up
            dc_summary_list.append(f"第{j+1}顆 {dc_model} ({dc_port})")

    st.markdown("---")
    st.subheader("4. TAP 串接級數選擇")
    num_taps = st.number_input("這條路徑總共經過幾顆 TAP？ (設為 0 則不經過 TAP)", min_value=0, max_value=10, value=0, step=1)
    total_tap_loss_low, total_tap_loss_high = 0.0, 0.0
    final_tap_up_val = orig_up

    for i in range(int(num_taps)):
        st.write(f"**第 {i+1} 顆 TAP**")
        col_t1, col_t2, col_t3 = st.columns([1, 1, 1])
        with col_t1:
            t_category = st.selectbox("規格", ["8路 TAP", "4路 TAP"], key=f"t_cat_{i}", index=0)
        with col_t2:
            if t_category == "4路 TAP":
                t_db_val = st.selectbox("分歧值 (dB)", [23, 20, 17, 14, 11, 8], key=f"t_db_{i}", index=0)
            else:
                t_db_val = st.selectbox("分歧值 (dB)", [23, 20, 17, 14, 11], key=f"t_db_{i}", index=0)
        with col_t3:
            is_target = st.checkbox(f"這是目標測量點？", value=(i == num_taps - 1), key=f"is_target_{i}")
        
        branch_l, branch_h, branch_up = tap_branch_table[str(t_db_val)]
        
        if is_target:
            total_tap_loss_low += branch_l
            total_tap_loss_high += branch_h
            final_tap_up_val = branch_up
        else:
            pass_loss_l = get_tap_insertion_loss(t_category, t_db_val, target_low_freq)
            pass_loss_h = get_tap_insertion_loss(t_category, t_db_val, target_high_freq)
            total_tap_loss_low += pass_loss_l
            total_tap_loss_high += pass_loss_h

    st.markdown("---")
    st.subheader("5. 用戶端室內線與室內分配器")
    col_in1, col_in2 = st.columns(2)
    with col_in1:
        indoor_splitter = st.selectbox("室內分配器選擇", ["無", "DC2 (二分配)", "DC3 (三分配 - 3.5dB埠)", "DC3 (三分配 - 7dB埠)"], index=0)
    with col_in2:
        indoor_length = st.number_input("室內 5C 線長 (公尺)", value=0.0, step=5.0)

    splitter_low, splitter_high, splitter_up = 0.0, 0.0, 0.0
    if indoor_splitter == "DC2 (二分配)":
        splitter_low, splitter_high, splitter_up = 3.5, 3.8, 3.5
    elif indoor_splitter == "DC3 (三分配 - 3.5dB埠)":
        splitter_low, splitter_high, splitter_up = 3.5, 3.8, 3.5
    elif indoor_splitter == "DC3 (三分配 - 7dB埠)":
        splitter_low, splitter_high, splitter_up = 7.0, 7.5, 7.0

    indoor_loss_low = (get_cable_loss_per_100m("5C", target_low_freq) / 100.0) * indoor_length
    indoor_loss_high = (get_cable_loss_per_100m("5C", target_high_freq) / 100.0) * indoor_length
    indoor_loss_up = (2.0 / 100.0) * indoor_length

    if device_type == "請選擇設備型號..." or orig_low == 0.0:
        final_low, final_high, final_up = 0.0, 0.0, 0.0
    else:
        final_low = orig_low - total_main_loss_low - total_passive_loss_low - total_tap_loss_low - splitter_low - indoor_loss_low
        final_high = orig_high - total_main_loss_high - total_passive_loss_high - total_tap_loss_high - splitter_high - indoor_loss_high
        final_up = final_tap_up_val + splitter_up + indoor_loss_up + total_passive_up_effect + total_main_loss_up

    st.markdown("---")
    st.subheader("🎯 預期量測結果 (dBμV)")
    col_r1, col_r2, col_r3 = st.columns(3)
    col_r1.metric(label=f"📺 下行低頻 (261MHz)", value=f"{final_low:.1f} dBμV")
    col_r2.metric(label=f"📺 下行高頻 (975MHz)", value=f"{final_high:.1f} dBμV")
    col_r3.metric(label=f"🔄 上行回傳預估", value=f"{final_up:.1f} dBμV")

    st.caption("📝 **永佳樂工程技術手冊備註**：衰減值會隨溫度增減，當溫度上升，衰減值也隨上升，反之亦然 (@68°F / 20°C)")

    with st.expander("🔍 檢視詳細損耗與各段明細"):
        st.write(f"**【下行傳輸明細】**")
        st.write(f"- 設備起點: 下行低 {orig_low} dBμV / 高 {orig_high} dBμV")
        if dist_500 > 0:
            st.write(f"- 500P3 幹線損耗 ({dist_500}m): 低頻 {loss_500_low:.2f} dB / 高頻 {loss_500_high:.2f} dB")
        if dist_7c > 0:
            st.write(f"- 7C 電纜損耗 ({dist_7c}m): 低頻 {loss_7c_low:.2f} dB / 高頻 {loss_7c_high:.2f} dB")
        if has_passive and dc_summary_list:
            st.write(f"- 外部 DC 被動元件混搭總計 ({', '.join(dc_summary_list)}): 下行扣除低 {total_passive_loss_low:.2f} dB / 高 {total_passive_loss_high:.2f} dB")
        if num_taps > 0:
            st.write(f"- TAP 串接計算扣除總量: 低頻 {total_tap_loss_low:.2f} dB / 高頻 {total_tap_loss_high:.2f} dB")
        if indoor_splitter != "無":
            st.write(f"- 室內分配器 ({indoor_splitter}): 扣除 {splitter_low} dB")
        if indoor_length > 0:
            st.write(f"- 室內 5C 線損 ({indoor_length}m): 下行低 {indoor_loss_low:.2f} dB / 高 {indoor_loss_high:.2f} dB")
        
        st.markdown("---")
        st.write(f"**【其他常用頻率理論預期訊號強度 (dBμV)】**")
        sample_freqs = [309, 327, 333, 579, 585, 603, 609, 627, 633, 651, 663, 705, 870]
        for f in sample_freqs:
            l_500 = (get_cable_loss_per_100m("500P3", f) / 100.0) * dist_500
            l_7c = (get_cable_loss_per_100m("7C", f) / 100.0) * dist_7c
            l_indoor = (get_cable_loss_per_100m("5C", f) / 100.0) * indoor_length
            
            p_l_total = 0.0
            if has_passive:
                for j_idx in range(int(num_dcs)):
                    m_val = st.session_state.get(f"dc_model_{j_idx}", "DC2 (兩路)")
                    p_val = st.session_state.get(f"dc_port_3_{j_idx}" if "DC2" in m_val or "DC3" in m_val else f"dc_port_8_{j_idx}", "3.5dB 埠")
                    pl_single, _, _ = get_single_dc_loss(m_val, p_val, f)
                    p_l_total += pl_single

            t_loss_f = 0.0
            for idx in range(int(num_taps)):
                t_cat_val = st.session_state.get(f"t_cat_{idx}", "8路 TAP")
                t_db_val = st.session_state.get(f"t_db_{idx}", 23)
                if idx == num_taps - 1:
                    t_loss_f += tap_branch_table[str(t_db_val)][0]
                else:
                    t_loss_f += get_tap_insertion_loss(t_cat_val, t_db_val, f)
            
            orig_f = orig_low + (f - 261.0) * 0.01
            final_f = orig_f - l_500 - l_7c - p_l_total - t_loss_f - splitter_low - l_indoor
            st.text(f"頻率 {f:3d} MHz ➔ 預期強度: {final_f:.1f} dBμV")

else:
    # 現場逆向回推模式
    st.subheader("🔍 現場儀表量測值 往回推算起點訊號與狀態診斷")
    st.write("請輸入現場儀表量測到的訊號、設定經過的路徑元件與距離，系統將自動精準回推起點訊號：")

    ref_device = st.selectbox(
        "選擇來源設備標準輸出基準",
        [
            "光機 / 幹線放大器 (標準: 下行 95.0 / 104.0 dBμV)",
            "延伸放大器 (標準: 下行 91.0 / 100.0 dBμV)",
            "手動自訂標準"
        ],
        index=0
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
        measured_low = st.number_input("儀表量測下行低頻 (261MHz) (dBμV)", value=0.0, step=0.5)
    with col_m2:
        measured_high = st.number_input("儀表量測下行高頻 (975MHz) (dBμV)", value=0.0, step=0.5)

    st.markdown("---")
    st.write("**【設定測量點的 TAP 串接結構】**")
    back_num_taps = st.number_input("這條路徑總共經過幾顆 TAP？", min_value=1, max_value=10, value=1, step=1, key="back_num_taps")
    
    total_back_tap_loss_l = 0.0
    total_back_tap_loss_h = 0.0
    back_target_tap_name = ""

    for i in range(int(back_num_taps)):
        st.write(f"**第 {i+1} 顆 TAP**")
        col_bt1, col_bt2, col_bt3 = st.columns([1, 1, 1])
        with col_bt1:
            bt_cat = st.selectbox("規格", ["8路 TAP", "4路 TAP"], key=f"back_t_cat_{i}", index=0)
        with col_bt2:
            if bt_cat == "4路 TAP":
                bt_db = st.selectbox("分歧值 (dB)", [23, 20, 17, 14, 11, 8], key=f"back_t_db_{i}", index=0)
            else:
                bt_db = st.selectbox("分歧值 (dB)", [23, 20, 17, 14, 11], key=f"back_t_db_{i}", index=0)
        with col_bt3:
            bt_is_target = st.checkbox(f"這是量測點？", value=(i == back_num_taps - 1), key=f"back_is_target_{i}")
        
        branch_l, branch_h, _ = tap_branch_table[str(bt_db)]
        if bt_is_target:
            total_back_tap_loss_l += branch_l
            total_back_tap_loss_h += branch_h
            back_target_tap_name = f"{bt_cat} {bt_db}dB"
        else:
            total_back_tap_loss_l += get_tap_insertion_loss(bt_cat, bt_db, 261.0)
            total_back_tap_loss_h += get_tap_insertion_loss(bt_cat, bt_db, 975.0)

    st.markdown("---")
    st.write("反推主線混用距離：")
    col_bc1, col_bc2 = st.columns(2)
    with col_bc1:
        back_dist_500 = st.number_input("500P3 距離 (公尺)", value=0.0, step=10.0, key="back_500")
    with col_bc2:
        back_dist_7c = st.number_input("7C 距離 (公尺)", value=0.0, step=10.0, key="back_7c")

    back_has_passive = st.checkbox("有經過 DC 被動元件", value=False, key="back_passive")
    total_back_pass_l, total_back_pass_h = 0.0, 0.0
    back_dc_summary = []
    num_back_dcs = 1

    if back_has_passive:
        num_back_dcs = st.number_input("總共經過幾顆 DC？", min_value=1, max_value=10, value=1, step=1, key="back_num_dcs")
        for k in range(int(num_back_dcs)):
            st.write(f"**第 {k+1} 顆 DC**")
            bp_col1, bp_col2 = st.columns(2)
            with bp_col1:
                b_p_type = st.selectbox(f"型號 #{k+1}", ["DC2 (兩路)", "DC3 (三路)", "DC8 (兩路不平衡)"], key=f"back_p_type_{k}", index=0)
            with bp_col2:
                if "DC2" in b_p_type:
                    b_p_port = "3.5dB 埠"
                elif "DC3" in b_p_type:
                    b_p_port = st.selectbox(f"埠 #{k+1}", ["3.5dB 埠", "7dB 埠"], key=f"back_p_port_3_{k}", index=0)
                else:
                    b_p_port = st.selectbox(f"埠 #{k+1}", ["8dB 埠", "1dB 埠"], key=f"back_p_port_8_{k}", index=0)
            
            pl_s, _, _ = get_single_dc_loss(b_p_type, b_p_port, 261.0)
            ph_s, _, _ = get_single_dc_loss(b_p_type, b_p_port, 975.0)
            total_back_pass_l += pl_s
            total_back_pass_h += ph_s
            back_dc_summary.append(f"第{k+1}顆 {b_p_type} ({b_p_port})")

    b_loss_500_l = (get_cable_loss_per_100m("500P3", 261.0) / 100.0) * back_dist_500
    b_loss_500_h = (get_cable_loss_per_100m("500P3", 975.0) / 100.0) * back_dist_500
    b_loss_7c_l = (get_cable_loss_per_100m("7C", 261.0) / 100.0) * back_dist_7c
    b_loss_7c_h = (get_cable_loss_per_100m("7C", 975.0) / 100.0) * back_dist_7c

    total_back_main_loss_l = b_loss_500_l + b_loss_7c_l
    total_back_main_loss_h = b_loss_500_h + b_loss_7c_h

    if measured_low == 0.0 and measured_high == 0.0:
        implied_orig_low, implied_orig_high = 0.0, 0.0
        diff_low, diff_high = 0.0, 0.0
    else:
        implied_orig_low = measured_low + total_back_tap_loss_l + total_back_pass_l + total_back_main_loss_l
        implied_orig_high = measured_high + total_back_tap_loss_h + total_back_pass_h + total_back_main_loss_h
        diff_low = std_low - implied_orig_low
        diff_high = std_high - implied_orig_high

    st.markdown("---")
    st.subheader("🎯 往回推算與設備標準比對結果")
    col_br1, col_br2 = st.columns(2)
    col_br1.metric(label="🚀 推算起點低頻 (261MHz)", value=f"{implied_orig_low:.1f} dBμV", delta=f"標準差: {-diff_low:+.1f} dB" if measured_low > 0 else None, delta_color="inverse")
    col_br2.metric(label="🚀 推算起點高頻 (975MHz)", value=f"{implied_orig_high:.1f} dBμV", delta=f"標準差: {-diff_high:+.1f} dB" if measured_high > 0 else None, delta_color="inverse")

    st.caption("📝 ：衰減值會隨溫度增減，當溫度上升，衰減值也隨上升，反之亦然 (@68°F / 20°C)")

    if measured_low > 0 or measured_high > 0:
        st.markdown("### 📋 現場診斷與巡查建議")
        if abs(diff_low) > 3.0 or abs(diff_high) > 3.0:
            st.error(f"⚠️ **【顯著衰減警告】** 推算起點訊號與設備標準輸出落差超過 3 dB（低頻落差 {abs(diff_low):.1f} dB / 高頻落差 {abs(diff_high):.1f} dB）。超出 NCC 規範，中間段落可能有異常損耗或增益偏離！")
        else:
            st.success("✅ **【訊號正常】** 推算起點訊號與設備標準輸出落差在 3 dB 容許範圍內，符合 NCC 標準與現場實務要求。")

    with st.expander("🔍 檢視逆向回推明細"):
        st.write(f"- 來源設備標準: 低頻 {std_low} / 高頻 {std_high} dBμV")
        st.write(f"- 儀表量測值: 低頻 {measured_low} / 高頻 {measured_high} dBμV")
        st.write(f"- 總經過 TAP 數量: {int(back_num_taps)} 顆 (目標量測 TAP: {back_target_tap_name})")
        st.write(f"- TAP 串接補回損耗: 低頻 {total_back_tap_loss_l:.2f} dB / 高頻 {total_back_tap_loss_h:.2f} dB")
        if back_has_passive and back_dc_summary:
            st.write(f"- DC 被動元件混搭總計 ({', '.join(back_dc_summary)}): 補回低 {total_back_pass_l:.2f} dB / 高 {total_back_pass_h:.2f} dB")
        st.write(f"- 混用主線損耗補回: 500P3 ({back_dist_500}m) + 7C ({back_dist_7c}m) -> 低頻 +{total_back_main_loss_l:.2f} dB / 高頻 +{total_back_main_loss_h:.2f} dB")

# 頁面最下方正式著作宣告
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray; font-size: 0.85em;'>"
    "© 2026 永佳樂 CATV Engineering Tool | Architecture & Concept by Guan-Chen"
    "</div>", 
    unsafe_allow_html=True
)
