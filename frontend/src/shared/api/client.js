/**
 * API client for communicating with the backend.
 * Uses relative URLs - Vite proxies /api to the backend during dev.
 */

const API_BASE = '/api';

/**
 * Extract user-friendly error message from response.
 */
function getErrorMessage(response, fallback) {
  if (response.detail) {
    // Handle FastAPI validation errors which come as array or string
    if (Array.isArray(response.detail)) {
      return response.detail.map(d => d.msg || d).join(', ');
    }
    return response.detail;
  }
  return fallback;
}

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
    throw new Error(getErrorMessage(error, 'Upload failed. Please try again.'));
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
    throw new Error(getErrorMessage(error, 'Failed to load reports. Please refresh.'));
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
    throw new Error(getErrorMessage(error, 'Failed to save report. Please try again.'));
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
    throw new Error(getErrorMessage(error, 'Failed to delete report. Please try again.'));
  }
}

/**
 * Analyze a screenshot using AI to generate bug report fields.
 * @param {string} imagePath - Path to the uploaded image file
 * @param {string} [userNote] - Optional user note about the screenshot
 * @param {string} [pageUrl] - Optional URL where the screenshot was taken
 * @returns {Promise<Object>} Object with suggested bug report fields
 */
export async function analyzeImage(imagePath, userNote = '', pageUrl = '') {
  const response = await fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      image_path: imagePath,
      user_note: userNote || null,
      page_url: pageUrl || null,
    }),
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    const message = getErrorMessage(error, 'AI analysis failed. You can still edit manually.');
    throw new Error(message);
  }
  
  return response.json();
}


