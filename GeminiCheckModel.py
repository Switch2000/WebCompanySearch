import google.generativeai as genai

# APIキーをセット
KEY_FILE = ".gemini_key"
genai.configure(api_key=open(KEY_FILE).read().strip())

print("🔍 現在利用可能なテキスト生成モデル一覧:")
# 使えるモデルをすべて取得してループ表示
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)