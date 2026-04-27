import { useState, useEffect, useRef } from 'react';
import { fetchReports, createReport, deleteReport, uploadFile, analyzeImage } from '../shared/api/client';

function HomePage() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // File upload state - starts with upload as main action
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);

  // AI analysis state
  const [analyzing, setAnalyzing] = useState(false);
  const [aiFilled, setAiFilled] = useState(false);
  const [analysisError, setAnalysisError] = useState(null);

  // Form state - shown after upload/analysis starts
  const [showForm, setShowForm] = useState(false);
  
  // Preview mode - shows read-only AI-generated report first
  const [showPreview, setShowPreview] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  
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
    suspected_area: '',
    confidence: null,
  });

  // Ref for file input
  const fileInputRef = useRef(null);

  // Modal state for viewing saved report details
  const [selectedReport, setSelectedReport] = useState(null);


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
      setShowForm(true);
      setShowPreview(false);
      setIsEditing(false);
      setUploading(true);

      // Upload and analyze immediately
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
            suspected_area: analysis.suspected_area || prev.suspected_area,
            confidence:
  analysis.confidence !== null && analysis.confidence !== undefined
    ? (analysis.confidence > 1 ? analysis.confidence / 100 : analysis.confidence)
    : prev.confidence,
          }));
          setAiFilled(true);
          // Show preview mode after AI analysis completes
          setShowPreview(true);
        })
        .catch((err) => {
          // Upload succeeded but analysis failed - show error but don't block
          setAnalysisError(err.message);
          // Still show form even if analysis failed
          setShowForm(true);
        })
        .finally(() => {
          setUploading(false);
          setAnalyzing(false);
        });
    }
  }

  // Handle click on upload area to trigger file input
  function handleUploadAreaClick() {
    fileInputRef.current?.click();
  }

  // Reset to start over with new upload
  function handleStartOver() {
    setSelectedFile(null);
    setUploadResult(null);
    setAiFilled(false);
    setAnalysisError(null);
    setShowForm(false);
    setShowPreview(false);
    setIsEditing(false);
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
      suspected_area: '',
      confidence: null,
    });
  }

  // Switch to edit mode
  function handleEdit() {
    setIsEditing(true);
  }

  async function handleSubmit(e) {
    e.preventDefault();
    try {
      setSubmitting(true);
      setError(null);
      await createReport(formData);
      setSaveSuccess(true);
      // Reset to initial state after successful save
      handleStartOver();
      await loadReports();
      // Clear success message after 3 seconds
      setTimeout(() => setSaveSuccess(false), 3000);
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

  
  

  // Open modal to view report details
  function handleViewReport(report) {
    setSelectedReport(report);
  }

  // Close modal
  function handleCloseModal() {
    setSelectedReport(null);
  }

  // Handle click outside modal to close
  function handleModalBackdropClick(e) {
    if (e.target === e.currentTarget) {
      handleCloseModal();
    }
  }

  return (
    <div className="app-container">
      {/* Header Card - Always visible */}
      <div className="card">
        <h1 className="title">Bug Report AI</h1>
        <p className="description">
          Upload a screenshot and AI will analyze it to create a detailed bug report.
        </p>

        {/* Upload Area - Main action on homepage */}
        <div 
          className={`upload-area ${selectedFile ? 'has-file' : ''}`}
          onClick={handleUploadAreaClick}
        >
          <input
            type="file"
            ref={fileInputRef}
            accept="image/*"
            onChange={handleFileSelect}
            className="file-input-hidden"
          />
          
          {!selectedFile ? (
            // No file selected - show upload prompt
            <>
              <div className="upload-icon">📷</div>
              <p className="upload-text">Click to upload a screenshot</p>
              <p className="upload-hint">PNG, JPG, or GIF</p>
            </>
          ) : (
            // File selected - show status
            <div className="file-status">
              <span className="file-name">{selectedFile.name}</span>
              {uploading && <span className="uploading-text">Uploading screenshot...</span>}
              {uploadResult && !analyzing && !aiFilled && !analysisError && (
                <span className="upload-success">✓ Upload complete</span>
              )}
              {analyzing && <span className="analyzing-text">Analyzing with AI...</span>}
              {aiFilled && !analyzing && (
                <span className="ai-filled-text">✓ Analysis complete</span>
              )}
              {analysisError && !analyzing && (
                <span className="analysis-error-text">⚠ Analysis failed — you can still edit manually</span>
              )}
            </div>
          )}
        </div>

        {error && <div className="error-message">{error}</div>}
        {saveSuccess && <div className="success-message">Report saved successfully!</div>}
      </div>

      {/* AI Preview Card - Read-only report preview */}
      {showPreview && !isEditing && (
        <div className="card">
          <h2 className="section-title">Generated Report</h2>
          <p className="form-description">
            Review the AI-generated report below. You can edit it before saving.
          </p>
          
          <div className="preview-card">
            <div className="preview-header">
              <span className={`severity-badge severity-${formData.severity}`}>
                {formData.severity}
              </span>
              <h3 className="preview-title">{formData.title || 'Untitled Report'}</h3>
            </div>
            
            <div className="preview-section">
              <label>Summary</label>
              <p>{formData.summary || 'No summary provided'}</p>
            </div>
            
            <div className="preview-section">
              <label>Expected Behavior</label>
              <p>{formData.expected_behavior || 'Not specified'}</p>
            </div>
            
            <div className="preview-section">
              <label>Actual Behavior</label>
              <p>{formData.actual_behavior || 'Not specified'}</p>
            </div>
            
            {formData.reproduction_steps && (
              <div className="preview-section">
                <label>Reproduction Steps</label>
                <p>{formData.reproduction_steps}</p>
              </div>
            )}
            
            {formData.suspected_area && (
              <div className="preview-section">
                <label>Suspected Area</label>
                <p>{formData.suspected_area}</p>
              </div>
            )}
            
            {formData.confidence !== null && formData.confidence !== undefined && (
              <div className="preview-section">
                <label>AI Confidence</label>
                <p>{Math.round(formData.confidence * 100)}%</p>
              </div>
            )}
          </div>
          
          <div className="form-actions">
            <button
              type="button"
              className="cancel-button"
              onClick={handleStartOver}
            >
              Start Over
            </button>
            <button
              type="button"
              className="secondary-button"
              onClick={handleEdit}
            >
              Edit
            </button>
            <button
              type="button"
              className="submit-button"
              onClick={handleSubmit}
              disabled={submitting}
            >
              {submitting ? 'Saving...' : 'Save Report'}
            </button>
          </div>
        </div>
      )}

      {/* Report Form - Shown when editing */}
      {showForm && isEditing && (
        <div className="card">
          <h2 className="section-title">Edit Report</h2>
          <p className="form-description">
            Modify the fields below as needed, then save your report.
          </p>
          
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
              <label htmlFor="suspected_area">Suspected Area</label>
              <input
                type="text"
                id="suspected_area"
                name="suspected_area"
                value={formData.suspected_area}
                onChange={handleInputChange}
                placeholder="Component or area causing the issue"
              />
            </div>

            {formData.confidence !== null && formData.confidence !== undefined && (
              <div className="form-group">
                <label>AI Confidence</label>
                <input
                  type="text"
                  value={`${Math.round(formData.confidence * 100)}%`}
                  disabled
                  className="confidence-display"
                />
              </div>
            )}

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

            <div className="form-actions">
              <button
                type="button"
                className="cancel-button"
                onClick={() => setIsEditing(false)}
              >
                Back to Preview
              </button>
              <button
                type="submit"
                className="submit-button"
                disabled={submitting}
              >
                {submitting ? 'Saving...' : 'Save Report'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Saved Reports List */}
      <div className="card">
        <h2 className="section-title">Saved Reports ({reports.length})</h2>

        {loading ? (
          <p className="loading-text">Loading reports...</p>
        ) : reports.length === 0 ? (
          <p className="empty-text">No reports yet. Upload a screenshot to get started!</p>
        ) : (
          <div className="reports-list">
            {reports.map((report) => (
              <div 
                key={report.id} 
                className="report-item"
                onClick={() => handleViewReport(report)}
              >
                <div className="report-header">
                  <span className={`severity-badge severity-${report.severity}`}>
                    {report.severity}
                  </span>
                  <h3 className="report-title">{report.title}</h3>
                  <button
                    className="delete-button"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDelete(report.id);
                    }}
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

      {/* Report Details Modal */}
      {selectedReport && (
        <div className="modal-overlay" onClick={handleModalBackdropClick}>
          <div className="modal-content">
            <button 
              className="modal-close-button"
              onClick={handleCloseModal}
              aria-label="Close modal"
            >
              ×
            </button>
            
            <div className="modal-header">
              <span className={`severity-badge severity-${selectedReport.severity}`}>
                {selectedReport.severity}
              </span>
              <h2 className="modal-title">{selectedReport.title}</h2>
            </div>

            <div className="modal-body">
              <div className="modal-field">
                <label>Summary</label>
                <p>{selectedReport.summary || 'No summary provided'}</p>
              </div>

              <div className="modal-field">
                <label>Expected Behavior</label>
                <p>{selectedReport.expected_behavior || 'Not specified'}</p>
              </div>

              <div className="modal-field">
                <label>Actual Behavior</label>
                <p>{selectedReport.actual_behavior || 'Not specified'}</p>
              </div>

              {selectedReport.reproduction_steps && (
                <div className="modal-field">
                  <label>Reproduction Steps</label>
                  <p>{selectedReport.reproduction_steps}</p>
                </div>
              )}

              {selectedReport.suspected_area && (
                <div className="modal-field">
                  <label>Suspected Area</label>
                  <p>{selectedReport.suspected_area}</p>
                </div>
              )}

              {selectedReport.confidence !== null && selectedReport.confidence !== undefined && (
                <div className="modal-field">
                  <label>AI Confidence</label>
                  <p>{Math.round(selectedReport.confidence * 100)}%</p>
                </div>
              )}

              {selectedReport.page_url && (
                <div className="modal-field">
                  <label>Page URL</label>
                  <p>{selectedReport.page_url}</p>
                </div>
              )}

              {selectedReport.user_note && (
                <div className="modal-field">
                  <label>User Note</label>
                  <p>{selectedReport.user_note}</p>
                </div>
              )}

              {selectedReport.image_path && (
                <div className="modal-field">
                  <label>Screenshot</label>
                  <div className="modal-screenshot">
                    <img 
                      src={selectedReport.image_path.startsWith('http') 
                        ? selectedReport.image_path 
                        : `/${selectedReport.image_path}`} 
                      alt="Screenshot" 
                    />
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default HomePage;