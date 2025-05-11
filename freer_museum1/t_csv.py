import json
import csv
import os

def json_to_csv(json_file_path, csv_file_path=None):
    """
    将JSON文件转换为CSV文件
    
    参数:
        json_file_path (str): JSON文件的完整路径
        csv_file_path (str, optional): 输出的CSV文件路径。如果未提供，则使用与JSON文件相同的路径，仅更改扩展名
    
    返回:
        str: 生成的CSV文件路径
    """
    try:
        # 检查JSON文件是否存在
        if not os.path.exists(json_file_path):
            raise FileNotFoundError(f"JSON文件不存在: {json_file_path}")
        
        # 读取JSON文件
        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        
        # 检查数据是否有效
        if not data or not isinstance(data, list):
            raise ValueError("JSON数据应该是一个非空列表")
        
        # 设置默认输出路径（如果未提供）
        if csv_file_path is None:
            base_path = os.path.splitext(json_file_path)[0]
            csv_file_path = f"{base_path}.csv"
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(csv_file_path) or '.', exist_ok=True)
        
        # 收集所有可能的字段（保持顺序）
        fieldnames = set()
        for item in data:
            if not isinstance(item, dict):
                raise ValueError("JSON数据中的每个项应该是字典")
            fieldnames.update(item.keys())
        
        # 写入CSV文件（使用utf-8-sig编码避免Excel乱码）
        with open(csv_file_path, 'w', encoding='utf-8-sig', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        print(f"转换成功！CSV文件已保存到: {csv_file_path}")
        return csv_file_path
    
    except json.JSONDecodeError as e:
        print(f"JSON文件解析失败: {str(e)}")
    except Exception as e:
        print(f"转换过程中发生错误: {str(e)}")

# 使用示例
if __name__ == "__main__":
    # 替换为你的实际JSON文件路径
    json_path = r"freer_artifacts_details.json"
    
    # 调用转换函数
    try:
        result_path = json_to_csv(json_path)
        if result_path:
            print(f"转换完成，CSV文件已保存到: {result_path}")
    except Exception as e:
        print(f"程序运行出错: {str(e)}")