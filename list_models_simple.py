#!/usr/bin/env python3
"""
List models that support generateContent
"""
import requests, os

api_key = os.environ.get("GEMINI_API_KEY")
r = requests.get(f'https://generativelanguage.googleapis.com/v1beta/models?key={api_key}')

print('Status:', r.status_code)
if r.status_code == 200:
    data = r.json()
    print('Models with generateContent support:')
    for m in data['models']:
        if 'generateContent' in m.get('supportedGenerationMethods', []):
            print(f'  - {m["name"]}')
else:
    print('Error:', r.text)