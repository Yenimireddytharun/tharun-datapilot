"use client";
import React, { useState } from 'react';
import axios from 'axios';
import dynamic from 'next/dynamic';

const Editor = dynamic(() => import('@monaco-editor/react'), { ssr: false });

export default function DataPilotDashboard() {
    const [code, setCode] = useState('DP.Query(data, all)\nDP.Report(data, all)');
    const [logs, setLogs] = useState([]);
    const [image, setImage] = useState(null);
    const [metrics, setMetrics] = useState(null);

    const API_URL = "http://localhost:8001";

    const handleFileUpload = async (event) => {
        const file = event.target.files[0];
        if (!file) return;
        const formData = new FormData();
        formData.append('file', file);
        try {
            setLogs(prev => [...prev, `[LOG] Uploading ${file.name}...`]);
            const res = await axios.post(`${API_URL}/upload`, formData);
            setLogs(prev => [...prev, `[LOG] Loaded ${file.name}`]);
            setLogs(prev => [...prev, `[LOG] Columns: ${res.data.columns.join(', ')}`]);
            setLogs(prev => [...prev, `[LOG] Rows: ${res.data.rows}`]);
            setLogs(prev => [...prev, `[LOG] Dataset Loaded. Ready to run.`]);
        } catch (err) {
            setLogs(prev => [...prev, "[ERROR] Upload failed. Check if API is live."]);
        }
    };

    const handleRun = async () => {
        try {
            setImage(null);
            setMetrics(null);
            setLogs([]);
            setLogs(prev => [...prev, "[SYSTEM] Executing script..."]);
            const res = await axios.post(`${API_URL}/execute`, { script: code });
            if (res.data.execution_logs) {
                setLogs(res.data.execution_logs);
            }
            if (res.data.visualization) {
                setImage(`data:image/png;base64,${res.data.visualization}`);
            }
            if (res.data.metrics && Object.keys(res.data.metrics).length > 0) {
                setMetrics(res.data.metrics);
            }
        } catch (err) {
            setLogs(prev => [...prev, "[ERROR] Connection to API failed."]);
        }
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', background: '#0f0f1a', color: '#e0e0e0', fontFamily: 'monospace' }}>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 24px', background: '#1a1a2e', borderBottom: '1px solid #333' }}>
                <div>
                    <span style={{ fontSize: 22, fontWeight: 700, color: '#61dafb' }}>⚡ Tharun's - DATAPILOT</span>
                    <span style={{ marginLeft: 16, fontSize: 11, color: '#666', background: '#0f0f1a', padding: '3px 10px', borderRadius: 20, border: '1px solid #333' }}>SQL + ML + BI + AI</span>
                </div>
                <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
                    <label style={{ background: '#1a1a2e', color: '#61dafb', border: '1px solid #61dafb', padding: '8px 16px', borderRadius: 6, cursor: 'pointer', fontSize: 12, fontWeight: 700 }}>
                        UPLOAD CSV
                        <input type="file" accept=".csv,.xlsx,.xls" onChange={handleFileUpload} style={{ display: 'none' }} />
                    </label>
                    <button onClick={handleRun} style={{ background: '#61dafb', color: '#000', border: 'none', padding: '8px 24px', borderRadius: 6, cursor: 'pointer', fontSize: 12, fontWeight: 700 }}>
                        ▶ RUN SCRIPT
                    </button>
                </div>
            </div>

            <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>

                <div style={{ width: '45%', borderRight: '1px solid #333', display: 'flex', flexDirection: 'column' }}>
                    <div style={{ padding: '8px 16px', background: '#13131f', borderBottom: '1px solid #222', fontSize: 11, color: '#666' }}>
                        DATAPILOT SCRIPT EDITOR — Commands: DP.Query | DP.Train | DP.Report | DP.Insight | DP.Describe | DP.Visualize | DP.SQL | DP.Filter
                    </div>
                    <div style={{ flex: 1 }}>
                        <Editor
                            height="100%"
                            language="python"
                            theme="vs-dark"
                            value={code}
                            onChange={(v) => setCode(v)}
                            options={{
                                fontSize: 14,
                                minimap: { enabled: false },
                                wordWrap: 'on',
                                lineNumbers: 'on',
                                scrollBeyondLastLine: false,
                                padding: { top: 16 }
                            }}
                        />
                    </div>
                </div>

                <div style={{ width: '55%', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>

                    <div style={{ height: '35%', borderBottom: '1px solid #333', overflow: 'auto', padding: 16 }}>
                        <div style={{ fontSize: 11, color: '#61dafb', fontWeight: 700, marginBottom: 8, textTransform: 'uppercase', letterSpacing: 1 }}>System Logs</div>
                        {logs.length === 0 && (
                            <div style={{ color: '#444', fontSize: 12 }}>Upload a CSV and click RUN SCRIPT to start.</div>
                        )}
                        {logs.map((l, i) => (
                            <div key={i} style={{
                                fontFamily: 'monospace',
                                fontSize: 12,
                                marginBottom: 3,
                                color: l.includes('ERROR') ? '#ff6b6b' : l.includes('AI') ? '#ffd93d' : l.includes('SQL') ? '#a855f7' : l.includes('SYSTEM') ? '#888' : '#6bcb77'
                            }}>
                                {l}
                            </div>
                        ))}
                    </div>

                    <div style={{ flex: 1, overflow: 'auto', padding: 16 }}>
                        {metrics && (
                            <div style={{ marginBottom: 16, padding: 16, background: '#1a1a2e', borderRadius: 8, border: '1px solid #333' }}>
                                <div style={{ color: '#61dafb', fontSize: 11, fontWeight: 700, marginBottom: 12, textTransform: 'uppercase', letterSpacing: 1 }}>ML Metrics Dashboard</div>
                                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 8 }}>
                                    {Object.entries(metrics).map(([key, value]) => (
                                        <div key={key} style={{ background: '#0f0f1a', padding: '12px 8px', borderRadius: 6, textAlign: 'center', border: '1px solid #222' }}>
                                            <div style={{ color: '#888', fontSize: 10, textTransform: 'uppercase', marginBottom: 6, letterSpacing: 1 }}>{key}</div>
                                            <div style={{ color: '#6bcb77', fontSize: 18, fontWeight: 700 }}>{value}</div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {image ? (
                            <div style={{ borderRadius: 8, overflow: 'hidden', border: '1px solid #333' }}>
                                <img src={image} style={{ width: '100%', display: 'block' }} alt="Visualization" />
                            </div>
                        ) : (
                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 200, color: '#333', fontSize: 13, border: '1px dashed #222', borderRadius: 8 }}>
                                No visualization generated
                            </div>
                        )}
                    </div>
                </div>
            </div>

            <div style={{ padding: '6px 24px', background: '#13131f', borderTop: '1px solid #222', display: 'flex', gap: 24, fontSize: 10, color: '#444' }}>
                <span>⚡ DataPilot v1.0</span>
                <span>SQL Engine: DuckDB</span>
                <span>ML Engine: RandomForest</span>
                <span>BI Engine: Matplotlib</span>
                <span>API: localhost:8001</span>
            </div>
        </div>
    );
}