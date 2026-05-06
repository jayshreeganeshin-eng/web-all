"""
Report generation utilities for web-all.
Generates detailed reports about cloned websites.
"""

import json
import csv
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class ReportGenerator:
    """Generate various reports about cloned websites."""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.report_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "source_directory": str(output_dir),
            },
            "statistics": {},
            "files": [],
            "errors": [],
        }
    
    def scan_directory(self) -> Dict:
        """Scan the output directory and collect statistics."""
        if not self.output_dir.exists():
            raise FileNotFoundError(f"Output directory {self.output_dir} does not exist")
        
        total_files = 0
        total_size = 0
        file_types = {}
        files_list = []
        
        for file_path in self.output_dir.rglob('*'):
            if file_path.is_file():
                total_files += 1
                file_size = file_path.stat().st_size
                total_size += file_size
                
                # Get file extension
                ext = file_path.suffix.lower() or 'no_extension'
                file_types[ext] = file_types.get(ext, 0) + 1
                
                # Add to files list
                rel_path = file_path.relative_to(self.output_dir)
                files_list.append({
                    "path": str(rel_path),
                    "size": file_size,
                    "type": ext,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                })
        
        self.report_data["statistics"] = {
            "total_files": total_files,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "file_types": file_types,
        }
        self.report_data["files"] = files_list
        
        return self.report_data
    
    def generate_json_report(self, output_path: Optional[str] = None) -> str:
        """Generate a JSON report."""
        if not self.report_data.get("statistics"):
            self.scan_directory()
        
        if output_path is None:
            output_path = str(self.output_dir / "report.json")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.report_data, f, indent=2)
        
        return output_path
    
    def generate_csv_report(self, output_path: Optional[str] = None) -> str:
        """Generate a CSV report of all files."""
        if not self.report_data.get("files"):
            self.scan_directory()
        
        if output_path is None:
            output_path = str(self.output_dir / "report.csv")
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Path", "Size (bytes)", "Type", "Last Modified"])
            
            for file_info in self.report_data["files"]:
                writer.writerow([
                    file_info["path"],
                    file_info["size"],
                    file_info["type"],
                    file_info["modified"],
                ])
        
        return output_path
    
    def generate_html_report(self, output_path: Optional[str] = None) -> str:
        """Generate an HTML report with statistics."""
        if not self.report_data.get("statistics"):
            self.scan_directory()
        
        if output_path is None:
            output_path = str(self.output_dir / "report.html")
        
        stats = self.report_data["statistics"]
        file_types_html = ""
        for ext, count in sorted(stats.get("file_types", {}).items(), key=lambda x: x[1], reverse=True):
            file_types_html += f"<tr><td>{ext}</td><td>{count}</td></tr>\n"
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>web-all Clone Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
            background: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{ color: #667eea; }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 2rem 0;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 2rem;
            font-weight: bold;
        }}
        .stat-label {{
            font-size: 0.875rem;
            opacity: 0.9;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 2rem;
        }}
        th, td {{
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }}
        th {{
            background: #f5f5f5;
            font-weight: 600;
        }}
        tr:hover {{
            background: #f9f9f9;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🕷️ web-all Clone Report</h1>
        <p>Generated: {self.report_data["metadata"]["generated_at"]}</p>
        <p>Source: {self.report_data["metadata"]["source_directory"]}</p>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{stats.get('total_files', 0)}</div>
                <div class="stat-label">Total Files</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats.get('total_size_mb', 0)} MB</div>
                <div class="stat-label">Total Size</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len(stats.get('file_types', {}))}</div>
                <div class="stat-label">File Types</div>
            </div>
        </div>
        
        <h2>File Types Distribution</h2>
        <table>
            <thead>
                <tr>
                    <th>Extension</th>
                    <th>Count</th>
                </tr>
            </thead>
            <tbody>
                {file_types_html}
            </tbody>
        </table>
        
        <h2>All Files ({len(self.report_data.get('files', []))})</h2>
        <table>
            <thead>
                <tr>
                    <th>Path</th>
                    <th>Size</th>
                    <th>Type</th>
                </tr>
            </thead>
            <tbody>
                {''.join([f"<tr><td>{f['path']}</td><td>{f['size']} bytes</td><td>{f['type']}</td></tr>" for f in self.report_data.get('files', [])[:100]])}
            </tbody>
        </table>
        {f'<p style="text-align: center; color: #666; margin-top: 1rem;">Showing first 100 of {len(self.report_data.get("files", []))} files</p>' if len(self.report_data.get('files', [])) > 100 else ''}
    </div>
</body>
</html>
"""
        
        Path(output_path).write_text(html_content, encoding='utf-8')
        return output_path
    
    def generate_all_reports(self, output_dir: Optional[str] = None) -> Dict[str, str]:
        """Generate all report formats."""
        if output_dir is None:
            output_dir = str(self.output_dir)
        
        return {
            "json": self.generate_json_report(str(Path(output_dir) / "report.json")),
            "csv": self.generate_csv_report(str(Path(output_dir) / "report.csv")),
            "html": self.generate_html_report(str(Path(output_dir) / "report.html")),
        }


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        generator = ReportGenerator(sys.argv[1])
        reports = generator.generate_all_reports()
        print("Generated reports:")
        for format, path in reports.items():
            print(f"  {format}: {path}")
    else:
        print("Usage: python report_generator.py <output_directory>")
