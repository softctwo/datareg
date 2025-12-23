"""
数据导出工具
作者：张彦龙
"""
from typing import List, Dict, Any
from datetime import datetime
import json
import csv
import io


class ExportService:
    """数据导出服务"""
    
    @staticmethod
    def export_to_csv(data: List[Dict[str, Any]], filename: str = None) -> tuple:
        """导出为CSV格式"""
        if not data:
            return "", "export_empty.csv"
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        
        csv_content = output.getvalue()
        output.close()
        
        if not filename:
            filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return csv_content, filename
    
    @staticmethod
    def export_to_json(data: List[Dict[str, Any]], filename: str = None) -> tuple:
        """导出为JSON格式"""
        json_content = json.dumps(data, ensure_ascii=False, indent=2, default=str)
        
        if not filename:
            filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        return json_content, filename
    
    @staticmethod
    def format_data_for_export(data: List[Any], fields: List[str] = None) -> List[Dict[str, Any]]:
        """格式化数据用于导出"""
        if not data:
            return []
        
        formatted = []
        for item in data:
            if hasattr(item, '__dict__'):
                # SQLAlchemy模型对象
                item_dict = {}
                for key, value in item.__dict__.items():
                    if not key.startswith('_'):
                        if fields is None or key in fields:
                            # 处理日期时间
                            if isinstance(value, datetime):
                                item_dict[key] = value.strftime('%Y-%m-%d %H:%M:%S')
                            else:
                                item_dict[key] = value
                formatted.append(item_dict)
            elif isinstance(item, dict):
                # 字典对象
                if fields:
                    formatted.append({k: v for k, v in item.items() if k in fields})
                else:
                    formatted.append(item)
        
        return formatted

