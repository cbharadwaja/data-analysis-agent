import React, { useState } from 'react';

export const ChatUI: React.FC<{ onConfig: (query: string) => void }> = ({ onConfig }) => {
  const [prompt, setPrompt] = useState('');

  return (
    <div className="vds-form-group">
      <textarea
        rows={3}
        className="vds-textarea"
        placeholder="Describe the chart you want..."
        value={prompt}
        onChange={e => setPrompt(e.target.value)}
      />
      <button
        onClick={() => onConfig(prompt)}
        className="vds-button vds-button--primary vds-margin-block-start-sm"
      >
        Generate
      </button>
    </div>
  );
};