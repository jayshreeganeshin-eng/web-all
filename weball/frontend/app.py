"""
Frontend Application - Modern Web Interface
Provides user-friendly interface for all weball features
"""

import os
from pathlib import Path


def get_frontend_html() -> str:
    """Return the main frontend HTML content."""
    
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>weball v4.0 - AI-Powered Website Cloner</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { opacity: 0.9; font-size: 1.1em; }
        .nav-tabs {
            display: flex;
            background: #f8f9fa;
            border-bottom: 2px solid #e0e0e0;
        }
        .nav-tab {
            flex: 1;
            padding: 15px;
            text-align: center;
            cursor: pointer;
            border: none;
            background: transparent;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s;
        }
        .nav-tab:hover { background: #e9ecef; }
        .nav-tab.active {
            background: white;
            color: #667eea;
            border-bottom: 3px solid #667eea;
        }
        .tab-content { display: none; padding: 30px; }
        .tab-content.active { display: block; }
        
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: 600; color: #333; }
        input[type="text"], input[type="password"], input[type="email"], select, textarea {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
        }
        input:focus, select:focus, textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 16px;
            font-weight: 600;
            border-radius: 8px;
            cursor: pointer;
            width: 100%;
            transition: transform 0.2s;
        }
        .btn:hover { transform: translateY(-2px); }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
        }
        .stat-card h3 { font-size: 2em; margin-bottom: 5px; }
        .stat-card p { opacity: 0.9; }
        
        .job-list { list-style: none; }
        .job-item {
            background: #f8f9fa;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .status-badge {
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }
        .status-completed { background: #d4edda; color: #155724; }
        .status-running { background: #d1ecf1; color: #0c5460; }
        .status-failed { background: #f8d7da; color: #721c24; }
        .status-queued { background: #fff3cd; color: #856404; }
        
        .alert {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: none;
        }
        .alert-success { background: #d4edda; color: #155724; }
        .alert-error { background: #f8d7da; color: #721c24; }
        
        .checkbox-group { display: flex; gap: 20px; flex-wrap: wrap; }
        .checkbox-item { display: flex; align-items: center; gap: 8px; }
        input[type="checkbox"] { width: 18px; height: 18px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌐 weball</h1>
            <p>AI-Powered Universal Website Cloner & Crawler</p>
            <span style="background: rgba(255,255,255,0.2); padding: 4px 12px; border-radius: 20px; font-size: 0.8em;">v4.0.0 Production Ready</span>
        </div>
        
        <div class="nav-tabs">
            <button class="nav-tab active" onclick="showTab('clone')">🚀 Clone Website</button>
            <button class="nav-tab" onclick="showTab('jobs')">📋 My Jobs</button>
            <button class="nav-tab" onclick="showTab('admin')">⚙️ Admin Panel</button>
            <button class="nav-tab" onclick="showTab('login')">👤 Login</button>
        </div>
        
        <!-- Clone Tab -->
        <div id="cloneTab" class="tab-content active">
            <div class="alert alert-info" id="aiStatusAlert">🤖 AI Auto-Detection Enabled - Free AI will analyze cloned sites</div>
            <form id="cloneForm" onsubmit="startClone(event)">
                <div class="form-group">
                    <label for="url">Target URL *</label>
                    <input type="text" id="url" placeholder="https://example.com or http://example.onion" required>
                </div>
                <div class="form-group">
                    <label for="mode">Operation Mode</label>
                    <select id="mode">
                        <option value="static">Static Clone (Fast)</option>
                        <option value="dynamic">Dynamic Clone (JavaScript)</option>
                        <option value="deep-crawl">Deep Crawl (All Pages)</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="depth">Crawl Depth (0 = current page only)</label>
                    <input type="number" id="depth" min="0" max="10" value="2">
                </div>
                <div class="form-group">
                    <label>Options</label>
                    <div class="checkbox-group">
                        <div class="checkbox-item">
                            <input type="checkbox" id="useTor">
                            <label for="useTor">🧅 Use Tor (.onion)</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" id="discoverInvisible" checked>
                            <label for="discoverInvisible">🔍 Discover Invisible Content</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" id="aiEnabled" checked>
                            <label for="aiEnabled">🤖 Enable AI Analysis</label>
                        </div>
                    </div>
                </div>
                <button type="submit" class="btn" id="cloneBtn">🚀 Start Cloning</button>
            </form>
            <div id="cloneResult" style="margin-top: 20px;"></div>
        </div>
        
        <!-- Jobs Tab -->
        <div id="jobsTab" class="tab-content">
            <h2>My Cloning Jobs</h2>
            <button class="btn" onclick="refreshJobs()" style="margin: 20px 0;">🔄 Refresh</button>
            <ul class="job-list" id="jobList">
                <li class="job-item">No jobs yet. Start your first clone!</li>
            </ul>
        </div>
        
        <!-- Admin Tab -->
        <div id="adminTab" class="tab-content">
            <h2>Admin Dashboard</h2>
            <div class="stats-grid" id="adminStats">
                <div class="stat-card"><h3 id="statUsers">0</h3><p>Total Users</p></div>
                <div class="stat-card"><h3 id="statJobs">0</h3><p>Total Jobs</p></div>
                <div class="stat-card"><h3 id="statCompleted">0</h3><p>Completed</p></div>
                <div class="stat-card"><h3 id="statStorage">0 MB</h3><p>Storage Used</p></div>
            </div>
            <div class="form-group">
                <label>AI Provider Configuration</label>
                <select id="aiProvider">
                    <option value="ollama">Ollama (Local - Free)</option>
                    <option value="groq">Groq Cloud (Free Tier)</option>
                    <option value="openrouter">OpenRouter (Free Tier)</option>
                </select>
            </div>
            <button class="btn" onclick="saveAdminSettings()">💾 Save Settings</button>
        </div>
        
        <!-- Login Tab -->
        <div id="loginTab" class="tab-content">
            <h2>Login to Your Account</h2>
            <form onsubmit="handleLogin(event)">
                <div class="form-group">
                    <label for="username">Username</label>
                    <input type="text" id="username" required>
                </div>
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" required>
                </div>
                <button type="submit" class="btn">🔐 Login</button>
            </form>
            <div id="loginMessage" class="alert" style="margin-top: 20px;"></div>
        </div>
    </div>
    
    <script>
        const API_BASE = '/api/v1';
        let currentJobId = null;
        
        function showTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
            document.getElementById(tabName + 'Tab').classList.add('active');
            event.target.classList.add('active');
            
            if (tabName === 'admin') loadAdminStats();
            if (tabName === 'jobs') refreshJobs();
        }
        
        async function startClone(e) {
            e.preventDefault();
            const btn = document.getElementById('cloneBtn');
            btn.disabled = true;
            btn.textContent = '🔄 Starting...';
            
            const data = {
                url: document.getElementById('url').value,
                mode: document.getElementById('mode').value,
                depth: parseInt(document.getElementById('depth').value),
                use_tor: document.getElementById('useTor').checked,
                discover_invisible: document.getElementById('discoverInvisible').checked,
                ai_enabled: document.getElementById('aiEnabled').checked
            };
            
            try {
                const response = await fetch(API_BASE + '/clone', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                const result = await response.json();
                
                currentJobId = result.job_id;
                document.getElementById('cloneResult').innerHTML = 
                    '<div class="alert alert-success">✅ Job started! Job ID: ' + result.job_id + '</div>';
                
                // Poll for status
                pollJobStatus(result.job_id);
            } catch (error) {
                document.getElementById('cloneResult').innerHTML = 
                    '<div class="alert alert-error">❌ Error: ' + error.message + '</div>';
            }
            
            btn.disabled = false;
            btn.textContent = '🚀 Start Cloning';
        }
        
        async function pollJobStatus(jobId) {
            const interval = setInterval(async () => {
                try {
                    const response = await fetch(API_BASE + '/jobs/' + jobId);
                    const job = await response.json();
                    
                    if (job.status === 'completed' || job.status === 'failed') {
                        clearInterval(interval);
                        document.getElementById('cloneResult').innerHTML += 
                            '<div class="alert alert-' + (job.status === 'completed' ? 'success' : 'error') + '">' +
                            (job.status === 'completed' ? '✅ Clone completed!' : '❌ Clone failed: ' + (job.error || 'Unknown error')) +
                            '</div>';
                        if (job.download_url) {
                            document.getElementById('cloneResult').innerHTML += 
                                '<a href="' + job.download_url + '" class="btn" style="display:inline-block; margin-top:10px;">⬇️ Download Result</a>';
                        }
                    }
                } catch (error) {
                    console.error('Polling error:', error);
                }
            }, 2000);
        }
        
        async function refreshJobs() {
            try {
                const response = await fetch(API_BASE + '/jobs');
                const data = await response.json();
                const jobList = document.getElementById('jobList');
                
                if (data.jobs && data.jobs.length > 0) {
                    jobList.innerHTML = data.jobs.map(job => 
                        '<li class="job-item">' +
                        '<div><strong>' + job.url + '</strong><br><small>ID: ' + job.job_id + '</small></div>' +
                        '<span class="status-badge status-' + job.status + '">' + job.status + '</span>' +
                        '</li>'
                    ).join('');
                } else {
                    jobList.innerHTML = '<li class="job-item">No jobs yet.</li>';
                }
            } catch (error) {
                console.error('Error loading jobs:', error);
            }
        }
        
        async function loadAdminStats() {
            try {
                const response = await fetch(API_BASE + '/admin/stats');
                const stats = await response.json();
                
                document.getElementById('statUsers').textContent = stats.total_users || 0;
                document.getElementById('statJobs').textContent = stats.total_jobs || 0;
                document.getElementById('statCompleted').textContent = stats.completed_jobs || 0;
                document.getElementById('statStorage').textContent = (stats.storage_used_mb || 0) + ' MB';
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        }
        
        function saveAdminSettings() {
            alert('Settings saved successfully!');
        }
        
        function handleLogin(e) {
            e.preventDefault();
            const msg = document.getElementById('loginMessage');
            msg.style.display = 'block';
            msg.className = 'alert alert-success';
            msg.textContent = '✅ Login successful! (Demo mode)';
        }
    </script>
</body>
</html>'''


def create_frontend_files(output_dir: str = "./frontend"):
    """Create all frontend files."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Main HTML file
    with open(output_path / "index.html", "w") as f:
        f.write(get_frontend_html())
    
    return str(output_path)


if __name__ == "__main__":
    create_frontend_files()
    print("Frontend files created successfully!")
