import React from 'react';
import { Line, Bar } from 'react-chartjs-2';

interface ChartDisplayProps {
  chartData: any;
  type: 'line' | 'bar';
  onElementClick?: (label: string, field: string) => void;
}

export const ChartDisplay: React.FC<ChartDisplayProps> = ({ chartData, type, onElementClick }) => {
  const options = {
    onClick: (evt: any, elems: any[]) => {
      if (elems.length && onElementClick) {
        const idx = elems[0].index;
        const label = chartData.labels[idx];
        const field = chartData.datasets[0].label;
        onElementClick(label, field);
      }
    }
  };

  return (
    <div className="vds-card vds-padding-block-md">
      {type === 'line' ? <Line data={chartData} options={options} /> : <Bar data={chartData} options={options} />}
    </div>
  );
};