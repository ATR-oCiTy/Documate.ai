import React from 'react';

function PreviewArea({ previewContent }) {
  return (
    <div className="preview-area-container">
      <h3>Confluence Page Preview</h3>
      <div
        className="preview-content"
        dangerouslySetInnerHTML={{ __html: previewContent }}
      />
    </div>
  );
}

export default PreviewArea;
