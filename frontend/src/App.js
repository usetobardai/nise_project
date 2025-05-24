import React, { useState, useEffect } from 'react';
import './App.css';
import SchoolSearch from './components/SchoolSearch';
import TimetableDisplay from './components/TimetableDisplay';
// import axios from 'axios'; // Using fetch for this example

function App() {
  const [schoolNameQuery, setSchoolNameQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [selectedSchool, setSelectedSchool] = useState(null);
  const [grade, setGrade] = useState('');
  const [classNum, setClassNum] = useState('');
  const [date, setDate] = useState(''); // YYYYMMDD
  const [timetable, setTimetable] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Get today's date in YYYYMMDD format
  const getTodayDate = () => {
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');
    return `${year}${month}${day}`;
  };

  // Set initial date to today
  useEffect(() => {
    setDate(getTodayDate());
  }, []);

  const handleSearchSchool = async () => {
    if (!schoolNameQuery.trim()) {
      setError('학교 이름을 입력해주세요.');
      setSearchResults([]);
      setSelectedSchool(null);
      setTimetable(null);
      return;
    }
    setLoading(true);
    setError('');
    setSearchResults([]);
    setSelectedSchool(null);
    setTimetable(null); // Clear previous timetable
    try {
      const response = await fetch(`http://localhost:5000/api/search_school?school_name=${encodeURIComponent(schoolNameQuery)}`);
      if (!response.ok) {
        const errData = await response.json().catch(() => ({ error: `HTTP error ${response.status}` })); // Catch if res.json() fails
        throw new Error(errData.error || `Error ${response.status}`);
      }
      const data = await response.json();
      if (data.schools && data.schools.length > 0) {
        setSearchResults(data.schools);
      } else {
        setError('검색 결과가 없습니다.');
      }
    } catch (err) {
      setError(`학교 검색 실패: ${err.message}`);
    }
    setLoading(false);
  };

  const handleSchoolSelect = (school) => {
    setSelectedSchool(school);
    setSearchResults([]); // Clear search results
    setSchoolNameQuery(school.SCHUL_NM); // Show selected school name in input
    setError('');
    setTimetable(null); // Clear previous timetable
    // Optionally, clear grade/class/date or pre-fill if needed
  };

  const handleGetTimetable = async () => {
    if (!selectedSchool || !grade.trim() || !classNum.trim() || !date.trim()) {
      setError('학교 선택 및 모든 시간표 정보를 입력해주세요. (학년, 반, 날짜)');
      return;
    }
    // Basic date validation (YYYYMMDD format)
    if (!/^\d{8}$/.test(date)) {
        setError('날짜 형식이 올바르지 않습니다. YYYYMMDD 형식으로 입력해주세요.');
        return;
    }
    setLoading(true);
    setError('');
    setTimetable(null);
    try {
      const params = new URLSearchParams({
        school_code: selectedSchool.SD_SCHUL_CODE,
        office_code: selectedSchool.ATPT_OFCDC_SC_CODE,
        school_kind: selectedSchool.SCHUL_KND_SC_NM,
        grade: grade,
        class_nm: classNum,
        date: date,
      });
      const response = await fetch(`http://localhost:5000/api/timetable?${params.toString()}`);
      if (!response.ok) {
         const errData = await response.json().catch(() => ({ error: `HTTP error ${response.status}` }));
         throw new Error(errData.error || `Error ${response.status}`);
      }
      const data = await response.json();
      
      if (data.error) { // Catch errors reported by the backend API itself
        setError(data.error);
        setTimetable([]); // Show "no data" or error specific message
      } else if (data.timetable && data.timetable.length > 0) {
        setTimetable(data.timetable);
      } else {
        setError('해당 조건의 시간표 데이터가 없습니다.'); // API success but no timetable rows
        setTimetable([]); 
      }
    } catch (err) {
      setError(`시간표 조회 실패: ${err.message}`);
      setTimetable([]); // Ensure timetable is empty on error
    }
    setLoading(false);
  };
  
  const handleClearSchoolSelection = () => {
    setSelectedSchool(null);
    setSchoolNameQuery('');
    setSearchResults([]);
    setTimetable(null);
    setError('');
    // setGrade(''); // Optionally reset these too
    // setClassNum('');
    // setDate(getTodayDate()); 
  };


  return (
    <div className="App">
      <header className="App-header">
        <h1>학교 시간표 조회 서비스</h1>
      </header>
      <main>
        {error && <p className="error-message">{error}</p>}
        {loading && <p className="loading-message">로딩 중...</p>}

        <SchoolSearch
          schoolNameQuery={schoolNameQuery}
          setSchoolNameQuery={setSchoolNameQuery}
          onSearch={handleSearchSchool}
          searchResults={searchResults}
          onSchoolSelect={handleSchoolSelect}
          disabled={loading || !!selectedSchool}
        />

        {selectedSchool && (
          <div className="timetable-form">
            <h2>시간표 정보 입력</h2>
            <div className="selected-school-info">
              <span>선택된 학교: <strong>{selectedSchool.SCHUL_NM}</strong> ({selectedSchool.ORG_RDNMA})</span>
              <button onClick={handleClearSchoolSelection} className="clear-selection-button" disabled={loading}>
                학교 선택 해제
              </button>
            </div>
            <div className="input-group">
              <label htmlFor="grade-input">학년: </label>
              <input 
                id="grade-input"
                type="text" 
                value={grade} 
                onChange={(e) => setGrade(e.target.value)} 
                placeholder="예: 1" 
                disabled={loading} 
              />
            </div>
            <div className="input-group">
              <label htmlFor="class-input">반: </label>
              <input 
                id="class-input"
                type="text" 
                value={classNum} 
                onChange={(e) => setClassNum(e.target.value)} 
                placeholder="예: 3" 
                disabled={loading}
              />
            </div>
            <div className="input-group">
              <label htmlFor="date-input">날짜 (YYYYMMDD): </label>
              <input 
                id="date-input"
                type="text" 
                value={date} 
                onChange={(e) => setDate(e.target.value)} 
                placeholder="예: 20231128" 
                disabled={loading}
              />
            </div>
            <button onClick={handleGetTimetable} disabled={loading} className="action-button">
              시간표 조회
            </button>
          </div>
        )}

        {timetable && <TimetableDisplay timetableData={timetable} />}
      </main>
      <footer className="App-footer">
        <p>NEIS API 기반</p>
      </footer>
    </div>
  );
}

export default App;
