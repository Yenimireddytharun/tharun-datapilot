"use client";
import React, { useState } from 'react';
import Editor from '@monaco-editor/react';
import axios from 'axios';

export default function DataPilotDashboard() {
  const [code, setCode] = useState('DP.Query(data, all)\nDP.Visualize(data, bar_chart)');
  const [logs, setLogs] = useState([]);
  const [image, setImage] = useState(null);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    try {
      setLogs(prev => [...prev, `[LOG] Uploading ${file.name}...`]);
      await axios.post('http://tharun-datapilot.onrender.com/upload', formData);
      setLogs(prev => [...prev, `[LOG] Dataset Loaded. Ready to run.`]);
    } catch (err) {
      setLogs(prev => [...prev, "[ERROR] Upload failed."]);
    }
  };

  const handleRun = async () => {
    try {
      setImage(null); // Clear previous result
      setLogs(prev => [...prev, "[SYSTEM] Executing script..."]);

      const res = await axios.post(`https://tharun-datapilot.onrender.com/execute`, { script: code });
      
      // Update logs
      if (res.data.execution_logs) {
        setLogs(res.data.execution_logs);
      }

      // Display Visualization
      if (res.data.visualization) {
        setImage(`data:image/png;base64,${res.data.visualization}`);
      } else {
        setLogs(prev => [...prev, "[WARN] No visualization returned."]);
      }
    } catch (err) {
      setLogs(prev => [...prev, "[ERROR] Connection to API failed."]);
    }
  };

  const downloadChart = () => {
    const link = document.createElement('a');
    link.href = image;
    link.download = 'DataPilot_Result.png';
    link.click();
  };

  return (
    <div className="flex flex-col h-screen bg-black text-white font-sans">
      <div className="p-6 bg-black border-b border-gray-900 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold tracking-tight mb-4">DATAPILOT <span className="text-blue-500">PRO</span></h1>
          <div className="flex gap-3">
            <label className="bg-white text-black px-4 py-2 rounded text-xs font-bold cursor-pointer hover:bg-yellow-300 transition">
              Choose File
              <input type="file" onChange={handleFileUpload} className="hidden" />
            </label>
            <button onClick={() => {setImage(null); setLogs([]);}} className="bg-gray-700 px-4 py-2 rounded text-pink font-bold">CLEAR ALL</button>
          </div>
        </div>
        <button onClick={handleRun} className="bg-white text-black px-10 py-3 rounded text-yellow font-black hover:bg-gray-200 transition">RUN SCRIPT</button>
      </div>

      <div className="flex flex-1 overflow-hidden">
        <div className="w-1/2 border-r border-[#756d6d]-900">
          <Editor height="100%" theme="vs-dark" defaultLanguage="python" value={code} onChange={(v) => setCode(v)} options={{ fontSize: 14, minimap: { enabled: false } }} />
        </div>

        <div className="w-1/2 p-6 overflow-y-auto bg-#d1abab flex flex-col gap-8">
          <div>
            <h3 className="text-blue-500 text-[10px] font-black uppercase tracking-[0.2em] mb-4">System Logs</h3>
            <div className="font-mono text-sm">
              {logs.map((l, i) => <div key={i} className="text-pink-500 mb-1">{l}</div>)}
            </div>
          </div>

          <div className="mt-8">
            <h3 className="text-blue-500 text-[10px] font-violet uppercase tracking-[0.2em] mb-4 border-b border-gray-800 pb-2">Visualization</h3>
            {image ? (
              <div className="bg-white p-4 rounded-lg text-center animate-in fade-in zoom-in duration-500">
                <div className="flex justify-end mb-2">
                  <button onClick={downloadChart} className="bg-[#eddfdf]-600 text-[#4f6cc4] text-[9px] px-3 py-1 rounded font-bold">DOWNLOAD PNG →</button>
                </div>
                <img src={image} className="mx-auto max-w-full h-auto rounded shadow-sm" alt="Result" />
                <p className="text-red-500 text-[10px] mt-2 font-bold uppercase">Visualization Ready</p>
              </div>
            ) : (
              <div className="border-2 border-dashed border-gray-800 h-64 rounded-xl flex items-center justify-center text-[#4f6cc4]-500 tracking-widest">NO VISUALIZATION GENERATED</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}