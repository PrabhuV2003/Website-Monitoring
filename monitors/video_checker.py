"""
Video Checker - Validates embedded videos on web pages.
Checks for YouTube, Vimeo, and other video embeds to ensure they are still available.
"""
import re
import time
import requests
from typing import Any, Dict, List, Set
from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup

from .base_monitor import BaseMonitor, MonitorResult


class VideoChecker(BaseMonitor):
    """Crawls pages and validates all embedded videos."""
    
    @property
    def name(self) -> str:
        return "videos"
    
    def __init__(self, config: Dict[str, Any], base_url: str):
        super().__init__(config, base_url)
        self.video_config = config.get('video_checker', {})
        self.timeout = self.video_config.get('timeout', 15)
        
        # Browser mode settings
        self.use_browser = config.get('use_browser', False)
        self.headless = config.get('headless', True)
        self.browser = None
        
        self.checked_videos: Set[str] = set()
        self.broken_videos: List[Dict] = []
        self.all_videos: List[Dict] = []
    
    def run(self) -> List[MonitorResult]:
        """Run video checks on all critical pages."""
        self.results = []
        self.checked_videos = set()
        self.broken_videos = []
        self.all_videos = []
        
        self.logger.info("Starting video checker")
        
        # Initialize browser if needed
        if self.use_browser:
            try:
                from utils.browser import BrowserManager
                self.browser = BrowserManager(headless=self.headless)
                if not self.browser.start():
                    self.logger.warning("Browser failed to start, falling back to HTTP requests")
                    self.use_browser = False
                    self.browser = None
                else:
                    mode = "visible" if not self.headless else "headless"
                    self.logger.info(f"Browser started in {mode} mode")
            except Exception as e:
                self.logger.warning(f"Browser init failed: {e}, falling back to HTTP requests")
                self.use_browser = False
                self.browser = None
        
        try:
            # Check videos on each critical page
            self._check_videos_per_page()
            
            # Generate summary results
            self._generate_summary()
        finally:
            # Cleanup browser
            if self.browser:
                self.browser.stop()
                self.browser = None
        
        return self.results
    
    def _check_videos_per_page(self):
        """Check all videos on each critical page."""
        pages = self.config.get('critical_pages', ['/'])
        
        for page in pages:
            url = self.get_full_url(page)
            page_broken = []
            page_videos = []
            
            try:
                self.logger.info(f"Checking videos on: {page}")
                
                # Fetch page content
                if self.browser:
                    success, status, load_time = self.browser.navigate(url)
                    if not success:
                        self.logger.warning(f"Page {page} failed to load in browser")
                        continue
                    html_content = self.browser.get_page_source()
                else:
                    response = requests.get(url, timeout=15,
                        headers={'User-Agent': 'WordPress-Monitor/1.0'})
                    
                    if response.status_code != 200:
                        self.logger.warning(f"Page {page} returned status {response.status_code}")
                        continue
                    
                    html_content = response.text
                
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Extract all videos from the page
                videos = self._extract_videos(soup, url)
                
                self.logger.info(f"Found {len(videos)} videos on {page}")
                
                for video_info in videos:
                    video_url = video_info['url']
                    video_id = video_info.get('video_id', '')
                    video_type = video_info['type']
                    
                    # Skip already checked videos
                    if video_url in self.checked_videos:
                        continue
                    self.checked_videos.add(video_url)
                    
                    # Check if video is available
                    is_available, error_message = self._check_video_availability(video_info)
                    
                    video_detail = {
                        'video_url': video_url,
                        'video_id': video_id,
                        'video_type': video_type,
                        'found_on_page': page,
                        'page_url': url,
                        'is_available': is_available,
                        'error': error_message if not is_available else None
                    }
                    
                    if is_available:
                        page_videos.append(video_detail)
                        self.all_videos.append(video_detail)
                    else:
                        video_detail['status'] = 'BROKEN'
                        video_detail['status_message'] = error_message
                        page_broken.append(video_detail)
                        self.broken_videos.append(video_detail)
                
                # Report broken videos on this page
                if page_broken:
                    self.add_result('error',
                        f'{len(page_broken)} broken videos on {page}',
                        severity='high', url=url,
                        details={
                            'error_summary': f'Found {len(page_broken)} broken/unavailable videos',
                            'broken_videos': page_broken,
                            'total_videos': len(videos)
                        })
                
                # Success summary for this page
                if not page_broken and videos:
                    self.add_result('success',
                        f'All {len(videos)} videos working on {page}',
                        url=url,
                        details={
                            'total_videos': len(videos),
                            'all_checked_videos': page_videos
                        })
                elif not videos:
                    self.add_result('info',
                        f'No videos found on {page}',
                        severity='low', url=url)
                        
            except Exception as e:
                self.logger.error(f"Error checking videos on {page}: {e}")
                self.add_result('error',
                    f'Failed to check videos on {page}: {str(e)[:100]}',
                    severity='medium', url=url)
    
    def _extract_videos(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extract all video embeds from the page."""
        videos = []
        seen_ids = set()
        
        # Find YouTube iframes
        for iframe in soup.find_all('iframe'):
            src = iframe.get('src') or iframe.get('data-src') or ''
            
            # YouTube embeds
            youtube_patterns = [
                r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
                r'youtube-nocookie\.com/embed/([a-zA-Z0-9_-]{11})',
                r'youtu\.be/([a-zA-Z0-9_-]{11})'
            ]
            
            for pattern in youtube_patterns:
                match = re.search(pattern, src)
                if match:
                    video_id = match.group(1)
                    if video_id not in seen_ids:
                        seen_ids.add(video_id)
                        videos.append({
                            'url': src,
                            'video_id': video_id,
                            'type': 'youtube',
                            'embed_url': f'https://www.youtube.com/embed/{video_id}'
                        })
                    break
            
            # Vimeo embeds
            vimeo_match = re.search(r'player\.vimeo\.com/video/(\d+)', src)
            if vimeo_match:
                video_id = vimeo_match.group(1)
                if video_id not in seen_ids:
                    seen_ids.add(video_id)
                    videos.append({
                        'url': src,
                        'video_id': video_id,
                        'type': 'vimeo',
                        'embed_url': f'https://player.vimeo.com/video/{video_id}'
                    })
            
            # Wistia embeds
            wistia_match = re.search(r'wistia\.com/embed/iframe/([a-zA-Z0-9]+)', src)
            if wistia_match:
                video_id = wistia_match.group(1)
                if video_id not in seen_ids:
                    seen_ids.add(video_id)
                    videos.append({
                        'url': src,
                        'video_id': video_id,
                        'type': 'wistia',
                        'embed_url': src
                    })
        
        # Find HTML5 video tags
        for video in soup.find_all('video'):
            sources = video.find_all('source')
            if sources:
                for source in sources:
                    src = source.get('src')
                    if src:
                        full_url = urljoin(base_url, src)
                        if full_url not in seen_ids:
                            seen_ids.add(full_url)
                            videos.append({
                                'url': full_url,
                                'video_id': '',
                                'type': 'html5',
                                'embed_url': full_url
                            })
            else:
                src = video.get('src')
                if src:
                    full_url = urljoin(base_url, src)
                    if full_url not in seen_ids:
                        seen_ids.add(full_url)
                        videos.append({
                            'url': full_url,
                            'video_id': '',
                            'type': 'html5',
                            'embed_url': full_url
                        })
        
        # Find YouTube links that might be displayed as embeds via JavaScript
        for a in soup.find_all('a', href=True):
            href = a.get('href', '')
            youtube_link_patterns = [
                r'youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
                r'youtu\.be/([a-zA-Z0-9_-]{11})'
            ]
            
            for pattern in youtube_link_patterns:
                match = re.search(pattern, href)
                if match:
                    video_id = match.group(1)
                    # Only add if it has video-related classes or is likely an embed
                    parent_classes = ' '.join(a.get('class', []))
                    if any(x in parent_classes.lower() for x in ['video', 'play', 'youtube', 'popup']):
                        if video_id not in seen_ids:
                            seen_ids.add(video_id)
                            videos.append({
                                'url': href,
                                'video_id': video_id,
                                'type': 'youtube_link',
                                'embed_url': f'https://www.youtube.com/embed/{video_id}'
                            })
                    break
        
        return videos
    
    def _check_video_availability(self, video_info: Dict) -> tuple:
        """Check if a video is available."""
        video_type = video_info['type']
        video_id = video_info.get('video_id', '')
        
        try:
            if video_type in ['youtube', 'youtube_link']:
                return self._check_youtube_video(video_id)
            elif video_type == 'vimeo':
                return self._check_vimeo_video(video_id)
            elif video_type == 'html5':
                return self._check_html5_video(video_info['url'])
            else:
                # For unknown types, just check if the embed URL is accessible
                return self._check_embed_url(video_info['embed_url'])
        except Exception as e:
            return False, f"Error checking video: {str(e)[:100]}"
    
    def _check_youtube_video(self, video_id: str) -> tuple:
        """Check if a YouTube video is available using oembed."""
        if not video_id:
            return False, "No video ID found"
        
        # Use YouTube's oembed endpoint (no API key required)
        oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        
        try:
            response = requests.get(oembed_url, timeout=self.timeout)
            
            if response.status_code == 200:
                return True, None
            elif response.status_code == 401:
                return False, "Video is private or restricted"
            elif response.status_code == 403:
                return False, "Video embedding disabled"
            elif response.status_code == 404:
                return False, "Video not found or deleted"
            else:
                return False, f"YouTube returned status {response.status_code}"
        except requests.exceptions.Timeout:
            return False, "Timeout checking YouTube video"
        except Exception as e:
            return False, f"Error: {str(e)[:50]}"
    
    def _check_vimeo_video(self, video_id: str) -> tuple:
        """Check if a Vimeo video is available."""
        if not video_id:
            return False, "No video ID found"
        
        # Use Vimeo's oembed endpoint
        oembed_url = f"https://vimeo.com/api/oembed.json?url=https://vimeo.com/{video_id}"
        
        try:
            response = requests.get(oembed_url, timeout=self.timeout)
            
            if response.status_code == 200:
                return True, None
            elif response.status_code == 403:
                return False, "Video is private"
            elif response.status_code == 404:
                return False, "Video not found"
            else:
                return False, f"Vimeo returned status {response.status_code}"
        except requests.exceptions.Timeout:
            return False, "Timeout checking Vimeo video"
        except Exception as e:
            return False, f"Error: {str(e)[:50]}"
    
    def _check_html5_video(self, video_url: str) -> tuple:
        """Check if an HTML5 video file is accessible."""
        try:
            response = requests.head(video_url, timeout=self.timeout,
                allow_redirects=True,
                headers={'User-Agent': 'WordPress-Monitor/1.0'})
            
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', '')
                if 'video' in content_type.lower():
                    return True, None
                else:
                    return False, f"Not a video file: {content_type}"
            elif response.status_code == 403:
                return False, "Access denied"
            elif response.status_code == 404:
                return False, "Video file not found"
            else:
                return False, f"HTTP {response.status_code}"
        except requests.exceptions.Timeout:
            return False, "Timeout loading video"
        except Exception as e:
            return False, f"Error: {str(e)[:50]}"
    
    def _check_embed_url(self, embed_url: str) -> tuple:
        """Check if an embed URL is accessible."""
        try:
            response = requests.head(embed_url, timeout=self.timeout,
                allow_redirects=True)
            
            if response.status_code < 400:
                return True, None
            else:
                return False, f"HTTP {response.status_code}"
        except Exception as e:
            return False, f"Error: {str(e)[:50]}"
    
    def _generate_summary(self):
        """Generate overall summary results."""
        if self.broken_videos:
            self.add_result('error',
                f'Found {len(self.broken_videos)} broken videos across site',
                severity='high',
                details={
                    'summary': f'Checked {len(self.checked_videos)} videos, found {len(self.broken_videos)} broken',
                    'broken_videos': self.broken_videos[:20],
                    'total_checked': len(self.checked_videos)
                })
        elif self.all_videos:
            self.add_result('success',
                f'All {len(self.checked_videos)} videos are working',
                details={
                    'summary': 'All embedded videos are accessible',
                    'total_checked': len(self.checked_videos)
                })
        else:
            self.add_result('info',
                'No videos found on the checked pages',
                severity='low',
                details={
                    'summary': 'No YouTube, Vimeo, or HTML5 videos detected'
                })
