import requests
from bs4 import BeautifulSoup
import json
import csv
import os
import time


def detail_message_get(all_item_urls, museum_name="ualberta"):
    all_artifacts = []
    count_num = 1

    # 单次爬取
    for item_url in all_item_urls:
        response = requests.get(item_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            details = {}

            # 解析详情字段
            spec_fields = soup.find_all('span', class_='spec-field')
            for field in spec_fields:
                field_name_tag = field.find('b')
                if field_name_tag:
                    field_name = field_name_tag.text.strip()
                    field_value_tag = field.find('span')
                    if field_value_tag.text.strip():
                        if field_name == 'Description':
                            full_desc = field_value_tag.find('div', class_='full-length-field')
                            truncated_desc = field_value_tag.find('div', class_='truncated-field')
                            field_value = full_desc.text.strip() if full_desc else (
                                truncated_desc.text.strip() if truncated_desc else field_value_tag.text.strip())
                        else:
                            field_value = field_value_tag.text.strip()
                        details[field_name] = field_value

            # 获取图片链接
            image_url_fields = soup.find_all('div', class_="image-display")
            detail_image_link = None
            for url in image_url_fields:
                if url.find('a'):
                    detail_image_link = url.find('a').get('data-largest', '').strip()

            # 存储数据（平铺details字段）
            artifact = {'url': item_url, **details, 'image_url': detail_image_link}
            all_artifacts.append(artifact)
            print(f"第{count_num}/{len(all_item_urls)}已完成")
            count_num += 1
        else:
            print(f"无法获取 {item_url}")
        time.sleep(0.3)

    # 保存JSON和CSV（使用同一份数据）
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # 1. 保存JSON
    json_path = os.path.join(output_dir, f'{museum_name}_chinese_artifacts.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(all_artifacts, f, ensure_ascii=False, indent=4)

    # 2. 保存CSV
    if all_artifacts:
        csv_path = os.path.join(output_dir, f'{museum_name}_chinese_artifacts.csv')
        fieldnames = set().union(*(artifact.keys() for artifact in all_artifacts))

        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=sorted(fieldnames))
            writer.writeheader()
            writer.writerows(all_artifacts)
        print(f"数据已保存到: {json_path} 和 {csv_path}")
    else:
        print("无有效数据可保存")


if __name__ == "__main__":
    with open('ualberta_chinese_artifacts_links_list.json', 'r', encoding='utf-8') as f:
        link_list = json.load(f)
    detail_message_get(link_list, museum_name="ualberta")