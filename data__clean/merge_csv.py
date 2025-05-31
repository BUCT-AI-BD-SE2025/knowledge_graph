import pandas as pd
from pathlib import Path


def merge_csv_with_serial(file1, file2, output_file):
    """
    合并两个CSV文件并添加序列号

    参数：
    file1: 第一个CSV文件路径
    file2: 第二个CSV文件路径
    output_file: 输出文件路径
    """

    def read_csv_safe(file_path):
        """带编码自动检测的CSV读取函数"""
        try:
            # 尝试常见中文编码
            return pd.read_csv(file_path, encoding='gb18030')
        except UnicodeDecodeError:
            try:
                return pd.read_csv(file_path, encoding='utf-8-sig')
            except:
                # 最终回退方案
                return pd.read_csv(file_path, engine='python', encoding_errors='replace')

    # 读取两个CSV文件
    df1 = read_csv_safe(file1)
    df2 = read_csv_safe(file2)

    # 合并数据（保留所有列）
    merged_df = pd.concat([df1, df2], axis=0, join='outer')

    # 添加序列号（从1开始）
    merged_df.insert(0, '序列号', range(1, len(merged_df)+1))

    # 处理缺失值（可选显示方式）
    merged_df = merged_df.fillna('')  # 替换NaN为空字符串
    # merged_df = merged_df.fillna('N/A')  # 或者替换为N/A

    # 保存结果（优化Excel兼容性）
    try:
        merged_df.to_csv(output_file,
                         index=False,
                         encoding='utf-8',
                         errors='xmlcharrefreplace')  # 处理特殊字符
        print(f"合并成功！保存至：{Path(output_file).resolve()}")
    except Exception as e:
        print(f"保存失败：{str(e)}")


if __name__ == "__main__":
    # 配置参数
    input_files = [
        r"数据清洗\freer_pure.csv",  # 替换为实际路径
        r"数据清洗\ulberta_pure.csv"   # 第二个文件路径
    ]
    output_path = r"数据清洗\merge_csv\merge_data.csv"  # 输出文件路径

    # 执行合并
    if all(Path(f).exists() for f in input_files):
        merge_csv_with_serial(*input_files, output_path)
    else:
        missing_files = [f for f in input_files if not Path(f).exists()]
        print(f"文件不存在：{missing_files}")
