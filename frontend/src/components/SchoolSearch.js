import React from 'react';

function SchoolSearch({
  schoolNameQuery,
  setSchoolNameQuery,
  onSearch,
  searchResults,
  onSchoolSelect,
  disabled,
}) {
  return (
    <div>
      <h2>학교 검색</h2>
      <input
        type="text"
        value={schoolNameQuery}
        onChange={(e) => setSchoolNameQuery(e.target.value)}
        placeholder="학교 이름을 입력하세요"
        disabled={disabled}
      />
      <button onClick={onSearch} disabled={disabled}>
        검색
      </button>
      {searchResults && searchResults.length > 0 && (
        <ul>
          {searchResults.map((school) => (
            <li key={school.SD_SCHUL_CODE} onClick={() => onSchoolSelect(school)}>
              {school.SCHUL_NM} ({school.ORG_RDNMA})
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default SchoolSearch;
