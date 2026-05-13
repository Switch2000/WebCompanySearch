import streamlit as st
from strage import save_data, load_data
from analyzer import analyze, KEYWORD_MAP
from ui_components import show_result

KEY_FILE = ".env"
PROFILE_FILE = "user_profile.json"

saved_key = load_data(KEY_FILE, "")
saved_profile = load_data(PROFILE_FILE, {"skills": "", "conditions": ""})

st.title("転職AIスカウター（β版）")
st.warning("【注意事項】転職サイトの「非公開求人」や、NDAに触れる情報の入力はお控えください。入力データはGemini APIに送信されます。")

st.sidebar.title("Settings")
user_api_key = st.sidebar.text_input("🔑 Gemini APIキー", value=saved_key, type="password")
if st.sidebar.button("設定を保存"):
    save_data(KEY_FILE, user_api_key)
    st.sidebar.success("APIキーを保存しました")

st.subheader("1. あなたの情報を入力")
user_skills = st.text_area("スキル・経験", value=saved_profile["skills"], height=150)
user_conditions = st.text_area("希望条件", value=saved_profile["conditions"], height=100)
if st.button("このプロフィールを保存"):
    save_data(PROFILE_FILE, {"skills": user_skills, "conditions": user_conditions})
    st.toast("プロフィールを保存しました！")

st.divider()

st.subheader("2. ターゲット企業の情報を入力")
job_info = st.text_area("求人票のテキスト、または企業のトップページURLを入力", height=150)

# URLが入力された時のみ深掘り選択を表示
if job_info.startswith("http"):
    selected_categories = st.multiselect(
        "🔍 深掘り調査したい項目を選択してください（最大3つ）",
        options=list(KEYWORD_MAP.keys()),
        default=["🤝 採用情報・募集要項"],
        max_selections=3,
    )
else:
    selected_categories = []

if st.button("🔥 AIスカウターで分析実行"):
    if not user_api_key:
        st.error("APIキーを設定してください")
    elif not user_skills or not job_info:
        st.error("スキルと求人情報を入力してください")
    else:
        with st.spinner("分析中..."):
            result, scanned_urls, missing_categories, error = analyze(
                user_api_key, user_skills, user_conditions, job_info, selected_categories
            )

        if error:
            st.error(error)
        else:
            # URL取得結果のフィードバック表示
            if scanned_urls:
                st.success("🌐 以下のページを解析しました:\n" + "\n".join(f"- {u}" for u in scanned_urls))
            if missing_categories:
                st.warning("⚠️ 自動検出できなかった項目（トップページの情報で代替）: " + ", ".join(missing_categories))

            st.success("分析完了！")
            show_result(result)