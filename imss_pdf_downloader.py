#!/usr/bin/env python3
"""
IMSS Clinical Guidelines PDF Downloader
Downloads all PDF files from IMSS clinical practice guidelines website.
"""

import requests
from bs4 import BeautifulSoup
import os
import time
import re
from urllib.parse import urljoin, urlparse
import logging

class IMSSPDFDownloader:
    def __init__(self, base_url="https://www.imss.gob.mx/guias_practicaclinica", download_dir="imss_pdfs"):
        self.base_url = base_url
        self.download_dir = download_dir
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Create download directory
        os.makedirs(self.download_dir, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('imss_download.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def get_total_pages(self):
        """Get the total number of pages to scrape"""
        try:
            response = self.session.get(f"{self.base_url}?field_categoria_gs_value=All")
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find pagination links
            pagination = soup.find('ul', class_='pager')
            if pagination:
                page_links = pagination.find_all('a')
                if page_links:
                    # Get the last page number
                    last_page_link = page_links[-1]
                    if 'page=' in last_page_link.get('href', ''):
                        page_num = re.search(r'page=(\d+)', last_page_link['href'])
                        if page_num:
                            return int(page_num.group(1)) + 1  # Pages are 0-indexed
            
            return 1  # Default to 1 page if no pagination found
        except Exception as e:
            self.logger.error(f"Error getting total pages: {e}")
            return 1
    
    def extract_pdf_links(self, page_num=0):
        """Extract all PDF links from a specific page"""
        pdf_links = []
        try:
            url = f"{self.base_url}?field_categoria_gs_value=All&page={page_num}"
            self.logger.info(f"Scraping page {page_num + 1}: {url}")
            
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all PDF links
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.endswith('.pdf'):
                    # Get the filename to check if it's a GER PDF
                    filename = os.path.basename(urlparse(href).path)
                    
                    # Only process GER PDFs (skip GRR PDFs)
                    if 'GER' not in filename.upper():
                        continue
                    
                    # Get the full URL
                    full_url = urljoin("https://www.imss.gob.mx", href)
                    
                    # Extract guide info
                    guide_title = link.get_text(strip=True)
                    
                    # Try to find the guide identifier and title from parent elements
                    parent_section = link.find_parent(['div', 'section', 'article'])
                    guide_id = ""
                    if parent_section:
                        # Look for IMSS identifier pattern
                        text_content = parent_section.get_text()
                        imss_match = re.search(r'IMSS-\d+-\d+', text_content)
                        if imss_match:
                            guide_id = imss_match.group(0)
                    
                    pdf_info = {
                        'url': full_url,
                        'filename': filename,
                        'title': guide_title,
                        'guide_id': guide_id
                    }
                    pdf_links.append(pdf_info)
            
            self.logger.info(f"Found {len(pdf_links)} GER PDF links on page {page_num + 1}")
            return pdf_links
            
        except Exception as e:
            self.logger.error(f"Error extracting PDF links from page {page_num}: {e}")
            return []
    
    def download_pdf(self, pdf_info, retry_count=3):
        """Download a single PDF file"""
        for attempt in range(retry_count):
            try:
                url = pdf_info['url']
                filename = pdf_info['filename']
                
                # Create a safe filename
                safe_filename = re.sub(r'[^\w\-_\.]', '_', filename)
                if pdf_info['guide_id']:
                    safe_filename = f"{pdf_info['guide_id']}_{safe_filename}"
                
                filepath = os.path.join(self.download_dir, safe_filename)
                
                # Skip if file already exists
                if os.path.exists(filepath):
                    self.logger.info(f"Skipping {safe_filename} (already exists)")
                    return True
                
                self.logger.info(f"Downloading: {safe_filename}")
                response = self.session.get(url, stream=True)
                response.raise_for_status()
                
                # Check if response is actually a PDF
                content_type = response.headers.get('content-type', '').lower()
                if 'pdf' not in content_type and len(response.content) < 1000:
                    self.logger.warning(f"Skipping {safe_filename} (not a valid PDF)")
                    return False
                
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                self.logger.info(f"Successfully downloaded: {safe_filename}")
                return True
                
            except Exception as e:
                self.logger.error(f"Attempt {attempt + 1} failed for {pdf_info['filename']}: {e}")
                if attempt < retry_count - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                
        return False
    
    def download_all_pdfs(self):
        """Download all PDFs from all pages"""
        self.logger.info("Starting IMSS PDF download process...")
        
        total_pages = self.get_total_pages()
        self.logger.info(f"Total pages to process: {total_pages}")
        
        all_pdf_links = []
        
        # Extract PDF links from all pages
        for page_num in range(total_pages):
            pdf_links = self.extract_pdf_links(page_num)
            all_pdf_links.extend(pdf_links)
            time.sleep(1)  # Be respectful to the server
        
        self.logger.info(f"Total GER PDFs found: {len(all_pdf_links)}")
        
        # Download all PDFs
        successful_downloads = 0
        failed_downloads = 0
        
        for i, pdf_info in enumerate(all_pdf_links, 1):
            self.logger.info(f"Progress: {i}/{len(all_pdf_links)}")
            
            if self.download_pdf(pdf_info):
                successful_downloads += 1
            else:
                failed_downloads += 1
            
            # Small delay between downloads
            time.sleep(0.5)
        
        self.logger.info(f"Download complete! Success: {successful_downloads}, Failed: {failed_downloads}")
        self.logger.info(f"PDFs saved in: {os.path.abspath(self.download_dir)}")

def main():
    downloader = IMSSPDFDownloader()
    downloader.download_all_pdfs()

if __name__ == "__main__":
    main()