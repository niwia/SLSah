"""
Steam Web API interface with retry logic and rate limiting
"""

import requests
import time
from typing import Optional, Dict, Any, List
from functools import wraps


class APIError(Exception):
    """Custom exception for API errors"""
    pass


class RateLimitError(APIError):
    """Raised when rate limit is exceeded"""
    pass


def retry_with_backoff(max_retries=3, base_delay=1, max_delay=30, backoff_factor=2):
    """
    Decorator for retrying functions with exponential backoff
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay between retries
        backoff_factor: Multiplier for exponential backoff
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            delay = base_delay
            
            while retries <= max_retries:
                try:
                    return func(*args, **kwargs)
                except (requests.RequestException, requests.Timeout, 
                        requests.ConnectionError) as e:
                    retries += 1
                    
                    if retries > max_retries:
                        raise APIError(f"Max retries ({max_retries}) exceeded: {e}")
                    
                    # Calculate delay with exponential backoff
                    wait_time = min(delay * (backoff_factor ** (retries - 1)), max_delay)
                    
                    print(f"Request failed: {e}")
                    print(f"Retrying in {wait_time:.1f} seconds... (Attempt {retries}/{max_retries})")
                    
                    time.sleep(wait_time)
                except RateLimitError:
                    retries += 1
                    if retries > max_retries:
                        raise APIError("Rate limit exceeded, max retries reached")
                    
                    # Longer delay for rate limits
                    wait_time = min(60, delay * (backoff_factor ** retries))
                    print(f"Rate limit hit. Waiting {wait_time:.0f} seconds...")
                    time.sleep(wait_time)
        
        return wrapper
    return decorator


class SteamAPI:
    """Interface for Steam Web API with retry logic and caching"""
    
    BASE_URL = "https://api.steampowered.com"
    STORE_API_URL = "https://store.steampowered.com/api"
    
    def __init__(self, api_key: str, rate_limit_delay: float = 0.5):
        """
        Initialize Steam API client
        
        Args:
            api_key: Steam Web API key
            rate_limit_delay: Minimum seconds between requests to avoid rate limiting
        """
        self.api_key = api_key
        self.rate_limit_delay = rate_limit_delay
        self.last_request_time = 0
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SLS-AH-Tool/2.0'
        })
    
    def _wait_for_rate_limit(self):
        """Ensure we don't exceed rate limits"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = time.time()
    
    @retry_with_backoff(max_retries=3, base_delay=2)
    def _make_request(self, url: str, params: Dict = None) -> Dict:
        """
        Make API request with retry logic
        
        Args:
            url: API endpoint URL
            params: Query parameters
        
        Returns:
            JSON response as dict
        """
        self._wait_for_rate_limit()
        
        response = self.session.get(url, params=params, timeout=30)
        
        # Check for rate limiting (HTTP 429)
        if response.status_code == 429:
            raise RateLimitError("Rate limit exceeded")
        
        # Raise for other HTTP errors
        response.raise_for_status()
        
        return response.json()
    
    def get_schema_for_game(self, app_id: int, language: str = "english") -> Optional[Dict]:
        """
        Fetch achievement schema for a game
        
        Args:
            app_id: Steam App ID
            language: Language for achievement descriptions
        
        Returns:
            Schema dict or None if not available
        """
        url = f"{self.BASE_URL}/ISteamUserStats/GetSchemaForGame/v2/"
        params = {
            'key': self.api_key,
            'appid': app_id,
            'l': language
        }
        
        try:
            data = self._make_request(url, params)
            
            if 'game' not in data:
                return None
            
            return data['game']
        except Exception as e:
            print(f"Error fetching schema for app {app_id}: {e}")
            return None
    
    def get_player_achievements(self, steam_id: str, app_id: int) -> Optional[Dict]:
        """
        Fetch player's achievement progress for a game
        
        Args:
            steam_id: Steam User ID
            app_id: Steam App ID
        
        Returns:
            Achievement progress dict or None
        """
        url = f"{self.BASE_URL}/ISteamUserStats/GetPlayerAchievements/v1/"
        params = {
            'key': self.api_key,
            'steamid': steam_id,
            'appid': app_id
        }
        
        try:
            data = self._make_request(url, params)
            return data.get('playerstats')
        except Exception as e:
            print(f"Error fetching achievements for app {app_id}: {e}")
            return None
    
    def get_owned_games(self, steam_id: str, include_appinfo: bool = True) -> List[Dict]:
        """
        Fetch list of games owned by user
        
        Args:
            steam_id: Steam User ID
            include_appinfo: Include game names and icons
        
        Returns:
            List of game dicts
        """
        url = f"{self.BASE_URL}/IPlayerService/GetOwnedGames/v1/"
        params = {
            'key': self.api_key,
            'steamid': steam_id,
            'include_appinfo': 1 if include_appinfo else 0,
            'include_played_free_games': 1
        }
        
        try:
            data = self._make_request(url, params)
            return data.get('response', {}).get('games', [])
        except Exception as e:
            print(f"Error fetching owned games: {e}")
            return []
    
    @retry_with_backoff(max_retries=3, base_delay=1)
    def search_games(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search for games by name using Steam Store API
        
        Args:
            query: Search query (game name)
            max_results: Maximum number of results to return
        
        Returns:
            List of matching games with {app_id, name, type}
        """
        # Steam doesn't have a direct search API, so we use the store search
        url = "https://steamcommunity.com/actions/SearchApps/"
        params = {'text': query}
        
        try:
            self._wait_for_rate_limit()
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            results = response.json()
            
            # Filter and format results
            games = []
            for item in results[:max_results]:
                games.append({
                    'appid': int(item['appid']),
                    'name': item['name'],
                    'logo': item.get('logo', '')
                })
            
            return games
        except Exception as e:
            print(f"Error searching for games: {e}")
            return []
    
    def get_app_details(self, app_id: int) -> Optional[Dict]:
        """
        Get detailed information about an app from Steam Store
        
        Args:
            app_id: Steam App ID
        
        Returns:
            App details dict or None
        """
        url = f"{self.STORE_API_URL}/appdetails"
        params = {'appids': app_id}
        
        try:
            data = self._make_request(url, params)
            
            app_data = data.get(str(app_id))
            if app_data and app_data.get('success'):
                return app_data.get('data')
            
            return None
        except Exception as e:
            print(f"Error fetching app details for {app_id}: {e}")
            return None
    
    def verify_api_key(self, steam_id: str) -> bool:
        """
        Verify that the API key is valid
        
        Args:
            steam_id: Steam User ID to test with
        
        Returns:
            True if API key is valid
        """
        try:
            # Try to fetch owned games - simple test
            url = f"{self.BASE_URL}/IPlayerService/GetOwnedGames/v1/"
            params = {
                'key': self.api_key,
                'steamid': steam_id
            }
            
            response = self._make_request(url, params)
            return 'response' in response
        except:
            return False
    
    def close(self):
        """Close the session"""
        self.session.close()
