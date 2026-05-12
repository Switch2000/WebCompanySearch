import streamlit as st
import pandas as pd

def show_match_score(result: dict):
    st.subheader("1. 総合マッチ度")
    score = result["total_match"]
    st.progress(score / 100)
    st.write(f"### {score}%")

def show_corporate_info(result: dict):
    st.subheader("🏢 企業基本情報")
    c = result.get("corporate_info", {})
    st.markdown(f"""
    - **企業名:** {c.get('company_name', '記載なし')}
    - **企業理念:** {c.get('philosophy', '記載なし')}
    - **提供サービス:** {c.get('products_services', '記載なし')}
    - **得意な業界・業種:** {c.get('strong_industries', '記載なし')}
    - **求める人材像:** {c.get('desired_talent', '記載なし')}
    - **主要技術:** {c.get('common_tech', '記載なし')}
    """)

def show_salary(result: dict):
    st.subheader("2. 想定オファー年収 (万円)")
    col1, col2 = st.columns(2)
    col1.metric("下限", f"{result['salary_min']}万")
    col2.metric("上限", f"{result['salary_max']}万")
    st.caption(f"💡 根拠: {result['salary_reason']}")
    st.divider()

def show_tech_stack(result: dict):
    st.subheader("3. 技術スタック合致度")
    stack = result.get("tech_stack", [])
    if stack:
        st.dataframe(pd.DataFrame(stack), use_container_width=True)
    else:
        st.write("技術情報が読み取れませんでした。")
    st.divider()

def show_analysis_tabs(result: dict):
    st.subheader("4. 忖度なしの実態分析")
    tab1, tab2, tab3 = st.tabs(["👍 メリット", "👎 デメリット", "？ 面接での確認事項"])
    with tab1:
        for p in result.get("pros", []):
            st.write(f"✅ {p}")
    with tab2:
        for c in result.get("cons", []):
            st.write(f"⚠️ {c}")
    with tab3:
        for d in result.get("darkness_risks", []):
            st.warning(d)
    st.caption("※上記は求人情報からの推測に基づく分析結果です。これらを踏まえてさらに深掘りの調査や確認を行うことをおすすめします。")

def show_result(result: dict):
    show_match_score(result)
    show_corporate_info(result)
    show_salary(result)
    show_tech_stack(result)
    show_analysis_tabs(result)