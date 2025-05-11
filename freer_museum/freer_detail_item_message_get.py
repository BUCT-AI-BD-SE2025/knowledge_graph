import requests
from bs4 import BeautifulSoup
import json
import time
import csv
from urllib.parse import urljoin


def clean_field_value(field_name, value):
    """字段值清洗函数"""
    if not value:
        return None
    # 特殊处理维度字段
    if field_name == 'Dimension':
        return value.split('(')[0].strip()
    # 处理EDAN ID的特殊格式
    if field_name == 'EDAN_ID':
        return value.replace('edanmdm:', '').strip()
    return value.strip()


def get_metadata(attributes_div):
    """提取标准化元数据"""
    metadata = {}
    if not attributes_div:
        return metadata

    field_mapping = {
        'Period': 'period',
        'Geography': 'origin',
        'Material': 'material',
        'Dimension': 'dimensions',
        'Accession_Number': 'accession_number',
        'EDAN_ID': 'edan_id'
    }

    for li in attributes_div.find_all('li'):
        label_tag = li.find(
            'h3', class_='individual-object-at-a-glance__attributes-label')
        value_div = li.find(
            'div', class_='individual-object-at-a-glance__attributes-value')

        if not label_tag or not value_div:
            continue

        raw_name = label_tag.get_text(strip=True)
        field_name = field_mapping.get(
            raw_name, raw_name.lower().replace(' ', '_'))
        raw_value = value_div.get_text(strip=True)

        metadata[field_name] = clean_field_value(field_name, raw_value)

    return metadata


def get_iiif_images(soup):
    """生成IIIF标准图片链接"""
    image_container = soup.find('div', {'id': 'openseadragonViewer'})
    image_ids = []

    if image_container and image_container.has_attr('data-image-ids'):
        raw_ids = image_container['data-image-ids'].strip()
        # 处理可能的多个ID（逗号分隔）
        image_ids = [img_id.strip()
                     for img_id in raw_ids.split(',') if img_id.strip()]

    # IIIF图片服务模板
    iiif_template = "https://ids.si.edu/ids/iiif/{image_id}/full/full/0/default.jpg"

    return [iiif_template.format(image_id=img_id) for img_id in image_ids]


def detail_message_get(all_item_urls, museum_name="freer"):
    all_artifacts = []
    request_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    for index, item_url in enumerate(all_item_urls, 1):
        try:
            # 发送请求
            response = requests.get(
                item_url, headers=request_headers, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # 提取元数据
            attributes_div = soup.find(
                'div', class_='individual-object-at-a-glance__attributes')
            metadata = get_metadata(attributes_div)

            # 提取图片链接
            image_links = get_iiif_images(soup)

            # 构建数据记录
            artifact = {
                'url': item_url,
                **metadata,
                'images': '|'.join(image_links) if image_links else None
            }

            all_artifacts.append(artifact)
            print(f"处理进度：{index}/{len(all_item_urls)}")

        except requests.exceptions.RequestException as e:
            print(f"请求失败：{item_url} - {str(e)}")
        except Exception as e:
            print(f"处理异常：{item_url} - {str(e)}")

        # 遵守爬虫礼仪
        time.sleep(0.3)

    # 生成CSV文件
    if all_artifacts:
        # 自动收集所有字段
        fieldnames = set()
        for artifact in all_artifacts:
            fieldnames.update(artifact.keys())

        # 固定字段顺序
        ordered_fields = ['url', 'edan_id', 'accession_number', 'period', 'origin',
                          'material', 'dimensions', 'images']
        extra_fields = sorted(fieldnames - set(ordered_fields))
        fieldnames = ordered_fields + extra_fields

        with open(f'{museum_name}_collection.csv', 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            success_count = 0
            for artifact in all_artifacts:
                try:
                    writer.writerow(artifact)
                    success_count += 1
                except ValueError as e:
                    print(f"记录写入失败：{artifact.get('url')} - {str(e)}")

            print(
                f"保存完成：成功 {success_count} 条，失败 {len(all_artifacts)-success_count} 条")

    return all_artifacts


if __name__ == "__main__":
    # 示例用法
    museum_name = "freer_gallery"

    # 从JSON文件加载URL列表
    with open(r'freer_museum\freer_museum_links.json', 'r', encoding='utf-8') as f:
        item_urls = json.load(f)

    # 运行爬虫（测试时限制为5个URL）
    detail_message_get(item_urls[:2], museum_name=museum_name)

    # # 可选：保存完整结果到JSON
    # with open(f'{museum_name}_full_data.json', 'w', encoding='utf-8') as f:
    #     json.dump(results, f, ensure_ascii=False, indent=2)
