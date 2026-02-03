"use client";
import React, { useState } from 'react';
import axios from 'axios';
import Editor from '@monaco-editor/react';

export default function DataPilotDashboard() {
  const [code, setCode] = useState('DP.Query(data, all)\nDP.Visualize(data, bar_chart)');
  const [logs, setLogs] = useState([]);
  const [image, setImage] = useState(null);

  // YOUR WORKING BACKEND API URL
  const API_URL = "https://tharun-datapilot.onrender.com";

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      setLogs(prev => [...prev, `[LOG] Uploading ${file.name}...`]);
      // Fixed: explicitly call the API_URL
      await axios.post(`${API_URL}/upload`, formData);
      setLogs(prev => [...prev, `[LOG] Dataset Loaded. Ready to run.`]);
    } catch (err) {
      console.error(err);
      setLogs(prev => [...prev, "[ERROR] Upload failed. Make sure API is live."]);
    }
  };

  const handleRun = async () => {
    try {
      setImage(null);
      setLogs(prev => [...prev, "[SYSTEM] Executing script..."]);
      // Fixed: explicitly call the API_URL
      const res = await axios.post(`${API_URL}/execute`, { script: code });
      
      if (res.data.execution_logs) {
        setLogs(res.data.execution_logs);
      }
      if (res.data.visualization) {
        setImage(`data:image/png;base64,${res.data.visualization}`);
      }
    } catch (err) {
      console.error(err);
      setLogs(prev => [...prev, "[ERROR] Connection to API failed."]);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-black text-white p-6">
      <div className="flex justify-between items-center border-b border-gray-800 pb-4">
        <h1 className="text-2xl font-bold text-blue-500"> Tharun's - DATAPILOT </h1>
        <div className="flex gap-4">
          <label className="bg-white text-black px-4 py-2 rounded font-bold cursor-pointer hover:bg-gray-200">
            UPLOAD CSV
            <input type="file" onChange={handleFileUpload} className="hidden" />
          </label>
          <button onClick={handleRun} className="bg-blue-600 px-8 py-2 rounded font-bold hover:bg-blue-700">RUN SCRIPT</button>
        </div>
      </div>

      <div className="flex flex-1 mt-6 gap-6 overflow-hidden">
        <div className="w-1/2 border border-gray-800 rounded overflow-hidden">
          <Editor height="100%" theme="vs-dark" defaultLanguage="python" value={code} onChange={(v) => setCode(v)} />
        </div>
        
        <div className="w-1/2 flex flex-col gap-4 overflow-y-auto">
          <div className="bg-gray-900 p-4 rounded min-h-[200px] border border-gray-800">
            <h3 className="text-blue-400 text-xs font-bold uppercase mb-2">System Logs</h3>
            <div className="space-y-1">
              {logs.map((l, i) => (
                <div key={i} className={`font-mono text-sm ${l.includes('ERROR') ? 'text-red-400' : 'text-green-400'}`}>
                  {l}
                </div>
              ))}
            </div>
          </div>
          
          <div className="bg-gray-900 p-4 rounded flex-1 border border-gray-800 flex flex-col">
            <h3 className="text-blue-400 text-xs font-bold uppercase mb-2">Visualization</h3>
            <div className="flex-1 flex items-center justify-center border border-dashed border-gray-700 rounded">
              {image ? (
                <img src={image} className="max-w-full max-h-full object-contain" alt="Data Visualization" />
              ) : (
                <span className="text-gray-600 italic">No visualization generated</span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}