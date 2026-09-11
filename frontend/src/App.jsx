import { useState } from "react";
import {
  Upload,
  FileText,
  Sparkles,
  Briefcase,
  CheckCircle,
  AlertCircle,
  TrendingUp,
  Target,
  X,
} from "lucide-react";

import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];

    if (!selectedFile) return;

    if (selectedFile.type !== "application/pdf") {
      setError("Please upload a PDF resume.");
      return;
    }

    setFile(selectedFile);
    setError("");
    setResult(null);
  };

  const analyzeResume = async () => {
    if (!file) {
      setError("Please select a resume first.");
      return;
    }

    setLoading(true);
    setError("");

    const formData = new FormData();

    formData.append("file", file);

    try {
      const response = await fetch(
        "https://ai-resume-analyzer-1-zjnp.onrender.com/api/analyze-resume",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Something went wrong.");
      }

      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const scoreColor = (score) => {
    if (score >= 80) return "excellent";
    if (score >= 60) return "good";
    return "needs-work";
  };

  return (
    <div className="app">

      {/* NAVBAR */}

      <nav className="navbar">

        <div className="brand">
          <div className="brand-icon">
            <Sparkles size={20} />
          </div>

          <span>ResumeAI</span>
        </div>

        <div className="nav-badge">
          AI Powered
        </div>

      </nav>


      {/* HERO */}

      {!result && (
        <main className="hero">

          <div className="hero-content">

            <div className="eyebrow">
              <Sparkles size={16} />
              AI RESUME ANALYZER
            </div>

            <h1>
              Turn your resume into
              <span> career opportunities.</span>
            </h1>

            <p>
              Upload your resume and let AI analyze your skills,
              identify gaps, calculate your ATS score, and find
              the jobs that match you best.
            </p>


            {/* UPLOAD CARD */}

            <div className="upload-card">

              <div className="upload-icon">
                <Upload size={28} />
              </div>

              <h2>
                Upload your resume
              </h2>

              <p>
                PDF files only
              </p>


              <label className="upload-button">

                <input
                  type="file"
                  accept=".pdf"
                  onChange={handleFileChange}
                />

                <Upload size={18} />

                Choose Resume

              </label>


              {file && (

                <div className="selected-file">

                  <FileText size={18} />

                  <span>
                    {file.name}
                  </span>

                  <button
                    onClick={() => setFile(null)}
                  >
                    <X size={16} />
                  </button>

                </div>

              )}


              {error && (

                <div className="error-message">

                  <AlertCircle size={17} />

                  {error}

                </div>

              )}


              <button
                className="analyze-button"
                onClick={analyzeResume}
                disabled={!file || loading}
              >

                {loading ? (
                  <>
                    <span className="spinner"></span>
                    Analyzing Resume...
                  </>
                ) : (
                  <>
                    <Sparkles size={18} />
                    Analyze Resume
                  </>
                )}

              </button>

            </div>


            {/* FEATURES */}

            <div className="features">

              <div>
                <Target size={20} />
                <span>ATS Score</span>
              </div>

              <div>
                <TrendingUp size={20} />
                <span>Skill Analysis</span>
              </div>

              <div>
                <Briefcase size={20} />
                <span>Job Matching</span>
              </div>

            </div>

          </div>

        </main>
      )}


      {/* RESULTS */}

      {result && (

        <main className="dashboard">

          <div className="dashboard-header">

            <div>

              <div className="eyebrow">
                <Sparkles size={16} />
                ANALYSIS COMPLETE
              </div>

              <h1>
                Your Resume Analysis
              </h1>

              <p>
                {result.filename}
              </p>

            </div>


            <button
              className="new-analysis"
              onClick={() => {
                setResult(null);
                setFile(null);
              }}
            >
              Analyze Another
            </button>

          </div>


          {/* SCORE */}

          <section className="score-grid">

            <div className="score-card main-score">

              <div className="score-label">
                Overall Resume Score
              </div>

              <div
                className={`score ${scoreColor(
                  result.analysis.overall_score
                )}`}
              >
                {result.analysis.overall_score}
              </div>

              <div className="score-out-of">
                out of 100
              </div>

              <div className="score-bar">

                <div
                  style={{
                    width: `${result.analysis.overall_score}%`,
                  }}
                />

              </div>

            </div>


            <div className="info-card">

              <Target size={24} />

              <h3>
                Candidate
              </h3>

              <p>
                {result.analysis.candidate_name ||
                  "Candidate"}
              </p>

            </div>


            <div className="info-card">

              <Briefcase size={24} />

              <h3>
                Recommended Jobs
              </h3>

              <p>
                {result.recommendations.length} opportunities
              </p>

            </div>

          </section>


          {/* SUMMARY */}

          <section className="content-card">

            <div className="section-title">

              <FileText size={20} />

              <h2>
                Professional Summary
              </h2>

            </div>

            <p className="summary">
              {result.analysis.summary}
            </p>

          </section>


          {/* SKILLS */}

          <section className="content-card">

            <div className="section-title">

              <TrendingUp size={20} />

              <h2>
                Skills
              </h2>

            </div>

            <div className="skills">

              {result.analysis.skills.map(
                (skill, index) => (

                  <span
                    className="skill"
                    key={index}
                  >
                    {skill}
                  </span>

                )
              )}

            </div>

          </section>


          {/* STRENGTHS + WEAKNESSES */}

          <section className="two-column">

            <div className="content-card">

              <div className="section-title">

                <CheckCircle size={20} />

                <h2>
                  Strengths
                </h2>

              </div>

              <ul>

                {result.analysis.strengths.map(
                  (item, index) => (

                    <li key={index}>
                      {item}
                    </li>

                  )
                )}

              </ul>

            </div>


            <div className="content-card">

              <div className="section-title">

                <AlertCircle size={20} />

                <h2>
                  Areas to Improve
                </h2>

              </div>

              <ul>

                {result.analysis.weaknesses.map(
                  (item, index) => (

                    <li key={index}>
                      {item}
                    </li>

                  )
                )}

              </ul>

            </div>

          </section>


          {/* JOB RECOMMENDATIONS */}

          <section className="jobs-section">

            <div className="section-heading">

              <div>

                <div className="eyebrow">
                  <Briefcase size={16} />
                  AI JOB RECOMMENDATIONS
                </div>

                <h2>
                  Jobs that match your profile
                </h2>

              </div>

            </div>


            <div className="jobs">

              {result.recommendations.map(
                (job) => (

                  <div
                    className="job-card"
                    key={job.id}
                  >

                    <div className="job-top">

                      <div className="company-icon">
                        {job.company.charAt(0)}
                      </div>

                      <div className="job-title">

                        <h3>
                          {job.title}
                        </h3>

                        <p>
                          {job.company} · {job.location}
                        </p>

                      </div>

                      <div
                        className={`match ${
                          job.match_score >= 80
                            ? "high"
                            : job.match_score >= 60
                            ? "medium"
                            : "low"
                        }`}
                      >
                        {job.match_score}% Match
                      </div>

                    </div>


                    <p className="job-description">
                      {job.description}
                    </p>


                    <div className="job-skills">

                      {job.skills.map(
                        (skill, index) => (

                          <span
                            key={index}
                            className={
                              job.matched_skills.includes(
                                skill.toLowerCase()
                              )
                                ? "job-skill matched"
                                : "job-skill"
                            }
                          >

                            {job.matched_skills.includes(
                              skill.toLowerCase()
                            ) && (
                              <CheckCircle size={13} />
                            )}

                            {skill}

                          </span>

                        )
                      )}

                    </div>


                    {job.missing_skills.length > 0 && (

                      <div className="missing">

                        <strong>
                          Skill gaps:
                        </strong>

                        {job.missing_skills.join(", ")}

                      </div>

                    )}

                  </div>

                )
              )}

            </div>

          </section>

        </main>
      )}

    </div>
  );
}

export default App;