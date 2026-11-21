import re
from io import BytesIO
from collections import Counter

import pandas as pd
import streamlit as st
from PIL import Image, ImageOps, ImageEnhance

st.set_page_config(page_title="Baccarat Result Analyzer", page_icon="🃏", layout="wide")

THEORY = {"Player": 0.4462, "Banker": 0.4586, "Tie": 0.0952}
COLORS = {"Player": "#2684ff", "Banker": "#e05252", "Tie": "#22a06b"}

if "history" not in st.session_state:
    st.session_state.history = []

def normalize_result(value):
    v = str(value).strip().lower()
    mapping = {"p": "Player", "player": "Player", "b": "Banker", "banker": "Banker",
               "t": "Tie", "tie": "Tie"}
    return mapping.get(v)

def get_probs(history):
    # Lightly smooth observed frequencies toward standard 8-deck theoretical odds.
    counts = Counter(history)
    n = len(history)
    strength = 12
    denom = n + strength
    return {k: (counts[k] + strength * THEORY[k]) / denom for k in THEORY}

def streak_info(history):
    if not history:
        return "—", 0
    last = history[-1]
    count = 0
    for item in reversed(history):
        if item != last:
            break
        count += 1
    return last, count

def read_ocr(image):
    try:
        import pytesseract
        img = ImageOps.grayscale(image)
        img = ImageEnhance.Contrast(img).enhance(2.0)
        text = pytesseract.image_to_string(img, config="--psm 6")
        words = re.findall(r"\b(player|banker|tie)\b", text, flags=re.I)
        return [normalize_result(w) for w in words], text
    except Exception as exc:
        return [], f"OCR unavailable: {exc}"

st.title("🃏 Baccarat Result Analyzer")
st.caption("Track results, review patterns, and inspect probability estimates. This tool does not predict or guarantee future outcomes.")

with st.sidebar:
    st.header("Add a result")
    choice = st.radio("Hand result", ["Player", "Banker", "Tie"], horizontal=True)
    if st.button("＋ Add result", use_container_width=True):
        st.session_state.history.append(choice)
        st.rerun()
    st.divider()
    st.subheader("Manage history")
    if st.button("Undo last result", use_container_width=True, disabled=not st.session_state.history):
        st.session_state.history.pop()
        st.rerun()
    if st.button("Clear all results", use_container_width=True, disabled=not st.session_state.history):
        st.session_state.history = []
        st.rerun()
    st.caption("Results are kept in this browser session. Download CSV to save a copy.")

tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🖼️ Screenshot OCR", "📁 Export"])

with tab1:
    history = st.session_state.history
    counts = Counter(history)
    total = len(history)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total hands", total)
    c2.metric("Player", counts["Player"])
    c3.metric("Banker", counts["Banker"])
    c4.metric("Tie", counts["Tie"])

    st.subheader("Observed results")
    if total:
        stats = pd.DataFrame({
            "Result": list(THEORY.keys()),
            "Count": [counts[k] for k in THEORY],
            "Observed %": [counts[k] / total * 100 for k in THEORY],
            "Theoretical %": [THEORY[k] * 100 for k in THEORY],
        })
        st.dataframe(stats, hide_index=True, use_container_width=True)
        st.bar_chart(stats.set_index("Result")[["Count"]])
        last, run = streak_info(history)
        st.info(f"Current streak: **{last} × {run}**")
        st.write("**Recent hands (oldest → newest)**")
        st.write("  ".join(history[-40:]))
    else:
        st.info("Wala pang results. Mag-add ng Player, Banker, o Tie sa sidebar, o gumamit ng Screenshot OCR tab.")

    st.divider()
    st.subheader("10 sample next-hand picks")
    if total:
        probs = get_probs(history)
        pcols = st.columns(3)
        for col, key in zip(pcols, THEORY):
            col.metric(f"{key} estimate", f"{probs[key]*100:.2f}%")
        # Reproducible illustrative sample, not a predictive model.
        import random
        rng = random.Random(total * 7919 + sum(ord(x[0]) for x in history))
        labels = list(probs.keys())
        weights = [probs[k] for k in labels]
        picks = rng.choices(labels, weights=weights, k=10)
        grid = st.columns(5)
        for i, pick in enumerate(picks, start=1):
            grid[(i-1) % 5].markdown(f"**{i}. {pick}**")
        st.caption("These are illustrative samples drawn from smoothed estimates—not ten reliable predictions. Baccarat hands are independent; streaks and past results do not establish what comes next.")
    else:
        st.caption("Maglagay muna ng kahit isang result para makabuo ng sample picks.")

with tab2:
    st.subheader("Upload a baccarat screenshot")
    uploaded = st.file_uploader("Choose PNG, JPG, or JPEG", type=["png", "jpg", "jpeg"])
    if uploaded:
        image = Image.open(uploaded).convert("RGB")
        st.image(image, caption="Uploaded screenshot", use_container_width=True)
        detected, raw_text = read_ocr(image)
        if detected:
            st.success(f"Detected {len(detected)} text result(s). Please verify before adding.")
            st.code("  ".join(detected))
            corrected = st.text_input("Edit detected sequence if needed (P/B/T or Player/Banker/Tie, separated by commas)", value=", ".join(detected))
            if st.button("Confirm and add OCR results"):
                parsed = [normalize_result(x) for x in re.split(r"[,\s]+", corrected) if x.strip()]
                if parsed and all(parsed):
                    st.session_state.history.extend(parsed)
                    st.success(f"Added {len(parsed)} confirmed result(s).")
                    st.rerun()
                else:
                    st.error("May invalid entry. Gumamit lamang ng P, B, T, Player, Banker, o Tie.")
        else:
            st.warning("Walang malinaw na PLAYER/BANKER/TIE text na nakita. Kung colored circles o bead-road lang ang screenshot, hindi ito maaasahang nade-decode ng text OCR. I-enter nang manual ang results.")
        with st.expander("OCR raw text / diagnostic"):
            st.text(raw_text or "No text detected.")

with tab3:
    st.subheader("Download your results")
    if st.session_state.history:
        export_df = pd.DataFrame({
            "Hand": range(1, len(st.session_state.history) + 1),
            "Result": st.session_state.history
        })
        csv = export_df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download CSV", data=csv, file_name="baccarat_results.csv", mime="text/csv")
        st.dataframe(export_df.tail(30), use_container_width=True, hide_index=True)
    else:
        st.info("Wala pang data na ie-export.")
