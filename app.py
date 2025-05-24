import os
import requests
from dotenv import load_dotenv
from datetime import datetime

# .env에서 neis_api_key 읽기
load_dotenv()
API_KEY = os.getenv('neis_api_key')

SCHOOL_INFO_ENDPOINT = 'https://open.neis.go.kr/hub/schoolInfo'
TIMETABLE_ENDPOINTS = {
    '초등학교': 'https://open.neis.go.kr/hub/elsTimetable',
    '중학교': 'https://open.neis.go.kr/hub/misTimetable',
    '고등학교': 'https://open.neis.go.kr/hub/hisTimetable'
}

def search_school(school_name: str) -> list[dict]:
    """학교 이름을 기반으로 학교 정보를 검색합니다."""
    params = {
        'KEY': API_KEY,
        'Type': 'json',
        'SCHUL_NM': school_name
    }
    try:
        resp = requests.get(SCHOOL_INFO_ENDPOINT, params=params)
        resp.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        data = resp.json()

        if 'schoolInfo' not in data or len(data['schoolInfo']) < 2:
            return []
        if data['schoolInfo'][0]['head'][1]['RESULT']['CODE'] != 'INFO-000':
            print(f"학교 정보 검색 API 오류: {data['schoolInfo'][0]['head'][1]['RESULT']['MESSAGE']}")
            return []
        return data['schoolInfo'][1]['row']
    except requests.exceptions.RequestException as e:
        print(f"학교 정보 검색 중 네트워크 오류 발생: {e}")
        return []
    except ValueError:
        print("학교 정보 API 응답 파싱 오류.")
        return []

def get_timetable(school_data: dict, grade: str, class_nm: str, date: str) -> list[dict]:
    """선택된 학교의 시간표를 조회합니다."""
    school_kind = school_data.get('SCHUL_KND_SC_NM')
    school_code = school_data.get('SD_SCHUL_CODE')
    office_code = school_data.get('ATPT_OFCDC_SC_CODE')

    if not school_kind or not school_code or not office_code:
        print("학교 정보가 불완전하여 시간표를 조회할 수 없습니다.")
        return []

    if school_kind not in TIMETABLE_ENDPOINTS:
        print(f"'{school_kind}' 종류의 학교는 시간표 조회를 지원하지 않습니다.")
        return []

    timetable_endpoint = TIMETABLE_ENDPOINTS[school_kind]

    params = {
        'KEY': API_KEY,
        'Type': 'json',
        'ATPT_OFCDC_SC_CODE': office_code,  # 시도교육청코드
        'SD_SCHUL_CODE': school_code,       # 학교코드
        'AY': datetime.now().year,          # 학년도 (현재 년도 사용)
        'GRADE': grade,                     # 학년
        'CLASS_NM': class_nm,               # 반명
        'TI_FROM_YMD': date,                # 시간표 조회 시작일
        'TI_TO_YMD': date                   # 시간표 조회 종료일 (단일 날짜 조회)
    }

    try:
        resp = requests.get(timetable_endpoint, params=params)
        resp.raise_for_status()
        data = resp.json()

        timetable_key = ''
        if school_kind == '초등학교':
            timetable_key = 'elsTimetable'
        elif school_kind == '중학교':
            timetable_key = 'misTimetable'
        elif school_kind == '고등학교':
            timetable_key = 'hisTimetable'

        if timetable_key not in data or len(data[timetable_key]) < 2:
            if timetable_key in data and len(data[timetable_key]) > 0 and 'head' in data[timetable_key][0]:
                result_code = data[timetable_key][0]['head'][1]['RESULT']['CODE']
                result_message = data[timetable_key][0]['head'][1]['RESULT']['MESSAGE']
                print(f"시간표 조회 API 오류: {result_code} - {result_message}")
            else:
                print("해당 조건의 시간표 데이터가 없습니다.")
            return []
        
        if data[timetable_key][0]['head'][1]['RESULT']['CODE'] != 'INFO-000':
             print(f"시간표 조회 API 오류: {data[timetable_key][0]['head'][1]['RESULT']['MESSAGE']}")
             return []
             
        return data[timetable_key][1]['row']
    except requests.exceptions.RequestException as e:
        print(f"시간표 조회 중 네트워크 오류 발생: {e}")
        return []
    except ValueError:
        print("시간표 API 응답 파싱 오류.")
        return []
    except KeyError:
        print("API 응답에서 예상치 못한 키를 찾을 수 없습니다. 응답 구조를 확인하세요.")
        return []

# --- 메인 프로그램 시작 ---
school_name = input('학교 이름을 입력하세요: ')
school_data_list = search_school(school_name)
len_data = len(school_data_list)

if len_data < 1:
    print("검색된 학교가 없습니다.")
else:
    print("\n--- 검색된 학교 목록 ---")
    for i, school in enumerate(school_data_list):
        print(f"{i+1}. 학교명: {school['SCHUL_NM']} | 학교종류: {school['SCHUL_KND_SC_NM']} | 주소: {school['ORG_RDNMA']}")

    while True:
        try:
            choice = int(input(f'시간표를 조회할 학교 번호를 선택하세요 (1 ~ {len_data}): '))
            if 1 <= choice <= len_data:
                selected_school = school_data_list[choice - 1]
                break
            else:
                print("잘못된 번호입니다. 다시 입력해주세요.")
        except ValueError:
            print("숫자를 입력해주세요.")

    print(f"\n선택된 학교: {selected_school['SCHUL_NM']} ({selected_school['SCHUL_KND_SC_NM']})")

    # 시간표 조회에 필요한 파라미터 입력받기
    print("\n--- 시간표 조회 정보 입력 ---")
    while True:
        grade = input("학년을 입력하세요 (예: 1, 2, 3): ")
        if grade.isdigit() and 1 <= int(grade) <= 6: # 초등 1~6, 중/고 1~3학년 고려
            break
        else:
            print("유효한 학년을 숫자로 입력해주세요.")
            
    while True:
        class_nm = input("반을 입력하세요 (예: 1, 2, 3): ")
        if class_nm.isdigit():
            break
        else:
            print("유효한 반을 숫자로 입력해주세요.")

    while True:
        target_date_str = input("조회할 날짜를 입력하세요 (YYYYMMDD 형식, 예: 20231123): ")
        try:
            datetime.strptime(target_date_str, '%Y%m%d')
            break
        except ValueError:
            print("날짜 형식이 올바르지 않습니다. YYYYMMDD 형식으로 입력해주세요.")

    # 시간표 조회
    print(f"\n--- {selected_school['SCHUL_NM']}의 {grade}학년 {class_nm}반 {target_date_str} 시간표 ---")
    timetable_data = get_timetable(selected_school, grade, class_nm, target_date_str)

    if timetable_data:
        # 시간표 데이터를 교시 순으로 정렬 (TI_DI_SC_CD는 교시 코드를 나타냄)
        # NEIS API 문서에 따르면 TI_DI_SC_CD (교시코드)는 숫자로 정렬 가능.
        # 예: '01' (1교시), '02' (2교시)
        sorted_timetable = sorted(timetable_data, key=lambda x: int(x.get('TI_DI_SC_CD', '0')))
        
        for lesson in sorted_timetable:
            # 과목명 필드가 없는 경우도 있을 수 있으므로 .get() 사용
            period = lesson.get('PERIO', 'N/A')
            subject = lesson.get('ITRT_CNTNT', '과목 정보 없음') # ITRT_CNTNT: 수업 내용 (과목명)
            print(f"{period}교시: {subject}")
    else:
        print("시간표 데이터를 불러오지 못했습니다.")