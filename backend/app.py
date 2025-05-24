import os
import requests
from flask import Flask, request, jsonify, send_from_directory # Added send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime

# Load .env from backend directory
load_dotenv() 
API_KEY = os.getenv('neis_api_key')

# NEIS API Endpoints
NEIS_API_BASE_URL = "https://open.neis.go.kr/hub/"
SCHOOL_INFO_ENDPOINT = NEIS_API_BASE_URL + "schoolInfo"
TIMETABLE_ENDPOINTS = {
    '초등학교': NEIS_API_BASE_URL + 'elsTimetable',
    '중학교': NEIS_API_BASE_URL + 'misTimetable',
    '고등학교': NEIS_API_BASE_URL + 'hisTimetable'
}

# Modify Flask app initialization for static files
# The static_folder path is relative to the 'backend' directory where app.py is.
app = Flask(__name__, static_folder='../frontend/build', static_url_path='/')

# CORS is still useful if you want to allow other origins to hit your API,
# or if your frontend is ever served from a different domain/port during development/testing.
# For a single-origin deployment, it might not be strictly necessary for the frontend part,
# but the API endpoints might still benefit.
CORS(app, resources={r"/api/*": {"origins": "*"}}) # Allow all origins for API for simplicity

def search_school(school_name: str) -> dict:
    """학교 이름을 기반으로 학교 정보를 검색하고 결과를 dict로 반환합니다."""
    if not school_name:
        return {'error': '학교 이름이 필요합니다.', 'status_code': 400}
    
    params = {
        'KEY': API_KEY,
        'Type': 'json',
        'SCHUL_NM': school_name
    }
    try:
        resp = requests.get(SCHOOL_INFO_ENDPOINT, params=params, timeout=10) # Increased timeout
        resp.raise_for_status()
        data = resp.json()

        if 'schoolInfo' not in data or len(data['schoolInfo']) < 2:
            return {'schools': []} 
        
        result_info = data['schoolInfo'][0]['head'][1]['RESULT']
        if result_info['CODE'] != 'INFO-000':
            return {'error': f"학교 정보 검색 API 오류: {result_info['MESSAGE']}", 'status_code': 500}
        
        return {'schools': data['schoolInfo'][1]['row']}
    except requests.exceptions.Timeout:
        return {'error': "학교 정보 검색 중 타임아웃이 발생했습니다.", 'status_code': 504}
    except requests.exceptions.RequestException as e:
        return {'error': f"학교 정보 검색 중 네트워크 오류 발생: {e}", 'status_code': 500}
    except ValueError:
        return {'error': "학교 정보 API 응답 파싱 오류.", 'status_code': 500}
    except KeyError:
        return {'error': "학교 정보 API 응답 형식 오류.", 'status_code': 500}


def get_timetable(school_data: dict, grade: str, class_nm: str, date_str: str) -> dict:
    """선택된 학교의 시간표를 조회하고 결과를 dict로 반환합니다."""
    school_kind = school_data.get('SCHUL_KND_SC_NM')
    school_code = school_data.get('SD_SCHUL_CODE')
    office_code = school_data.get('ATPT_OFCDC_SC_CODE')

    if not all([school_kind, school_code, office_code, grade, class_nm, date_str]):
        return {'error': '시간표 조회를 위한 필수 파라미터가 누락되었습니다.', 'status_code': 400}

    if school_kind not in TIMETABLE_ENDPOINTS:
        return {'error': f"'{school_kind}' 종류의 학교는 시간표 조회를 지원하지 않습니다.", 'status_code': 400}

    timetable_endpoint = TIMETABLE_ENDPOINTS[school_kind]
    
    try:
        datetime.strptime(date_str, '%Y%m%d')
    except ValueError:
        return {'error': "날짜 형식이 올바르지 않습니다. YYYYMMDD 형식으로 입력해주세요.", 'status_code': 400}

    params = {
        'KEY': API_KEY,
        'Type': 'json',
        'ATPT_OFCDC_SC_CODE': office_code,
        'SD_SCHUL_CODE': school_code,
        'AY': date_str[:4], 
        'GRADE': grade,
        'CLASS_NM': class_nm,
        'TI_FROM_YMD': date_str,
        'TI_TO_YMD': date_str
    }

    try:
        resp = requests.get(timetable_endpoint, params=params, timeout=10) # Increased timeout
        resp.raise_for_status()
        data = resp.json()

        timetable_key_map = {
            '초등학교': 'elsTimetable',
            '중학교': 'misTimetable',
            '고등학교': 'hisTimetable'
        }
        timetable_key = timetable_key_map[school_kind]

        if timetable_key not in data or not data[timetable_key]:
            if timetable_key in data and data[timetable_key] and 'head' in data[timetable_key][0]:
                 head_info = data[timetable_key][0]['head']
                 if len(head_info) > 1 and 'RESULT' in head_info[1]:
                    api_result = head_info[1]['RESULT']
                    if api_result['CODE'] == 'INFO-200': 
                        return {'timetable': []} 
                    return {'error': f"시간표 조회 API 메시지: {api_result['MESSAGE']} (코드: {api_result['CODE']})", 'status_code': 500}
            return {'timetable': []} 

        result_info = data[timetable_key][0]['head'][1]['RESULT']
        if result_info['CODE'] != 'INFO-000':
            return {'error': f"시간표 조회 API 오류: {result_info['MESSAGE']}", 'status_code': 500}
        
        timetable_entries = data[timetable_key][1]['row']
        sorted_timetable = sorted(timetable_entries, key=lambda x: int(x.get('PERIO', '0')))
        return {'timetable': sorted_timetable}

    except requests.exceptions.Timeout:
        return {'error': "시간표 조회 중 타임아웃이 발생했습니다.", 'status_code': 504}
    except requests.exceptions.RequestException as e:
        return {'error': f"시간표 조회 중 네트워크 오류 발생: {e}", 'status_code': 500}
    except ValueError:
        return {'error': "시간표 API 응답 파싱 오류.", 'status_code': 500}
    except KeyError: 
        return {'error': "시간표 API 응답에서 예상치 못한 키를 찾을 수 없습니다.", 'status_code': 500}


@app.route('/api/search_school', methods=['GET'])
def api_search_school():
    school_name = request.args.get('school_name')
    if not school_name:
        return jsonify({'error': '학교 이름(school_name) 파라미터가 필요합니다.'}), 400
    
    result = search_school(school_name)
    if 'error' in result:
        return jsonify({'error': result['error']}), result.get('status_code', 500)
    return jsonify(result)

@app.route('/api/timetable', methods=['GET'])
def api_get_timetable():
    required_params = ['school_code', 'office_code', 'school_kind', 'grade', 'class_nm', 'date']
    missing_params = [param for param in required_params if not request.args.get(param)]
    if missing_params:
        return jsonify({'error': f"필수 파라미터가 누락되었습니다: {', '.join(missing_params)}"}), 400

    school_data = {
        'SD_SCHUL_CODE': request.args.get('school_code'),
        'ATPT_OFCDC_SC_CODE': request.args.get('office_code'),
        'SCHUL_KND_SC_NM': request.args.get('school_kind')
    }
    grade = request.args.get('grade')
    class_nm = request.args.get('class_nm')
    date_str = request.args.get('date')
    
    result = get_timetable(school_data, grade, class_nm, date_str)
    if 'error' in result:
        return jsonify({'error': result['error']}), result.get('status_code', 500)
    return jsonify(result)

# Serve React App
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        # Check if index.html exists
        index_path = os.path.join(app.static_folder, 'index.html')
        if not os.path.exists(index_path):
            return jsonify({"error": "index.html not found in static folder. Did you build the frontend?"}), 404
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    if not API_KEY:
        print("오류: neis_api_key가 .env 파일에 설정되지 않았거나 로드되지 않았습니다.")
        print("backend/.env 파일에 neis_api_key='YOUR_API_KEY' 형식으로 설정해주세요.")
    else:
        print("NEIS API Key Loaded.")
    
    # Production-like server run
    # Use Waitress or Gunicorn for a proper production deployment
    # For this exercise, host='0.0.0.0' is sufficient to demonstrate.
    port = int(os.environ.get('PORT', 5000))
    print(f"Flask app running on http://0.0.0.0:{port}")
    # app.run(host='0.0.0.0', port=port) # debug=False is default if not set
    
    # For testing purposes in this environment, we'll keep debug=True to see logs.
    # In a real production deployment, debug should be False.
    app.run(debug=True, host='0.0.0.0', port=port)
