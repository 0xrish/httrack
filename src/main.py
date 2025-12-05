"""
HTTrack Website Scraper Actor - Main Module

This Actor uses HTTrack to scrape websites and create ZIP archives.
It reads configuration from Actor input and stores results in the default dataset.
"""

import os
import sys
import subprocess
import zipfile
import shutil
import urllib.parse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

try:
    from apify import Actor
    APIFY_AVAILABLE = True
except ImportError:
    APIFY_AVAILABLE = False
    # Mock Actor for local testing
    class Actor:
        class log:
            @staticmethod
            async def info(msg): 
                print(f"INFO: {msg}")
            
            @staticmethod
            async def warning(msg): 
                print(f"WARNING: {msg}")
            
            @staticmethod
            async def error(msg): 
                print(f"ERROR: {msg}")
        
        @staticmethod
        async def get_input(): 
            return {}
        
        @staticmethod
        async def fail(msg): 
            raise Exception(msg)
        
        @staticmethod
        async def set_value(key, value, **kwargs): 
            pass
        
        @staticmethod
        async def push_data(data): 
            pass
        
        def __enter__(self): 
            return self
        
        def __exit__(self, *args): 
            pass

import click


class HTTrackScraper:
    """HTTrack website scraper for Apify Actor"""
    
    def __init__(self, output_base: Optional[str] = None):
        if output_base is None:
            # Use environment-specific output directory
            if os.path.exists("/home/myuser/scraped_websites"):
                self.output_base = "/home/myuser/scraped_websites"
            else:
                self.output_base = os.path.join(os.getcwd(), "scraped_websites")
        else:
            self.output_base = output_base
        Path(self.output_base).mkdir(parents=True, exist_ok=True)
    
    def check_httrack(self) -> bool:
        """Check if HTTrack is installed"""
        try:
            result = subprocess.run(
                ["httrack", "--version"],
                capture_output=True,
                text=True,
                check=False
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def validate_url(self, url: str) -> bool:
        """Validate URL format and accessibility"""
        try:
            parsed = urllib.parse.urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False
            if parsed.scheme not in ['http', 'https']:
                return False
            return True
        except Exception:
            return False
    
    def build_httrack_command(
        self,
        url: str,
        output_dir: str,
        config: Dict[str, Any]
    ) -> list:
        """Build HTTrack command with parameters"""
        # Ensure URL is properly formatted
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        cmd = ["httrack", url, "-O", output_dir]
        
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
        
        # Additional options
        cmd.extend(["-v"])   # Verbose
        cmd.extend(["-N0"])  # Save structure
        cmd.extend(["-K0"])  # Keep original links
        cmd.extend(["-o"])   # Generate error files
        cmd.extend(["-%P"])  # Extended parsing
        cmd.extend(["-F", "Mozilla/5.0"])  # User agent
        
        # Non-interactive mode (important for automation)
        cmd.extend(["-Q"])   # Non-interactive mode
        
        return cmd
    
    async def scrape_website(
        self,
        url: str,
        config: Dict[str, Any],
        output_name: Optional[str] = None,
        logger=None
    ) -> Optional[str]:
        """Scrape website using HTTrack"""
        
        # Normalize URL
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Validate URL
        if not self.validate_url(url):
            error_msg = f"Invalid URL format: {url}. Please provide a valid HTTP/HTTPS URL."
            if logger:
                await logger.error(error_msg)
            else:
                print(f"ERROR: {error_msg}")
            return None
        
        # Create output directory name
        if not output_name:
            domain = url.replace("http://", "").replace("https://", "")
            domain = domain.split("/")[0].replace(":", "_")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_name = f"{domain}_{timestamp}"
        
        output_dir = os.path.join(self.output_base, output_name)
        os.makedirs(output_dir, exist_ok=True)
        
        if logger:
            await logger.info(f"Starting scrape: {url}")
            await logger.info(f"Output directory: {output_dir}")
            await logger.info(f"Configuration: {config}")
        else:
            print(f"INFO: Starting scrape: {url}")
            print(f"INFO: Output directory: {output_dir}")
            print(f"INFO: Configuration: {config}")
        
        # Build command
        cmd = self.build_httrack_command(url, output_dir, config)
        cmd_str = ' '.join(cmd)
        if logger:
            await logger.info(f"Command: {cmd_str}")
        else:
            print(f"INFO: Command: {cmd_str}")
        
        try:
            # Run HTTrack with proper error handling
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                timeout=config.get('max_time', 0) + 60 if config.get('max_time', 0) > 0 else None
            )
            
            # Check for common errors
            if result.returncode != 0:
                error_output = result.stderr or result.stdout or ""
                
                # Check for network/URL errors
                if "Unable to connect" in error_output or "Connection refused" in error_output:
                    error_msg = f"URL is not accessible: {url}. Please check the URL and network connection."
                    if logger:
                        await logger.error(error_msg)
                    else:
                        print(f"ERROR: {error_msg}")
                    return None
                
                if "Name or service not known" in error_output or "Could not resolve host" in error_output:
                    error_msg = f"Domain not found: {url}. Please check the URL spelling."
                    if logger:
                        await logger.error(error_msg)
                    else:
                        print(f"ERROR: {error_msg}")
                    return None
            
            if result.returncode == 0:
                if logger:
                    await logger.info("Scraping completed successfully")
                else:
                    print("INFO: Scraping completed successfully")
                return output_dir
            else:
                warn_msg = f"Scraping completed with warnings (exit code: {result.returncode})"
                if logger:
                    await logger.warning(warn_msg)
                else:
                    print(f"WARNING: {warn_msg}")
                if result.stderr:
                    error_preview = result.stderr[:500]
                    if logger:
                        await logger.info(f"Errors: {error_preview}")
                    else:
                        print(f"INFO: Errors: {error_preview}")
                # Still return output_dir if files were downloaded
                if os.path.exists(output_dir) and os.listdir(output_dir):
                    return output_dir
                return None
                
        except subprocess.TimeoutExpired:
            error_msg = f"Scraping timed out for {url}"
            if logger:
                await logger.error(error_msg)
            else:
                print(f"ERROR: {error_msg}")
            return None
        except Exception as e:
            error_msg = f"Error during scraping: {e}"
            if logger:
                await logger.error(error_msg)
            else:
                print(f"ERROR: {error_msg}")
            return None
    
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
            
            size_mb = os.path.getsize(zip_path) / (1024 * 1024)
            return zip_path
            
        except Exception as e:
            return None
    
    def cleanup_directory(self, directory: str):
        """Clean up scraped directory after zipping"""
        try:
            if os.path.exists(directory):
                shutil.rmtree(directory)
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
            await Actor.fail('Missing required input: url')
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
        
        await Actor.log.info(f"Starting HTTrack scraper for: {url}")
        
        # Initialize scraper
        scraper = HTTrackScraper()
        
        # Check HTTrack installation
        if not scraper.check_httrack():
            await Actor.fail('HTTrack is not installed in the container')
            return
        
        await Actor.log.info("HTTrack is installed and ready")
        
        # Scrape website (pass Actor.log as logger)
        output_dir = await scraper.scrape_website(url, config, output_name, logger=Actor.log)
        
        if not output_dir:
            await Actor.fail('Failed to scrape website')
            return
        
        await Actor.log.info(f"Scraping completed: {output_dir}")
        
        # Create ZIP archive
        await Actor.log.info("Creating ZIP archive...")
        zip_path = scraper.create_zip(output_dir)
        
        if not zip_path:
            await Actor.fail('Failed to create ZIP archive')
            return
        
        await Actor.log.info(f"ZIP created: {zip_path}")
        
        # Save ZIP to key-value store and get public URL
        zip_filename = os.path.basename(zip_path)
        with open(zip_path, 'rb') as f:
            zip_data = f.read()
        
        # Store ZIP in key-value store using Actor.set_value
        await Actor.set_value(zip_filename, zip_data, content_type='application/zip')
        
        await Actor.log.info(f"ZIP saved to key-value store: {zip_filename}")
        
        # Get public URL for the ZIP file using Apify SDK
        try:
            kv_store = await Actor.open_key_value_store()
            zip_url = await kv_store.get_public_url(zip_filename)
            await Actor.log.info(f"Public ZIP URL: {zip_url}")
        except Exception as e:
            # Fallback: construct URL manually if SDK method fails
            store_id = os.environ.get('APIFY_DEFAULT_KEY_VALUE_STORE_ID')
            if store_id:
                zip_url = f"https://api.apify.com/v2/key-value-stores/{store_id}/keys/{zip_filename}"
                await Actor.log.info(f"Public ZIP URL (fallback): {zip_url}")
            else:
                await Actor.log.warning("Could not generate public URL. Use output schema template to access ZIP file.")
                zip_url = None
        
        # Calculate statistics
        file_count = sum(len(files) for _, _, files in os.walk(output_dir))
        total_size = sum(
            os.path.getsize(os.path.join(root, file))
            for root, _, files in os.walk(output_dir)
            for file in files
        )
        zip_size = os.path.getsize(zip_path)
        
        # Store output with ZIP filename and direct download URL
        # Users can access the ZIP file via:
        # 1. Direct URL in OUTPUT.zipUrl (if available)
        # 2. Key-value store keys endpoint (browse and download by filename)
        output_data = {
            'zipFile': zip_filename,  # ZIP filename for reference
            'url': url,  # Original URL that was scraped
            'outputName': output_name or os.path.basename(output_dir),
        }
        if zip_url:
            output_data['zipUrl'] = zip_url  # Direct public download URL
        await Actor.set_value('OUTPUT', output_data)
        
        # Push results to dataset with ZIP URL
        dataset_record = {
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
        }
        if zip_url:
            dataset_record['zipUrl'] = zip_url
        await Actor.push_data(dataset_record)
        
        # Cleanup if requested
        if cleanup:
            await Actor.log.info("Cleaning up source directory...")
            scraper.cleanup_directory(output_dir)
            os.remove(zip_path)  # Also remove local ZIP after saving to KVS
        
        await Actor.log.info("✓ Scraping completed successfully!")


# Click CLI for local testing
@click.command()
@click.argument('url')
@click.option('--depth', default=2, help='Mirror depth (how many links deep)')
@click.option('--output-dir', default=None, help='Output directory for scraped files')
@click.option('--output-name', default=None, help='Custom output name')
@click.option('--stay-on-domain/--no-stay-on-domain', default=True, help='Stay on same domain')
@click.option('--connections', default=4, help='Number of simultaneous connections')
@click.option('--timeout', default=30, help='Connection timeout in seconds')
@click.option('--no-images', is_flag=True, help='Skip downloading images')
@click.option('--no-videos', is_flag=True, help='Skip downloading videos')
@click.option('--no-robots', is_flag=True, help='Ignore robots.txt')
@click.option('--max-rate', default=0, help='Maximum download rate in KB/s (0 = unlimited)')
@click.option('--max-size', default=0, help='Maximum size in MB (0 = unlimited)')
@click.option('--max-time', default=0, help='Maximum time in seconds (0 = unlimited)')
@click.option('--no-cleanup', is_flag=True, help='Keep source files after creating ZIP')
def cli(url, depth, output_dir, output_name, stay_on_domain, connections, timeout,
        no_images, no_videos, no_robots, max_rate, max_size, max_time, no_cleanup):
    """HTTrack Website Scraper - Local CLI Tool
    
    Scrapes a website using HTTrack and creates a ZIP archive.
    
    Example:
        python -m src.cli https://example.com --depth 3 --output-name my_backup
    """
    import asyncio
    
    async def run_cli():
        # Setup output directory
        if output_dir:
            scraper = HTTrackScraper(output_base=output_dir)
        else:
            scraper = HTTrackScraper()
        
        # Check HTTrack installation
        if not scraper.check_httrack():
            click.echo("ERROR: HTTrack is not installed. Please install HTTrack first.", err=True)
            sys.exit(1)
        
        click.echo(f"✓ HTTrack is installed and ready")
        
        # Build config
        config = {
            'depth': depth,
            'stay_on_domain': stay_on_domain,
            'max_rate': max_rate,
            'max_size': max_size,
            'max_time': max_time,
            'connections': connections,
            'retries': 2,
            'timeout': timeout,
            'get_images': not no_images,
            'get_videos': not no_videos,
            'follow_robots': not no_robots,
            'external_depth': 0,
        }
        
        # Scrape website (no logger for CLI - uses print)
        click.echo(f"Starting scrape: {url}")
        output_dir_path = await scraper.scrape_website(url, config, output_name, logger=None)
        
        if not output_dir_path:
            click.echo("ERROR: Failed to scrape website", err=True)
            sys.exit(1)
        
        click.echo(f"✓ Scraping completed: {output_dir_path}")
        
        # Create ZIP
        click.echo("Creating ZIP archive...")
        zip_path = scraper.create_zip(output_dir_path)
        
        if not zip_path:
            click.echo("ERROR: Failed to create ZIP archive", err=True)
            sys.exit(1)
        
        zip_size_mb = os.path.getsize(zip_path) / (1024 * 1024)
        click.echo(f"✓ ZIP created: {zip_path} ({zip_size_mb:.2f} MB)")
        
        # Cleanup if requested
        if not no_cleanup:
            click.echo("Cleaning up source directory...")
            scraper.cleanup_directory(output_dir_path)
            os.remove(zip_path)
            click.echo("✓ Cleanup complete")
        
        click.echo(f"\n✓ Success! ZIP file: {zip_path}")
    
    asyncio.run(run_cli())


if __name__ == '__main__':
    # Allow running as CLI when not in Apify environment
    if not APIFY_AVAILABLE or len(sys.argv) > 1:
        cli()
    else:
        # Run as Apify Actor
        import asyncio
        asyncio.run(main())
