import json
import requests
from bs4 import BeautifulSoup
import time
import random
from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import re

# 初始化配置
ua = UserAgent()
BASE_URL = "https://asia.si.edu"
INPUT_FILE = "freer_museum_links.json"
OUTPUT_FILE = "freer_artifacts_details.json"
REQUEST_DELAY = (0.5, 2)  # 随机延迟范围
MAX_RETRIES = 3
MAX_WORKERS = 10  # 线程数

# 全局Session对象
session = requests.Session()

def load_links():
    """从JSON文件加载文物链接"""
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_results(data):
    """保存结果到JSON文件"""
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_random_headers():
    """生成随机请求头"""
    return {
        "User-Agent": ua.random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": BASE_URL,
        "DNT": "1"
    }

def get_with_retry(url):
    """带重试机制的请求函数"""
    for attempt in range(MAX_RETRIES):
        try:
            response = session.get(
                url,
                headers=get_random_headers(),
                timeout=10
            )
            response.raise_for_status()
            
            if "Request Rejected" in response.text:
                raise requests.exceptions.RequestException("Request rejected by server")
                
            return response
        except requests.exceptions.RequestException as e:
            print(f"请求失败 (尝试 {attempt + 1}/{MAX_RETRIES}): {url} - {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(random.uniform(*REQUEST_DELAY))
    return None

def get_primary_image(soup):
    """提取文物主图片（包括IIIF格式）"""
    # 1. 检查OpenSeadragon查看器（IIIF图片）
    iiif_container = soup.find('div', {'id': 'openseadragonViewer'})
    if iiif_container and iiif_container.has_attr('data-image-ids'):
        image_id = iiif_container['data-image-ids'].strip().split(',')[0].strip()
        if image_id:
            return f"https://ids.si.edu/ids/iiif/{image_id}/full/full/0/default.jpg"
    
    # 2. 检查主图片标签
    img_tags = [
        soup.find('img', {'id': 'main-image'}),
        soup.find('img', class_='primary-image'),
        soup.find('img', class_='object-image')
    ]
    
    for img_tag in img_tags:
        if img_tag and img_tag.get('src'):
            img_url = img_tag['src'].split('?')[0].split(';')[0]
            if not img_url.startswith('http'):
                img_url = BASE_URL + img_url
            return img_url
    
    # 3. 检查meta标签中的图片
    meta_image = soup.find('meta', property='og:image')
    if meta_image and meta_image.get('content'):
        img_url = meta_image['content']
        if not img_url.startswith('http'):
            img_url = BASE_URL + img_url
        return img_url
    
    return None

def parse_artifact_page(html):
    """解析文物详情页HTML"""
    soup = BeautifulSoup(html, 'lxml')
    
    # 提取基本信息
    artifact = {
        'title': soup.find('h1').get_text(strip=True) if soup.find('h1') else None,
        'date': None,
        'culture': None,
        'medium': None,
        'dimensions': None,
        'description': None,
        'image_url': None,  # 只存储主图片URL
        'accession_number': None,
        'edan_id': None,
        'credit_line': None
    }
    
    # 提取"At a Glance"部分的属性
    glance_section = soup.find('div', class_='individual-object-at-a-glance__attributes')
    if glance_section:
        for item in glance_section.find_all('li'):
            label = item.find('h3').get_text(strip=True).lower() if item.find('h3') else None
            value = item.find('div').get_text(strip=True) if item.find('div') else None
            
            if 'period' in label:
                artifact['date'] = value
            elif 'geography' in label:
                artifact['culture'] = value
            elif 'medium' in label or 'material' in label:
                artifact['medium'] = value
            elif 'dimension' in label:
                artifact['dimensions'] = value
            elif 'accession' in label:
                artifact['accession_number'] = value
            elif 'edan' in label:
                artifact['edan_id'] = value
    
    # 提取详细描述
    details_section = soup.find('div', class_='individual-object-details')
    if details_section:
        # 提取艺术家信息
        artist_label = details_section.find('h3', string=lambda t: 'artist' in t.lower())
        if artist_label:
            artist_value = artist_label.find_next('div').get_text(strip=True)
            artifact['artist'] = artist_value
        
        # 提取描述文本
        description_label = details_section.find('h3', string=lambda t: 'description' in t.lower() or 'label' in t.lower())
        if description_label:
            description_value = description_label.find_next('div').get_text(strip=True)
            artifact['description'] = description_value
        
        # 提取信用信息
        credit_label = details_section.find('h3', string=lambda t: 'credit' in t.lower())
        if credit_label:
            credit_value = credit_label.find_next('div').get_text(strip=True)
            artifact['credit_line'] = credit_value
    
    # 提取文物主图片
    artifact['image_url'] = get_primary_image(soup)
    
    return artifact

def process_url(url):
    """处理单个URL的任务函数"""
    print(f"开始处理: {url}")
    response = get_with_retry(url)
    if not response:
        print(f"⚠️ 无法获取页面: {url}")
        return None
    
    artifact_data = parse_artifact_page(response.text)
    if not artifact_data:
        print(f"⚠️ 无法解析页面: {url}")
        return None
    
    artifact_data['url'] = url
    print(f"✅ 完成: {url} (图片: {'已找到' if artifact_data['image_url'] else '未找到'})")
    return artifact_data

def scrape_artifacts():
    """主爬取函数（多线程版）"""
    # 加载已有链接
    artifact_urls = load_links()
    total = len(artifact_urls)
    print(f"共发现 {total} 个文物链接")
    
    # 检查已有进度
    try:
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
            scraped_ids = {item['url'] for item in existing_data if 'url' in item}
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = []
        scraped_ids = set()
    
    results = existing_data.copy()
    pending_urls = [url for url in artifact_urls if url not in scraped_ids]
    
    if not pending_urls:
        print("无需补爬，所有数据已存在！")
        return
    
    print(f"待爬取链接数: {len(pending_urls)}")
    
    # 使用线程池并发处理
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_url = {
            executor.submit(process_url, url): url 
            for url in pending_urls
        }
        
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                artifact_data = future.result()
                if artifact_data:
                    results.append(artifact_data)
                    
                    # 每处理20条保存一次进度
                    if len(results) % 20 == 0:
                        save_results(results)
                        print(f"已保存 {len(results)} 条记录")
            except Exception as e:
                print(f"❌ 处理失败 {url}: {e}")
    
    # 最终保存
    save_results(results)
    print(f"\n完成! 共抓取 {len(results)} 件文物详细信息")

if __name__ == "__main__":
    scrape_artifacts()