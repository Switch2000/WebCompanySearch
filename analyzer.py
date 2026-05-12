import json
import re
import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from google import genai
from prompts import build_analysis_prompt

MODEL_NAME = "gemini-3-flash-preview"

KEYWORD_MAP = {
    "🏢 会社概要・企業情報": ['about', 'company', 'corporate', '会社概要', '企業情報'],
    "🤝 採用情報・募集要項": ['recruit', 'job', 'career', '中途採用', '求人', '募集', 'キャリア採用'],
    "👤 社員・働く環境": ['member', 'staff', 'people', 'culture', '社員', 'インタビュー', '環境'],
    "🚀 事業内容・サービス": ['service', 'business', 'product', '事業', 'サービス', 'プロダクト'],
}

def get_targeted_urls(base_url: str, selected_options: list) -> tuple[list, list]:
    """選択カテゴリに対応するURLを探索して返す"""
    found_urls = {base_url}
    missing_categories = []

    try:
        response = requests.get(base_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        all_links = soup.find_all('a', href=True)

        for option in selected_options:
            search_terms = KEYWORD_MAP[option]
            category_found = False

            for a_tag in all_links:
                href = a_tag['href'].lower()
                text = a_tag.get_text().lower()
                if any(term in href or term in text for term in search_terms):
                    found_urls.add(urljoin(base_url, a_tag['href']))
                    category_found = True
                    break

            if not category_found:
                missing_categories.append(option)

        return list(found_urls), missing_categories

    except Exception:
        return [base_url], list(selected_options)

def fetch_multiple_urls(urls: list) -> str:
    """複数URLの内容をJinaで取得して結合する"""
    combined = ""
    for url in urls:
        res = requests.get(
            f"https://r.jina.ai/{url}",
            headers={"X-Return-Format": "markdown"},
            timeout=50,
        )
        if res.status_code == 200:
            combined += f"\n\n--- 情報元: {url} ---\n\n{res.text}"
        time.sleep(1)
    return combined

def resolve_job_info(raw_input: str, selected_categories: list) -> tuple[str, list, list, str | None]:
    """
    入力がURLなら複数ページを取得、テキストならそのまま返す。
    戻り値: (テキスト, 取得したURLリスト, 未検出カテゴリリスト, エラー or None)
    """
    if not raw_input.startswith("http"):
        return raw_input, [], [], None

    try:
        urls, missing = get_targeted_urls(raw_input, selected_categories)
        text = fetch_multiple_urls(urls)
        return text, urls, missing, None
    except Exception as e:
        return "", [], [], f"情報の取得に失敗しました: {e}"

def parse_json_response(raw_text: str) -> dict:
    cleaned = re.sub(r"```json|```", "", raw_text).strip()
    return json.loads(cleaned)

def analyze(
        api_key: str,
        skills: str, 
        conditions: str, 
        job_info: str,
        selected_categories: list
        ) -> tuple[dict | None, list, list, str | None]:
    
    job_text, scanned_urls, missing_categories, err = resolve_job_info(job_info, selected_categories)
    if err:
        return None, [], [], err

    try:
        client = genai.Client(api_key=api_key)
        prompt = build_analysis_prompt(skills, conditions, job_text)
        response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
        result = parse_json_response(response.text)
        return result, scanned_urls, missing_categories, None
    except json.JSONDecodeError:
        return None, scanned_urls, missing_categories, f"AIの出力がJSON形式ではありませんでした。\n\n{response.text}"
    except Exception as e:
        return None, scanned_urls, missing_categories, f"エラーが発生しました: {e}"