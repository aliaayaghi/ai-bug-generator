import { useState, useEffect } from 'react';
import { fetchReports, createReport, deleteReport, uploadFile, analyzeImage } from '../shared/api/client';

function HomePage() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // File upload state
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);

  // AI analysis state
  const [analyzing, setAnalyzing] = useState(false);
  const [aiFilled, setAiFilled] = useState(false);
  const [analysisError, setAnalysisError] = useState(null);

  // Form state
  const [formData, setFormData] = useState({
    title: '',
    summary: '',
    severity: 'medium',
    expected_behavior: '',
    actual_behavior: '',
    image_path: '',
    user_note: '',
    page_url: '',
    reproduction_steps: '',
  });

  // Load reports on mount
  useEffect(() => {
    loadReports();
  }, []);

  async function loadReports() {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchReports();
      setReports(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function handleInputChange(e) {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  }

  function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setUploadResult(null);
      setAiFilled(false);
      setAnalysisError(null);
      setUploading(true);
      // Auto-upload immediately when file is selected
      uploadFile(file)
        .then((result) => {
          setUploadResult(result);
          setFormData((prev) => ({ ...prev, image_path: result.file_path }));
          
          // After upload succeeds, automatically analyze with AI
          setAnalyzing(true);
          return analyzeImage(
            result.file_path,
            formData.user_note,
            formData.page_url
          );
        })
        .then((analysis) => {
          // Auto-fill form fields with AI analysis
          setFormData((prev) => ({
            ...prev,
            title: analysis.title || prev.title,
            summary: analysis.summary || prev.summary,
            severity: analysis.severity || prev.severity,
            reproduction_steps: analysis.reproduction_steps || prev.reproduction_steps,
            expected_behavior: analysis.expected_behavior || prev.expected_behavior,
            actual_behavior: analysis.actual_behavior || prev.actual_behavior,
          }));
          setAiFilled(true);
        })
        .catch((err) => {
          // Upload succeeded but analysis failed - show error but don't block
          setAnalysisError(err.message);
        })
        .finally(() => {
          setUploading(false);
          setAnalyzing(false);
        });
    }
  }

  async function handleSubmit(e) {
    e.preventDefault();
    try {
      setSubmitting(true);
      setError(null);
      await createReport(formData);
      setFormData({
        title: '',
        summary: '',
        severity: 'medium',
        expected_behavior: '',
        actual_behavior: '',
        image_path: '',
        user_note: '',
        page_url: '',
        reproduction_steps: '',
      });
      setShowForm(false);
      setAiFilled(false);
      setAnalysisError(null);
      await loadReports();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDelete(reportId) {
    if (!confirm('Are you sure you want to delete this report?')) {
      return;
    }
    try {
      setError(null);
      await deleteReport(reportId);
      await loadReports();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="app-container">
      <div className="card">
        <h1 className="title">Bug Report AI</h1>
        <p className="description">
          Upload a screenshot and let AI generate a detailed bug report for you.
        </p>

        <button
          className="upload-button"
          onClick={() => setShowForm(!showForm)}
        >
          {showForm ? 'Cancel' : 'Create Report'}
        </button>

        {error && <div className="error-message">{error}</div>}
      </div>

      {showForm && (
        <div className="card">
          <h2 className="section-title">New Bug Report</h2>
          <form onSubmit={handleSubmit} className="report-form">
            <div className="form-group">
              <label htmlFor="title">Title *</label>
              <input
                type="text"
                id="title"
                name="title"
                value={formData.title}
                onChange={handleInputChange}
                required
                placeholder="Brief description of the bug"
              />
            </div>

            <div className="form-group">
              <label htmlFor="severity">Severity *</label>
              <select
                id="severity"
                name="severity"
                value={formData.severity}
                onChange={handleInputChange}
                required
              >
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
                <option value="info">Info</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="summary">Summary *</label>
              <textarea
                id="summary"
                name="summary"
                value={formData.summary}
                onChange={handleInputChange}
                required
                placeholder="Describe the issue"
                rows={3}
              />
            </div>

            <div className="form-group">
              <label htmlFor="expected_behavior">Expected Behavior *</label>
              <textarea
                id="expected_behavior"
                name="expected_behavior"
                value={formData.expected_behavior}
                onChange={handleInputChange}
                required
                placeholder="What should have happened"
                rows={2}
              />
            </div>

            <div className="form-group">
              <label htmlFor="actual_behavior">Actual Behavior *</label>
              <textarea
                id="actual_behavior"
                name="actual_behavior"
                value={formData.actual_behavior}
                onChange={handleInputChange}
                required
                placeholder="What actually happened"
                rows={2}
              />
            </div>

            <div className="form-group">
              <label htmlFor="reproduction_steps">Reproduction Steps</label>
              <textarea
                id="reproduction_steps"
                name="reproduction_steps"
                value={formData.reproduction_steps}
                onChange={handleInputChange}
                placeholder="Steps to reproduce the bug"
                rows={2}
              />
            </div>

            <div className="form-group">
              <label htmlFor="screenshot">Screenshot</label>
              <div className="file-upload-container">
                <input
                  type="file"
                  id="screenshot"
                  accept="image/*"
                  onChange={handleFileSelect}
                  className="file-input"
                />
                {selectedFile && (
                  <div className="selected-file">
                    <span className="file-name">{selectedFile.name}</span>
                    {uploading && <span className="uploading-text">Uploading...</span>}
                    {uploadResult && !analyzing && (
                      <span className="upload-success">✓ Uploaded</span>
                    )}
                    {analyzing && <span className="analyzing-text">Analyzing with AI...</span>}
                    {aiFilled && !analyzing && (
                      <span className="ai-filled-text">✓ Form auto-filled by AI</span>
                    )}
                    {analysisError && !analyzing && (
                      <span className="analysis-error-text">⚠ AI analysis failed: {analysisError}</span>
                    )}
                  </div>
                )}
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="page_url">Page URL</label>
              <input
                type="text"
                id="page_url"
                name="page_url"
                value={formData.page_url}
                onChange={handleInputChange}
                placeholder="URL where bug was found"
              />
            </div>

            <div className="form-group">
              <label htmlFor="user_note">User Note</label>
              <input
                type="text"
                id="user_note"
                name="user_note"
                value={formData.user_note}
                onChange={handleInputChange}
                placeholder="Optional note"
              />
            </div>

            <button
              type="submit"
              className="submit-button"
              disabled={submitting}
            >
              {submitting ? 'Creating...' : 'Submit Report'}
            </button>
          </form>
        </div>
      )}

      <div className="card">
        <h2 className="section-title">Bug Reports ({reports.length})</h2>

        {loading ? (
          <p className="loading-text">Loading reports...</p>
        ) : reports.length === 0 ? (
          <p className="empty-text">No reports yet. Create one above!</p>
        ) : (
          <div className="reports-list">
            {reports.map((report) => (
              <div key={report.id} className="report-item">
                <div className="report-header">
                  <span className={`severity-badge severity-${report.severity}`}>
                    {report.severity}
                  </span>
                  <h3 className="report-title">{report.title}</h3>
                  <button
                    className="delete-button"
                    onClick={() => handleDelete(report.id)}
                    title="Delete report"
                  >
                    ×
                  </button>
                </div>
                <p className="report-summary">{report.summary}</p>
                <div className="report-meta">
                  <span>Expected: {report.expected_behavior}</span>
                  <span>Actual: {report.actual_behavior}</span>
                </div>
                {report.reproduction_steps && (
                  <p className="report-steps">
                    <strong>Steps:</strong> {report.reproduction_steps}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default HomePage;