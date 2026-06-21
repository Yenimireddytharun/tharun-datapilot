"use client";
import React, { useState } from 'react';
import axios from 'axios';
import dynamic from 'next/dynamic';

const Editor = dynamic(() => import('@monaco-editor/react'), { ssr: false });

const DEFAULT_CODE = `DP.Query(data, all)
DP.Describe(data, info)
DP.Train(data, Sales)
DP.Insight(data, all)
DP.Report(data, all)`;

export default function DataPilotDashboard() {
    const [code, setCode] = useState(DEFAULT_CODE);
    const [logs, setLogs] = useState([]);
    const [image, setImage] = useState(null);
    const [metrics, setMetrics] = useState(null);
    const [table, setTable] = useState(null);
    const [loading, setLoading] = useState(false);
    const [uploadedFile, setUploadedFile] = useState(null);

    const API_URL = "http://localhost:8001";

    const handleClear = () => {
        setLogs([]);
        setImage(null);
        setMetrics(null);
        setTable(null);
        setCode('');
        setUploadedFile(null);
    };

    const handleFileUpload = async (event) => {
        const file = event.target.files[0];
        if (!file) return;
        const formData = new FormData();
        formData.append('file', file);
        try {
            setLogs(prev => [...prev, `[LOG] Uploading ${file.name}...`]);
            const res = await axios.post(`${API_URL}/upload`, formData);
            setUploadedFile(file.name);
            setLogs(prev => [
                ...prev,
                `[LOG] Loaded ${file.name}`,
                `[LOG] Columns: ${res.data.columns.join(', ')}`,
                `[LOG] Rows: ${res.data.rows}`,
                `[LOG] Dataset Loaded. Ready to run.`
            ]);
        } catch (err) {
            setLogs(prev => [...prev, "[ERROR] Upload failed. Check if API is live."]);
        }
    };

    const handleRun = async () => {
        try {
            setLoading(true);
            setImage(null);
            setMetrics(null);
            setTable(null);
            setLogs([]);
            setLogs(prev => [...prev, "[SYSTEM] Executing script..."]);
            const res = await axios.post(`${API_URL}/execute`, { script: code });
            if (res.data.execution_logs) setLogs(res.data.execution_logs);
            if (res.data.visualization) setImage(`data:image/png;base64,${res.data.visualization}`);
            if (res.data.metrics && Object.keys(res.data.metrics).length > 0) setMetrics(res.data.metrics);
            if (res.data.table && res.data.table.length > 0) setTable(res.data.table);
        } catch (err) {
            setLogs(prev => [...prev, "[ERROR] Connection to API failed."]);
        } finally {
            setLoading(false);
        }
    };

    const logColor = (l) => {
        if (l.includes('ERROR')) return '#ff6b6b';
        if (l.includes('[AI]')) return '#ffd93d';
        if (l.includes('[SQL]')) return '#a855f7';
        if (l.includes('SYSTEM')) return '#888';
        if (l.includes('COMPLETE') || l.includes('SUCCESS') || l.includes('DONE')) return '#6bcb77';
        return '#61dafb';
    };

    return (
        <div style={{ display:'flex', flexDirection:'column', height:'100vh', background:'#0a0a14', color:'#e0e0e0', fontFamily:'monospace', overflow:'hidden' }}>

            <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', padding:'10px 20px', background:'#1a1a2e', borderBottom:'1px solid #2a2a4a', flexShrink:0 }}>
                <div style={{ display:'flex', alignItems:'center', gap:12 }}>
                    <span style={{ fontSize:20, fontWeight:700, color:'#61dafb' }}>⚡ Tharun's — DATAPILOT</span>
                    <span style={{ fontSize:10, color:'#444', background:'#0a0a14', padding:'3px 10px', borderRadius:20, border:'1px solid #2a2a4a' }}>SQL + ML + BI + AI</span>
                    {uploadedFile && (
                        <span style={{ fontSize:10, color:'#6bcb77', background:'#0f2a1a', padding:'3px 10px', borderRadius:20, border:'1px solid #6bcb77' }}>
                            📂 {uploadedFile}
                        </span>
                    )}
                </div>
                <div style={{ display:'flex', gap:8, alignItems:'center' }}>
                    <label style={{ background:'#1a1a2e', color:'#61dafb', border:'1px solid #61dafb', padding:'7px 14px', borderRadius:6, cursor:'pointer', fontSize:11, fontWeight:700 }}>
                        📁 UPLOAD CSV
                        <input type="file" accept=".csv,.xlsx,.xls" onChange={handleFileUpload} style={{ display:'none' }} />
                    </label>
                    <button onClick={handleClear} style={{ background:'transparent', color:'#ff6b6b', border:'1px solid #ff6b6b', padding:'7px 14px', borderRadius:6, cursor:'pointer', fontSize:11, fontWeight:700 }}>
                        🗑 CLEAR
                    </button>
                    <button onClick={handleRun} disabled={loading} style={{ background: loading ? '#333' : '#61dafb', color:'#000', border:'none', padding:'7px 20px', borderRadius:6, cursor: loading ? 'not-allowed' : 'pointer', fontSize:11, fontWeight:700 }}>
                        {loading ? '⏳ Running...' : '▶ RUN SCRIPT'}
                    </button>
                </div>
            </div>

            <div style={{ display:'flex', flex:1, overflow:'hidden' }}>

                <div style={{ width:'30%', borderRight:'1px solid #2a2a4a', display:'flex', flexDirection:'column', minWidth:0 }}>
                    <div style={{ padding:'6px 12px', background:'#13131f', borderBottom:'1px solid #2a2a4a', fontSize:9, color:'#555', lineHeight:1.6 }}>
                        SCRIPT EDITOR — DP.Query | DP.Train | DP.Report | DP.Insight | DP.Describe | DP.Visualize | DP.SQL | DP.Filter
                    </div>
                    <div style={{ flex:1 }}>
                        <Editor
                            height="100%"
                            language="python"
                            theme="vs-dark"
                            value={code}
                            onChange={(v) => setCode(v || '')}
                            options={{ fontSize:13, minimap:{ enabled:false }, wordWrap:'on', lineNumbers:'on', scrollBeyondLastLine:false, padding:{ top:12 } }}
                        />
                    </div>
                </div>

                <div style={{ width:'30%', borderRight:'1px solid #2a2a4a', display:'flex', flexDirection:'column', overflow:'hidden' }}>
                    <div style={{ padding:'6px 12px', background:'#13131f', borderBottom:'1px solid #2a2a4a', fontSize:9, color:'#61dafb', fontWeight:700, letterSpacing:1 }}>
                        SYSTEM LOGS
                    </div>
                    <div style={{ flex:1, overflow:'auto', padding:12 }}>
                        {logs.length === 0 ? (
                            <div style={{ color:'#333', fontSize:11, marginTop:20, textAlign:'center' }}>Upload a file and click RUN SCRIPT</div>
                        ) : (
                            logs.map((l, i) => (
                                <div key={i} style={{ fontFamily:'monospace', fontSize:11, marginBottom:4, color: logColor(l), lineHeight:1.5, wordBreak:'break-word' }}>
                                    {l}
                                </div>
                            ))
                        )}
                    </div>
                </div>

                <div style={{ width:'40%', display:'flex', flexDirection:'column', overflow:'hidden' }}>
                    <div style={{ padding:'6px 12px', background:'#13131f', borderBottom:'1px solid #2a2a4a', fontSize:9, color:'#61dafb', fontWeight:700, letterSpacing:1 }}>
                        RESULTS — ML METRICS / SQL TABLE / VISUALIZATION
                    </div>
                    <div style={{ flex:1, overflow:'auto', padding:12 }}>

                        {metrics && (
                            <div style={{ marginBottom:12, padding:12, background:'#1a1a2e', borderRadius:8, border:'1px solid #2a2a4a' }}>
                                <div style={{ color:'#61dafb', fontSize:9, fontWeight:700, marginBottom:10, textTransform:'uppercase', letterSpacing:1 }}>ML Metrics Dashboard</div>
                                <div style={{ display:'grid', gridTemplateColumns:'repeat(3, 1fr)', gap:6 }}>
                                    {Object.entries(metrics).map(([key, value]) => (
                                        <div key={key} style={{ background:'#0a0a14', padding:'10px 6px', borderRadius:6, textAlign:'center', border:'1px solid #2a2a4a' }}>
                                            <div style={{ color:'#555', fontSize:9, textTransform:'uppercase', marginBottom:4, letterSpacing:1 }}>{key}</div>
                                            <div style={{ color:'#6bcb77', fontSize:15, fontWeight:700 }}>{value}</div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {table && table.length > 0 && (
                            <div style={{ marginBottom:12, borderRadius:8, border:'1px solid #2a2a4a', overflow:'hidden' }}>
                                <div style={{ background:'#1a1a2e', padding:'6px 12px', borderBottom:'1px solid #2a2a4a' }}>
                                    <span style={{ color:'#a855f7', fontSize:9, fontWeight:700, textTransform:'uppercase', letterSpacing:1 }}>SQL Result — {table.length} rows</span>
                                </div>
                                <div style={{ overflowX:'auto' }}>
                                    <table style={{ width:'100%', borderCollapse:'collapse', fontSize:11 }}>
                                        <thead>
                                            <tr>
                                                {Object.keys(table[0]).map(col => (
                                                    <th key={col} style={{ background:'#13131f', color:'#61dafb', padding:'6px 10px', textAlign:'left', borderBottom:'1px solid #2a2a4a', fontWeight:700, textTransform:'uppercase', fontSize:9, letterSpacing:1, whiteSpace:'nowrap' }}>
                                                        {col}
                                                    </th>
                                                ))}
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {table.map((row, i) => (
                                                <tr key={i} style={{ background: i % 2 === 0 ? '#0a0a14' : '#13131f' }}>
                                                    {Object.values(row).map((val, j) => (
                                                        <td key={j} style={{ padding:'5px 10px', borderBottom:'1px solid #1a1a2e', color:'#e0e0e0', whiteSpace:'nowrap', fontSize:11 }}>
                                                            {String(val)}
                                                        </td>
                                                    ))}
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        )}

                        {image ? (
                            <div style={{ borderRadius:8, overflow:'hidden', border:'1px solid #2a2a4a' }}>
                                <div style={{ background:'#1a1a2e', padding:'6px 12px', borderBottom:'1px solid #2a2a4a' }}>
                                    <span style={{ color:'#ffd93d', fontSize:9, fontWeight:700, textTransform:'uppercase', letterSpacing:1 }}>Visualization</span>
                                </div>
                                <img src={image} style={{ width:'100%', display:'block' }} alt="Visualization" />
                            </div>
                        ) : (
                            !metrics && !table && (
                                <div style={{ display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', height:200, color:'#2a2a4a', fontSize:12, border:'1px dashed #2a2a4a', borderRadius:8 }}>
                                    <div style={{ fontSize:32, marginBottom:8 }}>📊</div>
                                    <div>Results will appear here</div>
                                </div>
                            )
                        )}
                    </div>
                </div>
            </div>

            <div style={{ padding:'5px 20px', background:'#13131f', borderTop:'1px solid #2a2a4a', display:'flex', gap:20, fontSize:9, color:'#333', flexShrink:0 }}>
                <span>⚡ DataPilot v1.0</span>
                <span>SQL: DuckDB</span>
                <span>ML: RandomForest</span>
                <span>BI: Matplotlib</span>
                <span>API: localhost:8001</span>
                <span style={{ marginLeft:'auto', color: loading ? '#ffd93d' : '#6bcb77' }}>{loading ? '⏳ Processing...' : '✅ Ready'}</span>
            </div>
        </div>
    );
}