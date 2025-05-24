import React from 'react';

function TimetableDisplay({ timetableData }) {
  if (!timetableData) {
    return null; // Don't render if no data yet
  }

  if (timetableData.length === 0) {
    return <p>해당 날짜의 시간표 정보가 없습니다.</p>;
  }

  // Sort by period (PERIO) - assuming PERIO is a string like '1', '2'
  const sortedTimetable = [...timetableData].sort(
    (a, b) => parseInt(a.PERIO, 10) - parseInt(b.PERIO, 10)
  );

  return (
    <div>
      <h2>시간표</h2>
      <table>
        <thead>
          <tr>
            <th>교시</th>
            <th>과목</th>
          </tr>
        </thead>
        <tbody>
          {sortedTimetable.map((item, index) => (
            <tr key={index}> {/* Assuming no unique ID per lesson, use index */}
              <td>{item.PERIO}교시</td>
              <td>{item.ITRT_CNTNT || '정보 없음'}</td> {/* ITRT_CNTNT is subject */}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default TimetableDisplay;
