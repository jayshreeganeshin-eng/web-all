"""
CLI entry point for web-all.
Provides command-line interface for all download modes.
"""

import argparse
import asyncio
import sys
from pathlib import Path
from .cloner import WebsiteCloner
from .invisible import InvisibleContentHandler


def main():
    parser = argparse.ArgumentParser(
        prog='web-all',
        description='Universal Website Cloner & Crawler - Download visible and invisible content'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Clone command
    clone_parser = subparsers.add_parser('clone', help='Full website clone with assets')
    clone_parser.add_argument('url', help='Target website URL')
    clone_parser.add_argument('--output', '-o', default='./output', help='Output directory')
    clone_parser.add_argument('--depth', '-d', type=int, default=5, help='Crawl depth')
    clone_parser.add_argument('--concurrency', '-c', type=int, default=5, help='Concurrent requests')
    clone_parser.add_argument('--delay', type=float, default=1.0, help='Delay between requests')
    clone_parser.add_argument('--discover-invisible', action='store_true', help='Discover hidden content')
    clone_parser.add_argument('--headless', action='store_true', default=True, help='Run browser headless')
    
    # Scroll command
    scroll_parser = subparsers.add_parser('scroll', help='Single page with infinite scroll')
    scroll_parser.add_argument('url', help='Target website URL')
    scroll_parser.add_argument('--output', '-o', default='./output', help='Output directory')
    scroll_parser.add_argument('--iterations', type=int, default=5, help='Scroll iterations')
    scroll_parser.add_argument('--headless', action='store_true', default=True, help='Run browser headless')
    
    # Images command
    images_parser = subparsers.add_parser('images-only', help='Download all images')
    images_parser.add_argument('url', help='Target website URL')
    images_parser.add_argument('--output', '-o', default='./output/images', help='Output directory')
    images_parser.add_argument('--discover-invisible', action='store_true', help='Discover hidden content')
    images_parser.add_argument('--depth', '-d', type=int, default=3, help='Crawl depth')
    
    # Text command
    text_parser = subparsers.add_parser('text-only', help='Extract text from pages')
    text_parser.add_argument('url', help='Target website URL')
    text_parser.add_argument('--output', '-o', default='./output/text', help='Output directory')
    text_parser.add_argument('--depth', '-d', type=int, default=3, help='Crawl depth')
    
    # Video command
    video_parser = subparsers.add_parser('videos-only', help='Download all videos')
    video_parser.add_argument('url', help='Target website URL')
    video_parser.add_argument('--output', '-o', default='./output/videos', help='Output directory')
    
    # Mobile command
    mobile_parser = subparsers.add_parser('mobile-capture', help='Capture page as mobile device')
    mobile_parser.add_argument('url', help='Target website URL')
    mobile_parser.add_argument('--output', '-o', default='./output/mobile.html', help='Output file')
    mobile_parser.add_argument('--device', choices=['iphone12', 'pixel5', 'ipad'], default='iphone12', help='Device to emulate')
    
    # Auth command
    auth_parser = subparsers.add_parser('login', help='Interactive login and save cookies')
    auth_parser.add_argument('url', help='Login page URL')
    auth_parser.add_argument('--cookies', '-c', default='cookies.json', help='Cookie output file')
    
    # Archive command
    archive_parser = subparsers.add_parser('archive', help='Create ZIP archive of output')
    archive_parser.add_argument('input_dir', help='Directory to archive')
    archive_parser.add_argument('--output', '-o', help='Output ZIP file path')
    archive_parser.add_argument('--report', action='store_true', help='Generate analytics report')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate analytics report for cloned site')
    report_parser.add_argument('input_dir', help='Directory with cloned site')
    report_parser.add_argument('--output', '-o', help='Output report file (JSON)')
    
    # Upload command
    upload_parser = subparsers.add_parser('upload', help='Upload to FTP server')
    upload_parser.add_argument('local_dir', help='Local directory to upload')
    upload_parser.add_argument('--host', required=True, help='FTP host')
    upload_parser.add_argument('--user', required=True, help='FTP username')
    upload_parser.add_argument('--password', required=True, help='FTP password')
    upload_parser.add_argument('--remote', default='/', help='Remote directory')
    
    # Download all files command
    download_parser = subparsers.add_parser('download-all', help='Download all file types from website')
    download_parser.add_argument('url', help='Target website URL')
    download_parser.add_argument('--output', '-o', default='./downloads', help='Output directory')
    download_parser.add_argument('--depth', '-d', type=int, default=3, help='Crawl depth')
    download_parser.add_argument('--types', '-t', nargs='+', help='Specific file types (pdf, zip, jpg, etc.)')
    download_parser.add_argument('--max-size', type=int, default=100, help='Max file size in MB')
    download_parser.add_argument('--no-organize', action='store_true', help='Don\'t organize by type')
    
    # Archive.org download command
    archive_dl_parser = subparsers.add_parser('archive-download', help='Download from Internet Archive')
    archive_dl_parser.add_argument('--query', '-q', required=True, help='Search query')
    archive_dl_parser.add_argument('--output', '-o', default='./archive_downloads', help='Output directory')
    archive_dl_parser.add_argument('--limit', type=int, default=50, help='Max items to download')
    archive_dl_parser.add_argument('--types', '-t', nargs='+', help='File types to download')
    
    # Deep crawl command
    deep_parser = subparsers.add_parser('deep-crawl', help='Deep crawl with sitemap and path guessing')
    deep_parser.add_argument('url', help='Target website URL')
    deep_parser.add_argument('--output', '-o', default='./output', help='Output directory')
    deep_parser.add_argument('--sitemap', action='store_true', help='Use sitemap.xml')
    deep_parser.add_argument('--path-guess', action='store_true', help='Guess common paths')
    
    # Serve command (GUI)
    serve_parser = subparsers.add_parser('serve', help='Start web GUI server')
    serve_parser.add_argument('--port', '-p', type=int, default=8000, help='Server port')
    serve_parser.add_argument('--host', default='0.0.0.0', help='Server host')
    
    args = parser.parse_args()
    
    if args.command == 'clone':
        print(f"Cloning {args.url}...")
        cloner = WebsiteCloner(
            base_url=args.url,
            output_dir=args.output,
            depth=args.depth,
            concurrency=args.concurrency,
            delay=args.delay,
        )
        asyncio.run(cloner.clone_site())
        
    elif args.command == 'scroll':
        print(f"Scrolling {args.url}...")
        handler = InvisibleContentHandler(args.url, headless=args.headless)
        output_file = Path(args.output) / 'scrolled_page.html'
        output_file.parent.mkdir(parents=True, exist_ok=True)
        html = asyncio.run(handler.expand_hidden_elements(args.url, output_file))
        print(f"Saved to {output_file}")
        
    elif args.command == 'images-only':
        print(f"Downloading images from {args.url}...")
        # Simple image downloader - will be enhanced
        handler = InvisibleContentHandler(args.url, headless=True)
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        async def extract_images():
            html = await handler.expand_hidden_elements(args.url)
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'lxml')
            imgs = soup.find_all('img', src=True)
            print(f"Found {len(imgs)} images")
            
            import aiohttp
            async with aiohttp.ClientSession() as session:
                for i, img in enumerate(imgs):
                    src = img['src']
                    if src.startswith(('http://', 'https://')):
                        try:
                            async with session.get(src) as resp:
                                if resp.status == 200:
                                    img_name = src.split('/')[-1].split('?')[0] or f'image_{i}.jpg'
                                    img_path = output_dir / img_name
                                    img_path.write_bytes(await resp.read())
                                    print(f"  Downloaded: {img_name}")
                        except Exception as e:
                            print(f"  Failed: {src} - {e}")
        
        asyncio.run(extract_images())
        print(f"Images saved to {output_dir}")
        
    elif args.command == 'text-only':
        print(f"Extracting text from {args.url}...")
        handler = InvisibleContentHandler(args.url, headless=True)
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        async def extract_text():
            html = await handler.expand_hidden_elements(args.url)
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'lxml')
            
            # Remove script and style elements
            for tag in soup(['script', 'style']):
                tag.decompose()
                
            text = soup.get_text(separator='\n', strip=True)
            
            # Save text
            url_parsed = urlparse(args.url)
            text_file = output_dir / f"{url_parsed.netloc.replace('.', '_')}.txt"
            text_file.write_text(text, encoding='utf-8')
            print(f"Text saved to {text_file}")
            print(f"Extracted {len(text)} characters")
        
        from urllib.parse import urlparse
        asyncio.run(extract_text())
        
    elif args.command == 'videos-only':
        print(f"Downloading videos from {args.url}...")
        from .advanced import VideoDownloader
        
        output_dir = Path(args.output)
        downloader = VideoDownloader(str(output_dir))
        
        # For now, just download from the main URL
        # In future, crawl page to find all video URLs
        asyncio.run(downloader.download_videos([args.url]))
        print(f"Videos saved to {output_dir}")
        
    elif args.command == 'mobile-capture':
        print(f"Capturing {args.url} as {args.device}...")
        from .advanced import MobileEmulator
        
        emulator = MobileEmulator()
        output_file = Path(args.output)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        html = asyncio.run(emulator.capture_with_device(args.url, args.device, output_file))
        print(f"Mobile capture saved to {output_file} ({len(html)} bytes)")
        
    elif args.command == 'login':
        print(f"Interactive login for {args.url}...")
        from .advanced import AuthManager
        
        auth = AuthManager()
        cookies = asyncio.run(auth.interactive_login(args.url, args.cookies))
        print(f"Saved {len(cookies)} cookies")
        
    elif args.command == 'archive':
        print(f"Creating archive of {args.input_dir}...")
        from .advanced import ArchiveManager
        
        output_zip = args.output or f"{args.input_dir}.zip"
        zip_path = ArchiveManager.create_zip(args.input_dir, output_zip)
        print(f"Archive created: {zip_path}")
        
        # Generate report if requested
        if args.report:
            print("\nGenerating analytics report...")
            from .analytics import AnalyticsEngine
            analytics = AnalyticsEngine(args.input_dir)
            report = analytics.analyze_site(args.input_dir)
            report_file = analytics.save_report(report, args.output.replace('.zip', '_report.json') if args.output else None)
            analytics.print_summary(report)
            print(f"Report saved to: {report_file}")
        
    elif args.command == 'report':
        print(f"Generating report for {args.input_dir}...")
        from .analytics import AnalyticsEngine
        
        analytics = AnalyticsEngine(args.input_dir)
        report = analytics.analyze_site(args.input_dir)
        report_file = analytics.save_report(report, args.output)
        analytics.print_summary(report)
        print(f"Report saved to: {report_file}")
        
    elif args.command == 'upload':
        print(f"Uploading {args.local_dir} to {args.host}...")
        from .advanced import FTPUploader
        
        uploader = FTPUploader(args.host, args.user, args.password)
        asyncio.run(uploader.upload_directory(args.local_dir, args.remote))
        print("Upload complete!")
        
    elif args.command == 'download-all':
        print(f"Downloading all files from {args.url}...")
        from .universal_downloader import UniversalFileDownloader
        
        downloader = UniversalFileDownloader(
            base_url=args.url,
            output_dir=args.output,
            depth=args.depth,
            concurrency=10,
            file_types=args.types,
            max_file_size=args.max_size * 1024 * 1024,
            organize_by_type=not args.no_organize,
        )
        asyncio.run(downloader.crawl_and_download())
        
    elif args.command == 'archive-download':
        print(f"Searching and downloading from Internet Archive: {args.query}")
        from .universal_downloader import InternetArchiveDownloader
        
        downloader = InternetArchiveDownloader(args.output)
        downloaded = asyncio.run(downloader.search_and_download(
            query=args.query,
            limit=args.limit,
            file_types=args.types,
        ))
        print(f"Downloaded {len(downloaded)} files from Internet Archive")
        
    elif args.command == 'deep-crawl':
        print(f"Deep crawling {args.url}...")
        handler = InvisibleContentHandler(args.url)
        urls = asyncio.run(handler.discover_all())
        print(f"Discovered {len(urls)} URLs")
        
    elif args.command == 'serve':
        print("Starting web GUI...")
        try:
            from .api import start_server
            start_server(host=args.host, port=args.port)
        except ImportError:
            print("FastAPI not installed. Run: pip install fastapi uvicorn")
            sys.exit(1)
            
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
