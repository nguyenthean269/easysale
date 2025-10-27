from models import PropertyGroup, TypesUnit, db
from typing import List, Optional
import json


class PropertyService:
    """Service để xử lý các thao tác liên quan đến property groups"""
    
    @staticmethod
    def get_property_tree(root_id: int, db_instance=None) -> str:
        """
        Lấy danh sách tree property groups theo định dạng yêu cầu
        
        Args:
            root_id (int): ID của group root
            db_instance: Database instance để sử dụng (optional)
            
        Returns:
            str: Chuỗi tree theo định dạng:
                - Sapphire 1 (S1) (ID:2)
                - - S1.01 (ID:7)
                - - S1.02 (ID:8)
        """
        try:
            # Sử dụng db_instance nếu được cung cấp, nếu không thì dùng db mặc định
            query_db = db_instance if db_instance else db
            
            # Lấy root group
            root_group = query_db.session.query(PropertyGroup).get(root_id)
            if not root_group:
                return f"Không tìm thấy group với ID: {root_id}"
            
            # Lấy tất cả children của root group
            children = query_db.session.query(PropertyGroup).filter_by(parent_id=root_id).order_by(PropertyGroup.name).all()
            
            if not children:
                return f"- {root_group.name} (ID:{root_id})"
            
            # Xây dựng tree string
            tree_lines = []
            
            # Thêm root group
            tree_lines.append(f"- {root_group.name} (ID:{root_id})")
            
            # Thêm children
            for child in children:
                tree_lines.append(f"- - {child.name} (ID:{child.id})")
                
                # Lấy grandchildren (level 2)
                grandchildren = query_db.session.query(PropertyGroup).filter_by(parent_id=child.id).order_by(PropertyGroup.name).all()
                for grandchild in grandchildren:
                    tree_lines.append(f"- - - {grandchild.name} (ID:{grandchild.id})")
            
            return "\n".join(tree_lines)
            
        except Exception as e:
            return f"Lỗi khi lấy property tree: {str(e)}"
    
    @staticmethod
    def get_property_tree_recursive(root_id: int, max_depth: int = 3, db_instance=None) -> str:
        """
        Lấy danh sách tree property groups với đệ quy (hỗ trợ nhiều level)
        
        Args:
            root_id (int): ID của group root
            max_depth (int): Độ sâu tối đa của tree (mặc định 3)
            db_instance: Database instance để sử dụng (optional)
            
        Returns:
            str: Chuỗi tree theo định dạng
        """
        try:
            # Sử dụng db_instance nếu được cung cấp, nếu không thì dùng db mặc định
            query_db = db_instance if db_instance else db
            
            def build_tree_recursive(group_id: int, depth: int = 0) -> List[str]:
                if depth > max_depth:
                    return []
                
                # Lấy group hiện tại
                group = query_db.session.query(PropertyGroup).get(group_id)
                if not group:
                    return []
                
                lines = []
                indent = "- " * (depth + 1)
                lines.append(f"{indent} {group.name} (ID:{group_id})")
                
                # Lấy children
                children = query_db.session.query(PropertyGroup).filter_by(parent_id=group_id).order_by(PropertyGroup.name).all()
                for child in children:
                    lines.extend(build_tree_recursive(child.id, depth + 1))
                
                return lines
            
            # Bắt đầu từ root
            tree_lines = build_tree_recursive(root_id)
            return "\n".join(tree_lines) if tree_lines else f"Không tìm thấy group với ID: {root_id}"
            
        except Exception as e:
            return f"Lỗi khi lấy property tree: {str(e)}"
    
    @staticmethod
    def get_unit_types_for_prompt(db_instance=None) -> str:
        """
        Lấy danh sách unit types từ database cho prompt
        
        Args:
            db_instance: Database instance để sử dụng (optional)
            
        Returns:
            str: Chuỗi unit types đã format cho prompt
        """
        try:
            # Sử dụng db_instance nếu được cung cấp, nếu không thì dùng db mặc định
            query_db = db_instance if db_instance else db
            
            unit_types = query_db.session.query(TypesUnit).order_by(TypesUnit.name).all()
            
            if not unit_types:
                return "Danh sách các loại căn hộ (unit_type):\n(Không có dữ liệu)"
            
            unit_types_str = "Danh sách các loại căn hộ (unit_type):\n"
            for unit_type in unit_types:
                unit_types_str += f"(ID:{unit_type.id}) {unit_type.name}\n"
            
            return unit_types_str.strip()
            
        except Exception as e:
            return f"Lỗi khi lấy unit types: {str(e)}"
    
    @staticmethod
    def get_property_tree_for_prompt(root_id: int, db_instance=None) -> str:
        """
        Lấy danh sách tree property groups được format sẵn cho prompt
        
        Args:
            root_id (int): ID của group root
            db_instance: Database instance để sử dụng (optional)
            
        Returns:
            str: Chuỗi tree đã được format cho prompt
        """
        tree_content = PropertyService.get_property_tree_recursive(root_id, db_instance=db_instance)
        unit_types_content = PropertyService.get_unit_types_for_prompt(db_instance=db_instance)
        
        if tree_content.startswith("Lỗi") or tree_content.startswith("Không tìm thấy"):
            return tree_content
        
        return f"""<thong-tin-du-an>
Danh sách các phân khu/tòa và id tương ứng:

{tree_content}

{unit_types_content}
</thong-tin-du-an>"""
    
    @staticmethod
    def get_all_property_groups() -> List[dict]:
        """
        Lấy tất cả property groups
        
        Returns:
            List[dict]: Danh sách tất cả property groups
        """
        try:
            groups = PropertyGroup.query.order_by(PropertyGroup.name).all()
            return [group.to_dict() for group in groups]
        except Exception as e:
            return []
    
    @staticmethod
    def get_property_groups_by_parent(parent_id: Optional[int] = None) -> List[dict]:
        """
        Lấy property groups theo parent_id
        
        Args:
            parent_id (Optional[int]): ID của parent group (None để lấy root groups)
            
        Returns:
            List[dict]: Danh sách property groups
        """
        try:
            if parent_id is None:
                groups = PropertyGroup.query.filter_by(parent_id=None).order_by(PropertyGroup.name).all()
            else:
                groups = PropertyGroup.query.filter_by(parent_id=parent_id).order_by(PropertyGroup.name).all()
            
            return [group.to_dict() for group in groups]
        except Exception as e:
            return []
