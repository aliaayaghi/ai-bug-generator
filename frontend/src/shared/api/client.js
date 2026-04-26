/**
 * API client for communicating with the backend.
 * Uses relative URLs - Vite proxies /api to the backend during dev.
 */

const API_BASE = '/api';

/**
 * Upload an image file to the backend.
 * @param {File} file - The image file to upload
 * @returns {Promise<Object>} Object with file_path, original_filename, content_type
 */
export async function uploadFile(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE}/upload`, {
    method: 'POST',
    body: formData,
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || 'Failed to upload file');
  }
  
  return response.json();
}

/**
 * Fetch all reports from the backend.
 * @returns {Promise<Array>} Array of report objects
 */
export async function fetchReports() {
  const response = await fetch(`${API_BASE}/reports`);
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || 'Failed to fetch reports');
  }
  return response.json();
}

/**
 * Create a new report in the backend.
 * @param {Object} reportData - The report data to create
 * @returns {Promise<Object>} The created report object
 */
export async function createReport(reportData) {
  const response = await fetch(`${API_BASE}/reports`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(reportData),
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || 'Failed to create report');
  }
  return response.json();
}

/**
 * Delete a report by ID.
 * @param {number} reportId - The ID of the report to delete
 * @returns {Promise<void>}
 */
export async function deleteReport(reportId) {
  const response = await fetch(`${API_BASE}/reports/${reportId}`, {
    method: 'DELETE',
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || 'Failed to delete report');
  }
}


