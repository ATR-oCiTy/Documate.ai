import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import './App.css';
import Header from './Header';
import JiraInputForm from './JiraInputForm';
import ProgressLog from './ProgressLog';
import PreviewArea from './PreviewArea';

const API_BASE_URL = 'http://localhost:5000/api';

function App() {
  const [epicKey, setEpicKey] = useState('');
  const [progressLogs, setProgressLogs] = useState(["Enter an Epic Key and click 'Generate Changelog'."]);
  const [previewContent, setPreviewContent] = useState("Preview will appear here once the changelog is generated.");
  const [isLoading, setIsLoading] = useState(false);
  const [jobId, setJobId] = useState(null);
  const [pollingIntervalId, setPollingIntervalId] = useState(null);

  const clearPolling = useCallback(() => {
    if (pollingIntervalId) {
      clearInterval(pollingIntervalId);
      setPollingIntervalId(null);
    }
  }, [pollingIntervalId]);

  const pollJobStatus = useCallback(async (currentJobId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/status/${currentJobId}`);
      const { status, logs, previewContent: newPreviewContent } = response.data;

      // Only update logs if there are new messages.
      // Backend logs are cumulative, so we can replace or append strategically.
      // For simplicity, let's assume backend sends all logs each time.
      setProgressLogs(logs || ["Polling for status..."]);

      if (newPreviewContent) {
        setPreviewContent(newPreviewContent);
      }

      if (status === "completed") {
        setIsLoading(false);
        setProgressLogs(prevLogs => [...prevLogs, "Changelog generation complete!"]);
        clearPolling();
      } else if (status === "error") {
        setIsLoading(false);
        setProgressLogs(prevLogs => [...prevLogs, "Error during changelog generation."]);
        clearPolling();
      } else if (status === "processing") {
        // Continue polling: setTimeout is managed by the effect calling this
      }
    } catch (error) {
      setIsLoading(false);
      setProgressLogs(prevLogs => [...prevLogs, `Error fetching status: ${error.message}`]);
      clearPolling();
    }
  }, [clearPolling]);


  useEffect(() => {
    if (jobId && isLoading) {
      const intervalId = setInterval(() => {
        pollJobStatus(jobId);
      }, 2000); // Poll every 2 seconds
      setPollingIntervalId(intervalId);

      return () => clearInterval(intervalId); // Cleanup on component unmount or if jobId/isLoading changes
    }
  }, [jobId, isLoading, pollJobStatus]);


  const handleGenerateChangelog = async () => {
    clearPolling(); // Clear any existing polling
    setIsLoading(true);
    setJobId(null); // Reset job ID
    setProgressLogs(["Initiating changelog generation for " + epicKey + "..."]);
    setPreviewContent("Preview will appear here once the changelog is generated."); // Reset preview

    try {
      const response = await axios.post(`${API_BASE_URL}/generate-changelog`, { epicKey });
      if (response.status === 202) { // Accepted
        const { jobId: newJobId } = response.data;
        setJobId(newJobId);
        setProgressLogs(prevLogs => [...prevLogs, `Request sent to backend. Job ID: ${newJobId}. Awaiting progress...`]);
        // Polling will start due to useEffect watching jobId and isLoading
      } else {
        // Handle unexpected success status codes if necessary
        setIsLoading(false);
        setProgressLogs(prevLogs => [...prevLogs, `Unexpected response from server: ${response.status}`]);
      }
    } catch (error) {
      setIsLoading(false);
      let errorMessage = "Error starting process.";
      if (error.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        errorMessage = `Error starting process: ${error.response.data.error || error.message} (Status: ${error.response.status})`;
      } else if (error.request) {
        // The request was made but no response was received
        errorMessage = "Error starting process: No response from server. Ensure the backend is running.";
      } else {
        // Something happened in setting up the request that triggered an Error
        errorMessage = `Error starting process: ${error.message}`;
      }
      setProgressLogs(prevLogs => [...prevLogs, errorMessage]);
    }
  };

  return (
    <div className="App">
      <Header />
      <main className="main-content">
        <div className="left-column">
          <JiraInputForm
            epicKey={epicKey}
            onEpicKeyChange={setEpicKey}
            onSubmit={handleGenerateChangelog}
            isLoading={isLoading}
          />
          <ProgressLog progressLogs={progressLogs} />
        </div>
        <div className="right-column">
          <PreviewArea previewContent={previewContent} />
        </div>
      </main>
    </div>
  );
}

export default App;
