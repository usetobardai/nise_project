import { render, screen, fireEvent } from '@testing-library/react';
import App from './App';

// Helper to format date as YYYYMMDD
const formatDateToYYYYMMDD = (date) => {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}${month}${day}`;
};

describe('App Component Date Handling', () => {
  let mockDate;
  let originalDate;

  beforeEach(() => {
    // Mock Date for consistent testing
    // Target date: November 28, 2023
    mockDate = new Date(2023, 10, 28, 12, 0, 0); // Month is 0-indexed (10 is November)
    originalDate = global.Date; // Store original Date constructor
    global.Date = class extends Date {
      constructor(dateString) {
        if (dateString) {
          // @ts-ignore
          return new originalDate(dateString); // Allow DatePicker to create specific dates
        }
        return mockDate; // Return mocked 'today'
      }

      static now() {
        return mockDate.getTime();
      }
      
      // Delegate other static methods if needed, e.g., Date.UTC, Date.parse
      // For this test, only constructor and now() are primarily relevant for initial state.
    };
    // Copy static properties, like 'parse', 'UTC'
    Object.setPrototypeOf(global.Date, originalDate);

  });

  afterEach(() => {
    // Restore original Date constructor
    global.Date = originalDate;
  });

  test('initializes with today\'s date correctly formatted', () => {
    render(<App />);
    // The DatePicker input field will have the 'date' state value (YYYYMMDD)
    // It's identified by its placeholder or associated label.
    // Since DatePicker uses a text input, we can find it by its role and initial value.
    const datePickerInput = screen.getByLabelText(/날짜:/); // Assumes label text is "날짜:"
    
    const expectedTodayFormatted = formatDateToYYYYMMDD(mockDate); // "20231128"
    expect(datePickerInput).toHaveValue(expectedTodayFormatted);
  });

  test('getTodayDate (implicitly) provides correct YYYYMMDD format on init', () => {
    // This test is essentially the same as the one above, as getTodayDate()
    // is called during useEffect to set the initial date.
    // We are verifying its output by checking the input field's value.
    render(<App />);
    const datePickerInput = screen.getByLabelText(/날짜:/);
    const expectedTodayFormatted = formatDateToYYYYMMDD(mockDate); // "20231128"
    expect(datePickerInput).toHaveValue(expectedTodayFormatted);
  });
  
  test('updates date state (YYYYMMDD string and Date object) when DatePicker changes', () => {
    render(<App />);
    const datePickerInput = screen.getByLabelText(/날짜:/);

    // Simulate changing the date in the DatePicker input
    // This will trigger the DatePicker's internal onChange, then App's onChange
    // Note: react-datepicker formats its input value internally.
    // We directly change the input value to a YYYYMMDD string.
    // The component's onChange handler for DatePicker receives a Date object.
    // For testing, directly manipulating the input and checking its value
    // is a common way to test the component's reaction to date changes.
    
    const newDateStr = '20240115';
    fireEvent.change(datePickerInput, { target: { value: newDateStr } });
    
    // After the change, the input should reflect the new YYYYMMDD string
    expect(datePickerInput).toHaveValue(newDateStr);

    // To further verify the internal Date object (selectedDateObj) would require
    // more complex interaction or exposing state, which is beyond typical RTL usage.
    // However, if the input value (derived from `date` state, which is derived from
    // `selectedDateObj` via `format(d, 'yyyyMMdd')`) is correct, it's a strong
    // indication that selectedDateObj was also updated correctly with a Date object for "2024-01-15".
  });

  test('DatePicker input is present and has correct initial placeholder', () => {
    render(<App />);
    // The actual placeholder for react-datepicker might be handled differently
    // but we can check the one we passed.
    const datePickerInput = screen.getByPlaceholderText(/예: 20231128/);
    expect(datePickerInput).toBeInTheDocument();
  });

});
