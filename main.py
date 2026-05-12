import os
import csv
import json
import time
from openai import OpenAI

API_KEY = "sk-scf0mfravgoovbxwng48ojbm297qwq79k4joqip6cavegmtx"
client = OpenAI(api_key=API_KEY, base_url="https://api.xiaomimimo.com/v1")

def build_prompt(query):
    return f"""Ты — travel-планировщик. Верни ТОЛЬКО JSON:
{{
  "query": "{query}",
  "destination": "страна/город (максимум два)",
  "budget_estimate": "диапазон в USD",
  "activities": "три занятия через запятую",
  "accommodation": "три типа жилья через запятую",
  "best_time": "сезон или месяцы"
}}
Не пиши ничего кроме JSON. Ответ должен быть валидным JSON."""

def fix_json(raw):
    raw = raw.strip()
    if raw.startswith("```json"): raw = raw[7:]
    if raw.startswith("```"): raw = raw[3:]
    if raw.endswith("```"): raw = raw[:-3]
    if raw.count('{') > raw.count('}'): raw += '}'
    try:
        return json.loads(raw)
    except:
        return None

def ask_llm(query, retries=2):
    for attempt in range(retries+1):
        try:
            resp = client.chat.completions.create(
                model="mimo-v2.5-pro",
                messages=[{"role": "system", "content": "You are MiMo. Today: May 12, 2026."},
                          {"role": "user", "content": build_prompt(query)}],
                max_completion_tokens=2048,
                temperature=0.1
            )
            parsed = fix_json(resp.choices[0].message.content)
            if parsed:
                return parsed
        except Exception as e:
            print(f"  Попытка {attempt+1} ошибка: {e}")
        time.sleep(1)
    return {"query": query, "error": "Невалидный JSON после всех попыток"}

def main():
    with open("travel_requests.csv", "r", encoding="utf-8-sig") as f:
        queries = [row[0] for row in csv.reader(f)][1:]  # пропуск заголовка
    results = []
    for i, q in enumerate(queries, 1):
        print(f"\n[{i}] {q[:50]}...")
        results.append(ask_llm(q))
        time.sleep(0.5)
    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("\nГотово!")

if __name__ == "__main__":
    main()