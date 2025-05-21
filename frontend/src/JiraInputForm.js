import React from 'react';

function JiraInputForm({ epicKey, onEpicKeyChange, onSubmit, isLoading }) {
  const handleSubmit = (event) => {
    event.preventDefault(); // Prevent default form submission
    onSubmit();
  };

  return (
    <form onSubmit={handleSubmit} className="jira-input-form">
      <label htmlFor="epic-key-input">Enter Jira Epic Key</label>
      <input
        type="text"
        id="epic-key-input"
        placeholder="PROJECT-123"
        value={epicKey}
        onChange={(e) => onEpicKeyChange(e.target.value)}
        disabled={isLoading}
      />
      <button type="submit" disabled={isLoading}>
        {isLoading ? 'Generating...' : 'Generate Changelog'}
      </button>
    </form>
  );
}

export default JiraInputForm;
