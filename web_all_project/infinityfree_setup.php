<?php
/**
 * web-all InfinityFree Setup Script
 * This file helps verify your InfinityFree setup
 * Note: web-all is a Python tool that runs locally.
 * Upload CLONED website files to InfinityFree, not this tool.
 */

// Check PHP version
$phpVersion = phpversion();
$phpOk = version_compare($phpVersion, '7.0', '>=');

// Check if we're in htdocs
$isInHtdocs = strpos(__DIR__, 'htdocs') !== false || 
              strpos($_SERVER['DOCUMENT_ROOT'], 'htdocs') !== false;

// Get directory info
$diskSpace = disk_free_space(__DIR__);
$diskSpaceFormatted = round($diskSpace / 1024 / 1024, 2) . ' MB';

?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>web-all - InfinityFree Setup Check</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 600px;
            width: 100%;
            padding: 40px;
        }
        h1 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 2em;
        }
        .subtitle {
            color: #666;
            margin-bottom: 30px;
        }
        .check-item {
            display: flex;
            align-items: center;
            padding: 15px;
            margin: 10px 0;
            background: #f8f9fa;
            border-radius: 8px;
        }
        .check-icon {
            font-size: 1.5em;
            margin-right: 15px;
        }
        .check-text {
            flex: 1;
        }
        .check-label {
            font-weight: 600;
            color: #333;
        }
        .check-detail {
            color: #666;
            font-size: 0.9em;
        }
        .success { color: #28a745; }
        .warning { color: #ffc107; }
        .error { color: #dc3545; }
        .info-box {
            background: #e7f3ff;
            border-left: 4px solid #2196F3;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }
        .info-box h3 {
            color: #1976D2;
            margin-bottom: 10px;
        }
        .info-box p {
            color: #555;
            line-height: 1.6;
        }
        .btn {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 30px;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            margin-top: 20px;
            transition: transform 0.2s;
        }
        .btn:hover {
            transform: translateY(-2px);
        }
        .steps {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }
        .steps h3 {
            color: #856404;
            margin-bottom: 10px;
        }
        .steps ol {
            margin-left: 20px;
            color: #856404;
            line-height: 1.8;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌐 web-all</h1>
        <p class="subtitle">InfinityFree Setup Verification</p>
        
        <div class="info-box">
            <h3>ℹ️ Important Information</h3>
            <p>
                <strong>web-all</strong> is a Python-based website cloning tool that runs on your 
                <strong>local computer</strong>. You use it to download websites, then upload the 
                <strong>cloned files</strong> to InfinityFree for hosting.
            </p>
        </div>
        
        <h2 style="margin: 20px 0 10px;">Server Status</h2>
        
        <div class="check-item">
            <span class="check-icon"><?php echo $phpOk ? '✅' : '❌'; ?></span>
            <div class="check-text">
                <div class="check-label">PHP Version</div>
                <div class="check-detail"><?php echo $phpVersion; ?> <?php echo $phpOk ? '(Compatible)' : '(Upgrade required)'; ?></div>
            </div>
        </div>
        
        <div class="check-item">
            <span class="check-icon"><?php echo $isInHtdocs ? '✅' : '⚠️'; ?></span>
            <div class="check-text">
                <div class="check-label">Directory Location</div>
                <div class="check-detail"><?php echo $isInHtdocs ? 'Correctly installed in htdocs' : 'Should be in /htdocs/ folder'; ?></div>
            </div>
        </div>
        
        <div class="check-item">
            <span class="check-icon">💾</span>
            <div class="check-text">
                <div class="check-label">Available Disk Space</div>
                <div class="check-detail"><?php echo $diskSpace_formatted; ?></div>
            </div>
        </div>
        
        <div class="check-item">
            <span class="check-icon">📁</span>
            <div class="check-text">
                <div class="check-label">Current Directory</div>
                <div class="check-detail"><?php echo __DIR__; ?></div>
            </div>
        </div>
        
        <div class="steps">
            <h3>📋 How to Use web-all with InfinityFree</h3>
            <ol>
                <li><strong>Install web-all locally</strong> on your computer (requires Python 3.10+)</li>
                <li><strong>Clone a website</strong> using: <code>web-all clone https://example.com -o ./mysite</code></li>
                <li><strong>Upload cloned files</strong> from <code>./mysite</code> to your InfinityFree <code>/htdocs/</code> folder via FTP</li>
                <li><strong>Visit your domain</strong> to see the cloned website</li>
            </ol>
        </div>
        
        <div class="info-box">
            <h3>🔗 Quick Links</h3>
            <p>
                📖 <a href="https://github.com/web-all/web-all" target="_blank" style="color: #1976D2;">Documentation</a><br>
                📥 <a href="INSTALLATION_GUIDE.md" target="_blank" style="color: #1976D2;">Installation Guide</a><br>
                🚀 <a href="https://infinityfree.net" target="_blank" style="color: #1976D2;">InfinityFree Website</a>
            </p>
        </div>
        
        <center>
            <p style="margin-top: 20px; color: #666; font-size: 0.9em;">
                Need help? Check the INSTALLATION_GUIDE.md file for detailed instructions.
            </p>
        </center>
    </div>
</body>
</html>
