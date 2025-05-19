import React from 'react';

export const InsightDisplay: React.FC<{ insights: string }> = ({ insights }) => (
  <div className="vds-alert vds-alert--info vds-padding-block-md">
    <h2 className="vds-heading--medium vds-margin-block-end-sm">Insights</h2>
    <p>{insights}</p>
  </div>
);