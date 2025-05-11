import requests
from bs4 import BeautifulSoup
import json
import time
import urllib3

# 禁用SSL警告（可选）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


def page_item_links(base_search_url, total_pages=92, museum_name="freer"):
    all_item_urls = []

    # 配置重试策略
    session = requests.Session()
    retries = urllib3.util.retry.Retry(
        total=5,
        backoff_factor=0.3,
        status_forcelist=[500, 502, 503, 504]
    )
    session.mount(
        'https://', requests.adapters.HTTPAdapter(max_retries=retries))

    for page_num in range(0, total_pages + 1):
        url = base_search_url.format(page_num)
        try:
            # 解决方案1：禁用SSL验证（快速解决方法）
            response = session.get(
                url,
                headers=headers,
                verify=False,  # 关闭SSL验证
                timeout=30
            )

            # 解决方案2：使用系统证书（备用方案）
            # response = session.get(
            #     url,
            #     headers=headers,
            #     verify='/path/to/cert.pem'  # 或使用certifi.where()
            # )

            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # 优化选择器
            list_items = soup.find_all(
                'li', class_='search-results-image-grid__result-container')
            if not list_items:
                item_divs = soup.find_all(
                    'div', class_='search-results-image-grid__result')
            else:
                item_divs = [
                    li.find('div', class_='search-results-image-grid__result') for li in list_items]

            for item_div in item_divs:
                if item_div:  # 防止空元素
                    a_tag = item_div.find('a', class_='secondary-link')
                    if a_tag and 'href' in a_tag.attrs:
                        full_url = f"https://asia.si.edu{a_tag['href']}"
                        all_item_urls.append(full_url)

            print(f"✅ 第 {page_num} 页完成，找到 {len(item_divs)} 个条目")
            time.sleep(0.3)  # 增加间隔时间

        except Exception as e:
            print(f"❌ 第 {page_num} 页失败: {str(e)}")
            continue

    # 去重保存
    unique_urls = list(set(all_item_urls))
    with open(f'{museum_name}_links.json', 'w', encoding='utf-8') as f:
        json.dump(unique_urls, f, ensure_ascii=False, indent=4)

    print(f"🎉 完成！共找到 {len(unique_urls)} 个唯一链接")


if __name__ == "__main__":
    museum_name = "freer_museum"
    base_search_url = "https://asia.si.edu/explore-art-culture/collections/search/?listStart={}&edan_fq[]=topic:Chinese+Art"

    # 建议先测试少量页面
    page_item_links(
        base_search_url,
        total_pages=1168,  # 先用3页测试
        museum_name=museum_name
    )
