import React from 'react';

function ProgressLog({ progressLogs }) {
  return (
    <div className="progress-log-container">
      <h3>Activity Log</h3>
      <div className="log-messages">
        {progressLogs && progressLogs.length > 0 ? (
          progressLogs.map((log, index) => (
            <p key={index}>{log}</p>
          ))
        ) : (
          <p>No activity yet. Enter an Epic Key and click "Generate Changelog" to start.</p>
        )}
      </div>
    </div>
  );
}

export default ProgressLog;
