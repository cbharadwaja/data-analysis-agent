import React, { useState } from 'react';
import { ChatUI } from './components/ChatUI';
import { InsightDisplay } from './components/InsightDisplay';
import { DataGrid } from './components/DataGrid';
import { ChartDisplay } from './components/ChartDisplay';

function App() {
  const [insights, setInsights] = useState('');
  const [charts, setCharts] = useState([]);
  const [tableData, setTableData] = useState([]);

  const handleAnalyze = async (query: string) => {
    const res = await fetch('/analyze', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({nl_query:query})});
    const { insights, charts, tableData } = await res.json();
    setInsights(insights); setCharts(charts); setTableData(tableData);
  };

  return (
    <div className="vds-app">
      <header className="vds-header vds-header--main">
        <div className="vds-container vds-flex vds-justify-between vds-align-center">
          <img src="/visa-logo.svg" alt="Visa" className="vds-brand-logo" />
          <nav><ul className="vds-nav-list"><li><a href="#" className="vds-link">Home</a></li></ul></nav>
        </div>
      </header>
      <main className="vds-container vds-padding-block-md">
        <h1 className="vds-heading--large vds-margin-block-end-md">Generative Data Analysis UI</h1>
        <ChatUI onConfig={handleAnalyze} />
        {insights && <InsightDisplay insights={insights} />}
        {tableData.length>0 && <><h2 className="vds-heading--medium">Data Table</h2><DataGrid data={tableData} /></>}
        {charts.map((c,i)=><div key={i}><h3 className="vds-heading--small">{c.title}</h3><ChartDisplay chartData={c.chartData} type={c.type} onElementClick={async(label,field)=>{const r=await fetch('/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({nl_query:`Show details where ${field} is ${label}`})});const d=await r.json(); setTableData(d.tableData); setCharts(d.charts);}} /></div>)}
      </main>
      <footer className="vds-footer vds-padding-block-md vds-background-color-light"><div className="vds-container vds-text-align-center">© Visa</div></footer>
    </div>
  );
}
export default App;