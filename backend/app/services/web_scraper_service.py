import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional
from loguru import logger
import re
from urllib.parse import urlparse


class WebScraperService:
    """Webページのスクレイピングを行うサービス"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def scrape_url(self, url: str) -> Optional[Dict[str, str]]:
        """
        URLからWebページの内容をスクレイピングする
        
        Args:
            url (str): スクレイピング対象のURL
            
        Returns:
            Optional[Dict[str, str]]: スクレイピング結果（title, content, url）
        """
        try:
            logger.info(f"Scraping URL: {url}")
            
            # URLの正規化
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # ページの取得
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # HTMLの解析
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 不要な要素を削除
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                element.decompose()
            
            # タイトルの取得
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "No title"
            
            # メインコンテンツの抽出
            main_content = None
            for selector in ['main', 'article', 'div[role="main"]', 'body']:
                main_content = soup.select_one(selector)
                if main_content:
                    break
            
            if not main_content:
                main_content = soup.body if soup.body else soup
            
            # テキストの抽出とクリーニング
            content = self._extract_clean_text(main_content)
            
            # 結果の検証
            if not content or len(content.strip()) < 50:
                logger.warning(f"Extracted content is too short for URL: {url}")
                return None
            
            result = {
                'url': url,
                'title': title_text,
                'content': content
            }
            
            logger.info(f"Successfully scraped URL: {url}, content length: {len(content)}")
            return result
            
        except requests.RequestException as e:
            logger.error(f"Request error while scraping {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None
    
    def _extract_clean_text(self, element) -> str:
        """
        HTML要素からクリーンなテキストを抽出する
        
        Args:
            element: BeautifulSoup要素
            
        Returns:
            str: クリーンなテキスト
        """
        if not element:
            return ""
        
        # テキストの取得
        text = element.get_text()
        
        # テキストのクリーニング
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = text.strip()
        
        return text
    
    def validate_url(self, url: str) -> bool:
        """
        URLの形式を検証する
        
        Args:
            url (str): 検証対象のURL
            
        Returns:
            bool: 有効なURLかどうか
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False


class WebScraperServiceFactory:
    """WebScraperServiceのファクトリークラス"""
    
    _instance = None
    
    @classmethod
    def create(cls) -> WebScraperService:
        if cls._instance is None:
            cls._instance = WebScraperService()
        return cls._instance 