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
    <div className="school-search-container">
      <h2>학교 검색</h2>
      <div className="search-controls">
        <input
          type="text"
          className="search-input"
          value={schoolNameQuery}
          onChange={(e) => setSchoolNameQuery(e.target.value)}
          placeholder="학교 이름을 입력하세요..."
          disabled={disabled}
        />
        <button onClick={onSearch} disabled={disabled} className="search-button">
          검색
        </button>
      </div>
      {searchResults && searchResults.length > 0 && (
        <ul className="search-results-list"> {/* Added class for consistency */}
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
