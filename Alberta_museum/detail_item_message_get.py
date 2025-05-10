import requests
from bs4 import BeautifulSoup
import json
import time


def detail_message_get(all_item_urls, museum_name="ualberta"):

    # 步骤2：获取每个物品的详细信息
    all_artifacts = []
    count_num = 1
    for item_url in all_item_urls:
        response = requests.get(item_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            # 初始化字典来存储物品详情
            details = {}
            # 找到所有spec-field元素
            spec_fields = soup.find_all('span', class_='spec-field')
            for field in spec_fields:
                # 获取字段名称（在<b>标签中）
                field_name_tag = field.find('b')
                if field_name_tag:
                    field_name = field_name_tag.text.strip()
                    # 获取字段值（在下一个<span>标签中）
                    field_value_tag = field.find('span')
                    if field_value_tag.text.strip():
                        # 如果是Description，可能包含div
                        if field_name == 'Description':
                            full_desc = field_value_tag.find(
                                'div', class_='full-length-field')
                            truncated_desc = field_value_tag.find(
                                'div', class_='truncated-field')
                            field_value = full_desc.text.strip() if full_desc else (
                                truncated_desc.text.strip() if truncated_desc else field_value_tag.text.strip())
                        else:
                            field_value = field_value_tag.text.strip()
                        details[field_name] = field_value
            image_url_fields = soup.find_all('div', class_="image-display")
            for url in image_url_fields:
                image_url = url.find('a')['data-largest']

                # image_url = image_url['src']
                if image_url:
                    detail_image_link = image_url.strip()

    # 存储物品信息
            artifact = {
                'url': item_url,
                'details': details,
                'images': detail_image_link
            }
            all_artifacts.append(artifact)
            print(f"第{count_num}/1930已完成")
            count_num += 1

        else:
            print(f"无法获取 {item_url}")
        # 添加延迟以避免服务器限制
        time.sleep(0.3)

    # 步骤3：将数据保存到JSON文件
    with open(f'{museum_name}_chinese_artifacts.json', 'w', encoding='utf-8') as f:
        json.dump(all_artifacts, f, ensure_ascii=False, indent=4)

    print("爬取完成。数据已保存到 'chinese_artifacts.json'。")


if __name__ == "__main__":
    museum_name = "ualberta"
    link_URL = 'ualberta_chinese_artifacts_links_list.json'
    base_search_url = "https://search.museums.ualberta.ca/search?keywords=chinese&items_sort=relevance&items_view=list&items_per_page=21&items_page_num={}&item_groups_sort=relevance&item_groups_view=list&item_groups_per_page=21&type_view=items"
    with open(r"alberta museum\ualberta_chinese_artifacts_links_list.json", 'r+', encoding='utf-8') as f:
        link_list = json.load(f)

    detail_message_get(link_list, museum_name=museum_name)
