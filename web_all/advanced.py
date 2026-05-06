"""
Advanced features for web-all.
Includes: video downloads, ZIP packaging, FTP upload, mobile emulation, authentication.
"""

import asyncio
import zipfile
import ftplib
from pathlib import Path
from typing import Optional, List, Dict
from urllib.parse import urlparse
from playwright.async_api import async_playwright


class VideoDownloader:
    """Download videos from websites using yt-dlp."""

    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)

    async def download_videos(self, urls: List[str], progress_callback=None):
        """Download videos from a list of URLs."""
        try:
            import yt_dlp
        except ImportError:
            print("yt-dlp not installed. Install with: pip install yt-dlp")
            return []

        self.output_dir.mkdir(parents=True, exist_ok=True)
        downloaded = []

        ydl_opts = {
            'outtmpl': str(self.output_dir / '%(title)s.%(ext)s'),
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            for url in urls:
                try:
                    if progress_callback:
                        progress_callback(f"Downloading video: {url}")
                    info = ydl.extract_info(url, download=True)
                    downloaded.append({
                        'url': url,
                        'title': info.get('title', 'Unknown'),
                        'path': str(self.output_dir / f"{info.get('title', 'unknown')}.{info.get('ext', 'mp4')}")
                    })
                except Exception as e:
                    print(f"Failed to download {url}: {e}")

        return downloaded


class ArchiveManager:
    """Create and manage ZIP archives of cloned sites."""

    @staticmethod
    def create_zip(source_dir: str, output_path: Optional[str] = None) -> str:
        """Create a ZIP archive of the source directory."""
        source = Path(source_dir)
        if not source.exists():
            raise FileNotFoundError(f"Source directory {source} does not exist")

        if output_path is None:
            output_path = f"{source_dir}.zip"

        output_file = Path(output_path)

        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in source.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(source)
                    zipf.write(file_path, arcname)

        return str(output_file)

    @staticmethod
    def extract_zip(zip_path: str, dest_dir: str) -> str:
        """Extract a ZIP archive to destination directory."""
        dest = Path(dest_dir)
        dest.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zipf.extractall(dest)

        return str(dest)


class FTPUploader:
    """Upload cloned sites to FTP servers (e.g., InfinityFree)."""

    def __init__(self, host: str, username: str, password: str, port: int = 21):
        self.host = host
        self.username = username
        self.password = password
        self.port = port

    async def upload_directory(self, local_dir: str, remote_dir: str = '/', progress_callback=None):
        """Upload entire directory to FTP server."""
        local = Path(local_dir)

        if not local.exists():
            raise FileNotFoundError(f"Local directory {local} does not exist")

        loop = asyncio.get_event_loop()

        def _upload():
            ftp = ftplib.FTP()
            ftp.connect(self.host, self.port)
            ftp.login(self.username, self.password)

            try:
                self._upload_recursive(ftp, local, remote_dir, progress_callback)
            finally:
                ftp.quit()

        await loop.run_in_executor(None, _upload)

    def _upload_recursive(self, ftp: ftplib.FTP, local_path: Path, remote_path: str, progress_callback=None):
        """Recursively upload files and directories."""
        if local_path.is_file():
            if progress_callback:
                progress_callback(f"Uploading: {local_path.name}")

            with open(local_path, 'rb') as f:
                ftp.storbinary(f'STOR {remote_path}/{local_path.name}', f)

        elif local_path.is_dir():
            # Create remote directory if needed
            dir_name = local_path.name
            try:
                ftp.mkd(f"{remote_path}/{dir_name}")
            except ftplib.error_perm:
                pass  # Directory already exists

            # Upload contents
            for item in local_path.iterdir():
                self._upload_recursive(
                    ftp,
                    item,
                    f"{remote_path}/{dir_name}",
                    progress_callback
                )


class MobileEmulator:
    """Emulate mobile devices for testing mobile-specific content."""

    MOBILE_DEVICES = {
        'iphone12': {
            'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
            'viewport': {'width': 390, 'height': 844},
            'device_scale_factor': 3,
            'is_mobile': True,
        },
        'pixel5': {
            'user_agent': 'Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.91 Mobile Safari/537.36',
            'viewport': {'width': 393, 'height': 851},
            'device_scale_factor': 2.75,
            'is_mobile': True,
        },
        'ipad': {
            'user_agent': 'Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
            'viewport': {'width': 820, 'height': 1180},
            'device_scale_factor': 2,
            'is_mobile': True,
        },
    }

    async def capture_with_device(self, url: str, device: str = 'iphone12', output_path: Optional[Path] = None) -> str:
        """Capture page content emulating a specific mobile device."""
        if device not in self.MOBILE_DEVICES:
            raise ValueError(f"Unknown device: {device}. Available: {list(self.MOBILE_DEVICES.keys())}")

        config = self.MOBILE_DEVICES[device]

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)

            context = await browser.new_context(
                user_agent=config['user_agent'],
                viewport=config['viewport'],
                device_scale_factor=config['device_scale_factor'],
                is_mobile=config['is_mobile'],
            )

            page = await context.new_page()
            await page.goto(url, wait_until='networkidle')

            # Scroll to load lazy content
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(1000)

            html = await page.content()

            if output_path:
                output_path.write_text(html, encoding='utf-8')

            await context.close()
            await browser.close()

            return html


class AuthManager:
    """Handle authentication for protected websites."""

    def __init__(self):
        self.cookies: List[Dict] = []
        self.headers: Dict[str, str] = {}

    async def interactive_login(self, url: str, save_cookies: Optional[str] = None) -> List[Dict]:
        """Launch browser for manual login, then save cookies."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)  # Visible for interaction
            context = await browser.new_context()
            page = await context.new_page()

            print(f"Please log in at: {url}")
            await page.goto(url)

            # Wait for user to complete login (press Enter in terminal when done)
            input("Press Enter after you've logged in...")

            # Save cookies
            self.cookies = await context.cookies()

            if save_cookies:
                import json as json_lib
                Path(save_cookies).write_text(json_lib.dumps(self.cookies), encoding='utf-8')
                print(f"Cookies saved to: {save_cookies}")

            await browser.close()

            return self.cookies

    def load_cookies(self, cookie_file: str) -> List[Dict]:
        """Load cookies from file."""
        import json as json_lib
        self.cookies = json_lib.loads(Path(cookie_file).read_text(encoding='utf-8'))
        return self.cookies

    def set_basic_auth(self, username: str, password: str):
        """Set basic authentication headers."""
        import base64 as base64_lib
        credentials = f"{username}:{password}"
        encoded = base64_lib.b64encode(credentials.encode()).decode()
        self.headers['Authorization'] = f"Basic {encoded}"

    def get_headers(self) -> Dict[str, str]:
        """Get all authentication headers."""
        return self.headers.copy()

    def get_cookies(self) -> List[Dict]:
        """Get all cookies."""
        return self.cookies.copy()


async def test_advanced_features():
    """Test all advanced features."""
    print("Testing Advanced Features...")

    # Test ZIP creation
    print("\n1. Testing ZIP Archive...")
    if Path('./test_output').exists():
        zip_path = ArchiveManager.create_zip('./test_output', './test_archive.zip')
        print(f"✓ Created ZIP: {zip_path}")

    # Test mobile emulation
    print("\n2. Testing Mobile Emulation...")
    emulator = MobileEmulator()
    try:
        html = await emulator.capture_with_device('https://example.com', 'iphone12')
        print(f"✓ Mobile capture successful ({len(html)} bytes)")
    except Exception as e:
        print(f"✗ Mobile emulation failed: {e}")

    print("\n✅ Advanced features test complete!")


if __name__ == '__main__':
    asyncio.run(test_advanced_features())
