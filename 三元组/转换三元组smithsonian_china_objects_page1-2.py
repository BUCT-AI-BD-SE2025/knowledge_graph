import pandas as pd
import csv

# 读取原始 CSV 文件
df = pd.read_csv('smithsonian_china_objects_page1-2.csv')

# 字段对应的谓语
field_map = {
    'accession_number': '编号',
    'credit_line': '捐赠来源',
    'type': '对象类型',
    'date': '制作时间',
    'title': '标题'
}

# 用于指定每个谓语对应的目标节点标签
predicate_to_label = {
    '创作者': 'artist',
    '类别': 'category',
    '捐赠来源': 'donor',
    '文化': 'culture',
    '制作时间': 'date',
    '描述': 'description',
    '题跋': 'inscription',
    '材质': 'material',
    '材料术语': 'glossary',
    '尺寸': 'measurement',
    '对象类型': 'type',
    '时期': 'period',
    '制作地点': 'place',
    '标题': 'title'
}

triples = set()

for _, row in df.iterrows():
    subject = str(row.get('accession_number', '未知编号')).strip()
    for field, predicate in field_map.items():
        if field == 'accession_number':
            continue
        obj = row.get(field)
        if pd.notna(obj):
            obj_str = str(obj).strip().replace('\n', ' ')
            if obj_str.lower() in ['unknown', 'date unknown']:
                continue
            if obj_str:
                obj_label = predicate_to_label.get(predicate, 'Entity')
                triples.add((subject, predicate, obj_str, obj_label))

# 写入增强版 triples CSV
with open('triples_with_labels.csv', mode='w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerow(['Subject', 'Predicate', 'Object', 'ObjectLabel'])
    writer.writerows(triples)

print("✅ 已生成 triples_with_labels.csv，包含目标节点标签信息")
