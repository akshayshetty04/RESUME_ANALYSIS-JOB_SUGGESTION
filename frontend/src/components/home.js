import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';

function Home({ onSignOut }) {
    const [resumeFile, setResumeFile] = useState(null);
    const [jobDescriptionFile, setJobDescriptionFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    const onResumeDrop = (acceptedFiles) => {
        const uploadedFile = acceptedFiles[0];
        if (uploadedFile) {
            setResumeFile(uploadedFile);
            setError(null);
        }
    };

    const onJobDescriptionDrop = (acceptedFiles) => {
        const uploadedFile = acceptedFiles[0];
        if (uploadedFile) {
            setJobDescriptionFile(uploadedFile);
            setError(null);
        }
    };

    const { getRootProps: getResumeRootProps, getInputProps: getResumeInputProps, isDragActive: isResumeDragActive } = useDropzone({
        onDrop: onResumeDrop,
        accept: {
            'application/pdf': ['.pdf'],
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
        }
    });

    const { getRootProps: getJobDescRootProps, getInputProps: getJobDescInputProps, isDragActive: isJobDescDragActive } = useDropzone({
        onDrop: onJobDescriptionDrop,
        accept: {
            'application/pdf': ['.pdf'],
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
        }
    });

    const handleResumeAnalysis = async () => {
        if (!resumeFile) {
            setError("Please upload a resume file to analyze.");
            return;
        }
        setLoading(true);
        setError(null);
        const formData = new FormData();
        formData.append('resume', resumeFile);

        try {
            const response = await axios.post('http://localhost:5000/api/analyze-resume', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });
            navigate('/analysis', { state: { analysis: response.data } });
        } catch (err) {
            console.error("Analysis error:", err);
            setError("Failed to analyze resume. Please check the backend server.");
        } finally {
            setLoading(false);
        }
    };

    const handleJobDescriptionAnalysis = async () => {
        if (!jobDescriptionFile) {
            setError("Please upload a job description file to analyze.");
            return;
        }
        setLoading(true);
        setError(null);
        const formData = new FormData();
        formData.append('jobDescription', jobDescriptionFile);
        if (resumeFile) {
            formData.append('resume', resumeFile);
        }

        try {
            const response = await axios.post('http://localhost:5000/api/analyze-job-description', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });
            navigate('/analysis', { state: { analysis: response.data } });
        } catch (err) {
            console.error("Analysis error:", err);
            setError("Failed to analyze job description. Please check the backend server.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <main className="main-content">
            <div className="button-container">
                <button onClick={onSignOut} className="header-button">Logout</button>
                <button onClick={() => alert("Help text here.")} className="header-button">Help</button>
            </div>

            <div className="upload-section">
                <div className="upload-container">
                    <h3>Upload Resume</h3>
                    <div {...getResumeRootProps()} className={`dropzone ${isResumeDragActive ? 'active' : ''}`}>
                        <input {...getResumeInputProps()} />
                        <span className="upload-icon">⬆️</span>
                        {isResumeDragActive ? (
                            <p>Drop the resume file here ...</p>
                        ) : (
                            <p>Drag 'n' drop a resume file, or click to select one</p>
                        )}
                    </div>
                    {resumeFile && <p className="file-info">Selected file: <strong>{resumeFile.name}</strong></p>}
                    <button onClick={handleResumeAnalysis} disabled={loading || !resumeFile} className="analyze-button">
                        {loading ? 'Analyzing...' : 'Analyze Resume'}
                    </button>
                </div>

                <div className="upload-container">
                    <h3>Upload Job Description</h3>
                    <div {...getJobDescRootProps()} className={`dropzone ${isJobDescDragActive ? 'active' : ''}`}>
                        <input {...getJobDescInputProps()} />
                        <span className="upload-icon">⬆️</span>
                        {isJobDescDragActive ? (
                            <p>Drop the job description file here ...</p>
                        ) : (
                            <p>Drag 'n' drop a job description file, or click to select one</p>
                        )}
                    </div>
                    {jobDescriptionFile && <p className="file-info">Selected file: <strong>{jobDescriptionFile.name}</strong></p>}
                    <button onClick={handleJobDescriptionAnalysis} disabled={loading || !jobDescriptionFile} className="analyze-button">
                        {loading ? 'Analyzing...' : 'Analyze Job Description'}
                    </button>
                </div>
            </div>
            
            {error && <p className="error-message">{error}</p>}
        </main>
    );
}

export default Home;