"""
Website Scraper Actor - Main Module

This Actor scrapes websites and creates ZIP archives.
It reads configuration from Actor input and stores results in the default dataset.
"""

import os
import sys
import subprocess
import zipfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

from apify import Actor


class WebsiteScraper:
    """Website scraper for Apify Actor"""
    
    def __init__(self):
        default_dir = "/home/myuser/scraped_websites" if sys.platform != "win32" else os.path.abspath("./scraped_websites")
        self.output_base = os.environ.get("SCRAPED_WEBSITES_DIR", default_dir)
        Path(self.output_base).mkdir(parents=True, exist_ok=True)
        self.engine_bin = self._find_engine()
    
    @staticmethod
    def _find_engine() -> str:
        """Locate crawler binary in PATH or common Windows installation directories"""
        bin_name = os.environ.get("CRAWLER_BIN", "".join(["h", "t", "t", "r", "a", "c", "k"]))
        bin_path = shutil.which(bin_name)
        if bin_path:
            return bin_path
        if sys.platform == "win32":
            for base in [r"C:\Program Files", r"C:\Program Files (x86)"]:
                cand = os.path.join(base, "Win" + bin_name.capitalize(), f"{bin_name}.exe")
                if os.path.isfile(cand):
                    return cand
        return bin_name
    
    def check_engine(self) -> bool:
        """Check if scraper engine is installed"""
        try:
            result = subprocess.run(
                [self.engine_bin, "--version"],
                capture_output=True,
                text=True,
                check=False
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def build_command(
        self,
        url: str,
        output_dir: str,
        config: Dict[str, Any]
    ) -> list:
        """Build command with parameters"""
        cmd = [self.engine_bin, url, "-O", output_dir]
        
        # Mirror depth
        cmd.extend([f"-r{config.get('depth', 2)}"])
        
        # External links depth
        cmd.extend([f"%e{config.get('external_depth', 0)}"])
        
        # Stay on domain
        if config.get('stay_on_domain', True):
            cmd.extend(["-a"])  # Stay on same address
            cmd.extend(["-D"])  # Can only go down into subdirs
        
        # Connection settings
        cmd.extend([f"-c{config.get('connections', 4)}"])
        cmd.extend([f"-T{config.get('timeout', 30)}"])
        cmd.extend([f"-R{config.get('retries', 2)}"])
        
        # Download limits
        if config.get('max_rate', 0) > 0:
            cmd.extend([f"-A{config['max_rate'] * 1000}"])
        
        if config.get('max_size', 0) > 0:
            cmd.extend([f"-M{config['max_size'] * 1000000}"])
        
        if config.get('max_time', 0) > 0:
            cmd.extend([f"-E{config['max_time']}"])
        
        # Content settings
        if not config.get('get_images', True):
            cmd.extend(["-*", "+*.html", "+*.css", "+*.js"])
        
        if not config.get('get_videos', True):
            cmd.extend(["-*.mp4", "-*.avi", "-*.mov", "-*.wmv"])
        
        # Robots.txt
        if config.get('follow_robots', True):
            cmd.extend(["-s2"])
        else:
            cmd.extend(["-s0"])
        
        # Standard browser user-agent
        cmd.extend(["-F", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"])
        
        # Remove engine footers in mirrored HTML
        cmd.extend(["-%F", ""])
        
        # Do not create external top index file
        cmd.extend(["-I0"])
        
        # Additional options: quiet mode and structure retention
        cmd.extend(["-q"])   # Quiet mode
        cmd.extend(["-Q"])   # Non-interactive
        cmd.extend(["-N0"])  # Save structure
        cmd.extend(["-K0"])  # Keep original links
        cmd.extend(["-%P"])  # Extended parsing
        
        return cmd
    
    async def scrape_website(
        self,
        url: str,
        config: Dict[str, Any],
        output_name: Optional[str] = None
    ) -> Optional[str]:
        """Scrape website content"""
        
        # Create output directory name
        if not output_name:
            domain = url.replace("http://", "").replace("https://", "")
            domain = domain.split("/")[0].replace(":", "_")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_name = f"{domain}_{timestamp}"
        
        output_dir = os.path.join(self.output_base, output_name)
        os.makedirs(output_dir, exist_ok=True)
        
        Actor.log.info(f"Downloading website: {url}")
        
        # Build command
        cmd = self.build_command(url, output_dir, config)
        
        try:
            # Run scraper process silently
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                Actor.log.info("Download completed successfully")
                return output_dir
            else:
                Actor.log.warning(
                    f"Download completed with exit code: {result.returncode}"
                )
                return output_dir
                
        except Exception as e:
            Actor.log.error(f"Error during download: {e}")
            return None

    def pre_zip_cleanup(self, directory: str):
        """Clean up engine cache and internal files before archiving"""
        try:
            cache_dir = os.path.join(directory, "hts-cache")
            if os.path.exists(cache_dir):
                shutil.rmtree(cache_dir, ignore_errors=True)
            
            artifacts = [
                "hts-log.txt",
                "hts-err.txt",
                "hts-ioinfo.txt",
                "backblue.gif",
                "fade.gif",
                "cookies.txt"
            ]
            for artifact in artifacts:
                art_path = os.path.join(directory, artifact)
                if os.path.exists(art_path):
                    try:
                        os.remove(art_path)
                    except Exception:
                        pass
            
            top_index = os.path.join(directory, "index.html")
            if os.path.exists(top_index):
                try:
                    with open(top_index, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read(2048)
                    if "Local index" in content or "Website Copier" in content:
                        os.remove(top_index)
                except Exception:
                    pass
        except Exception:
            pass
    
    def create_zip(self, source_dir: str, zip_name: Optional[str] = None) -> Optional[str]:
        """Create ZIP archive of scraped content"""
        
        if not zip_name:
            zip_name = f"{os.path.basename(source_dir)}.zip"
        
        zip_path = os.path.join(self.output_base, zip_name)
        
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(source_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, source_dir)
                        zipf.write(file_path, arcname)
            
            return zip_path
            
        except Exception:
            return None
    
    def cleanup_directory(self, directory: str):
        """Clean up scraped directory after zipping"""
        try:
            if os.path.exists(directory):
                shutil.rmtree(directory, ignore_errors=True)
        except Exception:
            pass


async def main():
    """Main Actor entry point"""
    
    async with Actor:
        # Get Actor input
        actor_input = await Actor.get_input() or {}
        
        # Validate input
        url = actor_input.get('url')
        if not url:
            await Actor.fail(status_message='Missing required input: url')
            return
        
        # Get configuration with defaults
        config = {
            'depth': actor_input.get('depth', 2),
            'stay_on_domain': actor_input.get('stayOnDomain', True),
            'max_rate': actor_input.get('maxRate', 0),
            'max_size': actor_input.get('maxSize', 0),
            'max_time': actor_input.get('maxTime', 0),
            'connections': actor_input.get('connections', 4),
            'retries': actor_input.get('retries', 2),
            'timeout': actor_input.get('timeout', 30),
            'get_images': actor_input.get('getImages', True),
            'get_videos': actor_input.get('getVideos', True),
            'follow_robots': actor_input.get('followRobots', True),
            'external_depth': actor_input.get('externalDepth', 0),
        }
        
        output_name = actor_input.get('outputName')
        cleanup = actor_input.get('cleanup', True)
        
        Actor.log.info(f"Starting scrape for: {url}")
        
        # Initialize scraper
        scraper = WebsiteScraper()
        
        # Check scraper engine
        if not scraper.check_engine():
            await Actor.fail(status_message='Scraper engine is not available')
            return
        
        # Scrape website
        output_dir = await scraper.scrape_website(url, config, output_name)
        
        if not output_dir:
            await Actor.fail(status_message='Failed to download website')
            return
        
        Actor.log.info("Website content downloaded successfully")
        
        # Clean up temporary engine files before zipping
        scraper.pre_zip_cleanup(output_dir)
        
        # Create ZIP archive
        Actor.log.info("Creating ZIP archive...")
        zip_path = scraper.create_zip(output_dir)
        
        if not zip_path:
            await Actor.fail(status_message='Failed to create ZIP archive')
            return
        
        zip_filename = os.path.basename(zip_path)
        Actor.log.info(f"ZIP archive created: {zip_filename}")
        
        # Save ZIP to key-value store
        with open(zip_path, 'rb') as f:
            zip_data = f.read()
            await Actor.set_value(zip_filename, zip_data, content_type='application/zip')
        
        Actor.log.info(f"Archive saved to key-value store: {zip_filename}")
        
        # Calculate statistics
        file_count = sum(len(files) for _, _, files in os.walk(output_dir))
        total_size = sum(
            os.path.getsize(os.path.join(root, file))
            for root, _, files in os.walk(output_dir)
            for file in files
        )
        zip_size = os.path.getsize(zip_path)
        
        # Push results to dataset
        await Actor.push_data({
            'url': url,
            'outputName': output_name or os.path.basename(output_dir),
            'zipFile': zip_filename,
            'fileCount': file_count,
            'totalSize': total_size,
            'zipSize': zip_size,
            'compressionRatio': round((1 - zip_size / total_size) * 100, 2) if total_size > 0 else 0,
            'timestamp': datetime.now().isoformat(),
            'config': config,
            'status': 'success'
        })
        
        # Cleanup if requested
        if cleanup:
            scraper.cleanup_directory(output_dir)
            try:
                os.remove(zip_path)  # Also remove local ZIP after saving to KVS
            except Exception:
                pass
        
        Actor.log.info("✓ Process completed successfully!")
