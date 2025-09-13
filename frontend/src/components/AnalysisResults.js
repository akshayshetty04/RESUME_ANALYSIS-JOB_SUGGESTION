import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

function AnalysisResults() {
    const location = useLocation();
    const navigate = useNavigate();
    const analysis = location.state?.analysis;

    if (!analysis) {
        return (
            <div className="analysis-results-container">
                <h2>No Analysis Data Available</h2>
                <p>Please go back to the home page to upload your resume and job description.</p>
                <button className="go-back-button" onClick={() => navigate('/home')}>Go to Home</button>
            </div>
        );
    }
    
    const isResumeAnalysis = analysis.analysisType === 'resume';
    const isJobDescAnalysis = analysis.analysisType === 'jobDescription';

    // Chart data and options for Resume vs. Trending Skills
    const resumeChartData = isResumeAnalysis && {
        labels: analysis.trendingSkills?.map(s => s[0]) || [],
        datasets: [
            {
                label: 'Trending Skills in Jobs',
                data: analysis.trendingSkills?.map(s => s[1]) || [],
                backgroundColor: 'rgba(54, 162, 235, 0.5)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1,
            },
            {
                label: 'Your Skills',
                data: analysis.trendingSkills?.map(s => analysis.skills?.includes(s[0]) ? s[1] : 0) || [],
                backgroundColor: 'rgba(75, 192, 192, 0.5)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1,
            },
        ],
    };

    // Chart data and options for My Skills vs. Job Description
    const jobDescChartData = isJobDescAnalysis && {
        labels: [...new Set([...(analysis.mySkills || []), ...(analysis.jobDescriptionSkills || [])])],
        datasets: [
            {
                label: 'Your Skills',
                data: [...new Set([...(analysis.mySkills || []), ...(analysis.jobDescriptionSkills || [])])].map(skill => (analysis.mySkills || []).includes(skill) ? 1 : 0),
                backgroundColor: 'rgba(75, 192, 192, 0.5)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1,
            },
            {
                label: 'Job Required Skills',
                data: [...new Set([...(analysis.mySkills || []), ...(analysis.jobDescriptionSkills || [])])].map(skill => (analysis.jobDescriptionSkills || []).includes(skill) ? 1 : 0),
                backgroundColor: 'rgba(255, 99, 132, 0.5)',
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 1,
            },
        ],
    };

    const jobDescChartOptions = {
      responsive: true,
      scales: {
          y: { beginAtZero: true, max: 1, ticks: { display: false } },
          x: { grid: { display: false } },
      },
      plugins: {
        legend: { position: 'top' },
        title: { display: true, text: 'Your Skills vs. Job Required Skills' },
      },
    };

    const handleGoBack = () => {
         navigate('/home');
    };

    return (
        <div className="analysis-results">
            <button className="go-back-button" onClick={handleGoBack}>Go Back</button>
            
            <h2>Analysis Results</h2>
            
            {isResumeAnalysis && (
                <div className="analysis-section">
                    <h3>Resume Skills vs. Trending Jobs</h3>
                    <p>This chart compares your skills with skills currently in demand based on job market trends.</p>
                    {analysis.trendingSkills && analysis.trendingSkills.length > 0 ? (
                        <div className="chart-container">
                            <Bar data={resumeChartData} options={{ responsive: true, plugins: { legend: { display: true }, title: { display: true, text: 'Resume Skills vs. Trending Jobs' } } }} />
                        </div>
                    ) : (
                        <p>No trending skills data available to visualize.</p>
                    )}
                    <hr/>
                    <h3>Current Job Openings</h3>
                    {analysis.currentJobs && analysis.currentJobs.length > 0 ? (
                        <ul>
                            {analysis.currentJobs.map((job, index) => (
                                <li key={index} className="job-listing">
                                    <strong>{job.title}</strong> at {job.company} - {job.location}
                                    <br/>
                                    <small>Posted: {job.posted_at}</small>
                                    <p>{job.description.substring(0, 150)}...</p>
                                    <a href={job.apply_link} target="_blank" rel="noopener noreferrer">Apply Now</a>
                                </li>
                            ))}
                        </ul>
                    ) : (
                        <p>No current job openings found.</p>
                    )}
                </div>
            )}

            {isJobDescAnalysis && (
                <div className="analysis-section">
                    <h3>Your Skills vs. Job Required Skills</h3>
                    <p>This chart shows how your resume skills match the skills required by the provided job description.</p>
                    {jobDescChartData && (
                        <div className="chart-container">
                            <Bar data={jobDescChartData} options={jobDescChartOptions} />
                        </div>
                    )}
                    <hr/>
                    <h3>Skills You Should Learn</h3>
                    {analysis.skillGaps && analysis.skillGaps.length > 0 ? (
                        <ul>
                            {analysis.skillGaps.map((gap, index) => (
                                <li key={index}>{gap}</li>
                            ))}
                        </ul>
                    ) : (
                        <p>You have all the required skills for this job! 🎉</p>
                    )}
                    <hr/>
                    <h3>Recommended Courses</h3>
                    {analysis.recommendedCourses && analysis.recommendedCourses.length > 0 ? (
                        <ul>
                            {analysis.recommendedCourses.map((rec, index) => (
                                <li key={index}>
                                    <strong>{rec.skill}</strong>: {rec.course}
                                </li>
                            ))}
                        </ul>
                    ) : (
                        <p>No course recommendations at this time.</p>
                    )}
                </div>
            )}
        </div>
    );
}

export default AnalysisResults;