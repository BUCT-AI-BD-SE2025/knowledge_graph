import requests
from bs4 import BeautifulSoup
import json
import time


def page_item_links(base_search_url, total_pages=92, museum_name="freer"):
    all_item_urls = []

    # 步骤1：从所有搜索结果页面中提取物品URL
    for page_num in range(0, total_pages):
        url = base_search_url.format(page_num)
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            # 找到所有包含物品信息的div
            # item_divs = soup.find_all(
            #     'div', class_=['search-results-image-grid__result', 'search-results-image-grid__result--clickable'])
            item_divs = soup.find_all(
                'div', class_='search-results-image-grid__result')
            for item_div in item_divs:
                # 找到每个物品的标题链接
                a_tag = item_div.find('a')
                if a_tag:
                    relative_url = a_tag['href']
                    # 构造完整URL
                    full_url = "https://asia.si.edu" + relative_url
                    all_item_urls.append(full_url)
            print(f"已获取第{page_num}页文物")
        else:
            print(f"无法获取第{page_num}页")

    # 去除重复的URL
    all_item_urls = list(set(all_item_urls))
    with open(f'{museum_name}_chinese_artifacts_links_list.json', 'w', encoding='utf-8') as f:
        json.dump(all_item_urls, f, ensure_ascii=False, indent=4)
    print(f"共有：{len(all_item_urls)}件文物")


if __name__ == "__main__":
    museum_name = "freer_museum"
    base_search_url = "https://asia.si.edu/explore-art-culture/collections/search/?listStart={}&edan_fq[]=topic:Chinese+Art"
    page_item_links(base_search_url, total_pages=1168, museum_name=museum_name)
