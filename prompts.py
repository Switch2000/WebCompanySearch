def build_analysis_prompt(skills: str, conditions: str, job_info: str) -> str:
    return f"""
    あなたは的確なキャリアコンサルタントです。
    以下の情報を元に、忖度なしで分析し、
    **必ず以下のJSON形式の文字列のみ**で出力してください。Markdownのコードブロックや解説は不要です。
    求人情報から読み取れない項目は「記載なし」としてください。

    {{
        "total_match": 総合マッチ度(%)（数値のみ）,
        "corporate_info": {{
            "company_name": "企業名",
            "philosophy": "企業理念",
            "desired_talent": "求める人材像",
            "common_tech": "主要技術",
            "products_services": "提供サービス",
            "strong_industries": "得意な業界・業種"
        }},
        "salary_min": 年収下限(万円)（数値のみ）,
        "salary_max": 年収上限(万円)（数値のみ）,
        "salary_reason": "年収算出の根拠",
        "tech_stack": [
            {{ "name": "技術名", "match": "合致度(A/B/C)" }}
        ],
        "pros": ["メリット1"],
        "cons": ["デメリット1"],
        "darkness_risks": ["面接で確認すべき事項1"]
    }}

    【求職者スキル】: {skills}
    【希望条件】: {conditions}
    【求人情報】: {job_info}
    """