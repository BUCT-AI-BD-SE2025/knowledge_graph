import pandas as pd

# --------------------------
# 用户配置区（根据需求修改以下参数）
# --------------------------
input_file = r'数据清洗\freer_artifacts_details.csv'         # 输入文件名
output_file = r'freer_pure.csv'       # 输出文件名

# 列合并配置（支持多个合并操作）
# merge_operations = [
#     {
#         'source_columns': ['FirstName', 'LastName'],  # 需要合并的原始列
#         'new_column': 'FullName',                     # 合并后的新列名
#         'separator': ' ',                             # 合并分隔符（默认空格）
#         'keep_source': False                          # 是否保留原始列
#     }
# ]

# 列重命名配置（旧列名: 新列名）
rename_columns = {
    'accession_number': 'ID',
    'title': 'Title',
    'url': 'url',
    'image_url': 'images',
    'culture': 'location',
    'date': 'Period',
    'medium': 'Materials',
    'dimensions': 'Measurements',
    'artist': 'Artist',
    'Description': 'Description',
    'Inscriptions and Colophons': 'Illusion',
    'credit_line': 'Credit Line',

}

# 最终列顺序（必须包含处理后的所有列）
new_column_order = ['ID', 'Title', 'url', 'images',
                    'location', 'Period', 'Materials', 'Measurements', 'Artist',  'Credit Line']

# --------------------------
# 数据处理逻辑
# --------------------------


def process_csv():
    # 读取CSV文件
    try:
        df = pd.read_csv(input_file,
                         #  encoding='cp950',
                         )
    except FileNotFoundError:
        print(f"错误：输入文件 {input_file} 未找到")
        return

    # 处理列合并
    # for operation in merge_operations:
    #     source_cols = operation['source_columns']
    #     new_col = operation['new_column']
    #     sep = operation.get('separator', ' ')
    #     keep_source = operation.get('keep_source', False)

    #     # 检查列是否存在
    #     missing = [col for col in source_cols if col not in df.columns]
    #     if missing:
    #         print(f"错误：合并操作需要的列 {missing} 不存在")
    #         return

    #     # 执行合并
    #     df[new_col] = df[source_cols].apply(
    #         lambda row: sep.join(row.astype(str)),
    #         axis=1
    #     )

    #     # 移除原始列（如果不需要保留）
    #     if not keep_source:
    #         df.drop(columns=source_cols, inplace=True)

    # # 处理列重命名
    try:
        df.rename(columns=rename_columns, inplace=True)
    except KeyError as e:
        print(f"重命名错误：列 {e} 不存在")
        return

    # 验证并设置新列顺序
    missing_cols = [col for col in new_column_order if col not in df.columns]
    extra_cols = [col for col in df.columns if col not in new_column_order]

    if missing_cols:
        print(f"错误：最终列顺序中缺少以下列 {missing_cols}")
        return
    if extra_cols:
        print(f"警告：以下列未包含在最终输出中 {extra_cols}")

    df = df[new_column_order]

    # 保存结果
    df.to_csv(output_file, index=False, encoding='utf_8_sig')
    print(f"文件处理完成，已保存为 {output_file}")


if __name__ == "__main__":
    process_csv()
