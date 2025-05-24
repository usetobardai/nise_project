import os
import requests
from dotenv import load_dotenv

# .env에서 neis_api_key 읽기
load_dotenv()
API_KEY = os.getenv('neis_api_key')

ENDPOINT = 'https://open.neis.go.kr/hub/schoolInfo'

def search_school(school_name: str) -> list[dict]:
    params = {
        'KEY'     : API_KEY,
        'Type'    : 'json',
        'SCHUL_NM': school_name
    }
    resp = requests.get(ENDPOINT, params=params)
    resp.raise_for_status()
    data = resp.json()

    if 'schoolInfo' not in data or len(data['schoolInfo']) < 2:
        return []
    if data['schoolInfo'][0]['head'][1]['RESULT']['CODE'] != 'INFO-000':
        return []
    return data['schoolInfo'][1]['row']

school_name = input('학교 이름을 입력하세요: ')
school_data = search_school(school_name)
len_data = len(school_data)

if not len_data < 1:
    for i in range(len_data):
        print(f'학교명: {school_data[i]['SCHUL_NM']} 학교종류: {school_data[i]['SCHUL_KND_SC_NM']}')
else:
    print("데이터가 없습니다")