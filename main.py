import streamlit as st
from google import genai
import os
import json
import requests

KEY_FILE = ".gemini_key"
PROFILE_FILE = "user_profile.json"

def save_data(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_data(filename, default_value):
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return default_value
    return default_value

saved_key = load_data(KEY_FILE, "")
saved_profile = load_data(PROFILE_FILE, {"skills": "", "conditions": ""})

st.title("転職AIスカウター（β版）")
st.warning("【注意事項】転職サイトの「非公開求人」や、機密保持契約（NDA）に触れる情報の入力はお控えください。本ツールに入力されたデータはGoogleのGemini APIに送信されます。入力によるいかなるトラブルも開発者は責任を負いません。")

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
job_info = st.text_area("求人票のテキスト、または企業HPのURLを貼り付けてください。", height=200)

if st.button("🔥 AIで分析実行"):
    if not user_api_key:
        st.error("APIキーを設定してください")
    elif user_skills and job_info:
        with st.spinner("分析企業の情報を収集中..."):

            # URL判定 & 読み込みロジック
            final_job_info = ""

            if job_info.startswith("http"):
                st.info("URLが入力されました。内容を取得中...")
                try:
                    jina_url = f"https://r.jina.ai/{job_info}"
                    headers = {"X-Return-Format": "markdown"}
                    response = requests.get(jina_url, headers=headers, timeout=20)
                    response.raise_for_status()
                    final_job_info = response.text
                    st.success("URLから情報を取得しました！")
                except Exception as e:
                    st.error(f"URLの内容を取得できませんでした: {e}")
                    final_job_info = ""
            else:
                final_job_info = job_info

            try:
                client = genai.Client(api_key=user_api_key)
                
                # --- プロンプト ---
                prompt = f"""
                あなたは的確なキャリアコンサルタントです。
                以下の情報を元に、忖度なしで分析し、
                **必ず以下のJSON形式の文字列のみ**で出力してください。Markdown表記や解説は不要です。
                求人情報から読み取れない項目は「記載なし」としてください。

                ```json
                {{
                    "total_match": 総合マッチ度(%)（数値のみ）,
                    "corporate_info": {{
                    "company_name": "企業名",
                    "philosophy": "企業理念",
                    "desired_talent": "企業が求めている人材",
                    "common_tech": "企業でよく使われる技術",
                    "products_services": "その企業が何を提供している会社か",
                    "strong_industries": "どこの業界・業種に強いのか"
                    }}
                    "salary_min": 想定オファー年収の下限(万円)（数値のみ）,
                    "salary_max": 想定オファー年収の上限(万円)（数値のみ）,
                    "salary_reason": "年収算出の根拠",
                    "tech_stack": [
                        {{ "name": "言語/技術名1", "match": "合致度(A/B/C)" }},
                        {{ "name": "言語/技術名2", "match": "合致度(A/B/C)" }}
                    ],
                    "pros": ["メリット1", "メリット2"],
                    "cons": ["デメリット1", "デメリット2"],
                    "darkness_risks": ["面接で確認すべき「事項」1", "「事項」2"]
                }}
                ```
                
                【求職者スキル】: {user_skills}
                【希望条件】: {user_conditions}
                【求人情報】: {job_info}
                """
                
                # 💡 推論の実行（モデル名も最新の 'gemini-2.5-flash' などを使用）
                response = client.models.generate_content(
                    model='gemini-3-flash-preview',
                    contents=prompt
                )
            except Exception as e:
            # エラーが起きた場合は画面に表示してデバッグしやすくする
                st.error(f"エラーが発生しました: {e}")

            st.success("分析完了！")
            try:
                # 1. AIの出力（JSONテキスト）をPythonの辞書に変換
                result = json.loads(response.text)
                
                # 2. 視覚化の実装
                
                # --- 総合マッチ度（ゲージチャート） ---
                st.subheader("1. 総合マッチ度")
                # Streamlit標準のprogress barで簡易的に表現
                st.progress(result["total_match"] / 100)
                st.write(f"### 🔥 {result['total_match']}%")
                
                st.divider()
                
                # --- 企業基本情報 ---
                st.subheader("🏢 企業基本情報")
                c_info = result.get("corporate_info", {})
                st.markdown(f"""
                * **企業名:** {c_info.get('company_name', '記載なし')}
                * **企業理念:** {c_info.get('philosophy', '記載なし')}
                * **提供サービス:** {c_info.get('products_services', '記載なし')}
                * **得意な業界・業種:** {c_info.get('strong_industries', '記載なし')}
                * **求める人材像:** {c_info.get('desired_talent', '記載なし')}
                * **主要技術:** {c_info.get('common_tech', '記載なし')}
                """)

                # --- 想定オファー年収（カラムレイアウト） ---
                st.subheader("2. 想定オファー年収 (万円)")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("下限", f"{result['salary_min']}万")
                with col2:
                    st.metric("上限", f"{result['salary_max']}万")
                st.caption(f"💡 根拠: {result['salary_reason']}")
                
                st.divider()
                
                # --- 技術スタック合致度（表形式） ---
                st.subheader("3. 主要な技術・言語スタック")
                if result["tech_stack"]:
                    import pandas as pd
                    # データを表に変換して表示
                    df = pd.DataFrame(result["tech_stack"])
                    st.dataframe(df, use_container_width=True)
                else:
                    st.write("求人票から具体的な技術情報が読み取れませんでした。")
                
                st.divider()
                
                # --- メリット・デメリット・（タブで切り替え） ---
                st.subheader("4. 忖度なしの実態分析")
                tab1, tab2, tab3 = st.tabs(["👍 メリット", "👎 デメリット", "？ 面接での確認事項"])
                
                with tab1:
                    for p in result["pros"]:
                        st.write(f"✅ {p}")
                with tab2:
                    for c in result["cons"]:
                        st.write(f"⚠️ {c}")
                with tab3:
                    for d in result["darkness_risks"]:
                        st.warning(f"{d}")

            except json.JSONDecodeError:
                # AIがJSON形式で出力しなかった場合
                st.error("AIの出力形式が正しくありませんでした。テキストで表示します。")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")