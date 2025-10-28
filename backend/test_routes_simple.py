#!/usr/bin/env python3
"""
Simple test để kiểm tra routes
"""

def test_routes():
    """Test routes mà không import toàn bộ app"""
    try:
        print("Testing routes...")
        
        # Test import blueprint
        from routes.zalo_test import zalo_test_bp
        print(f"✅ zalo_test_bp imported: {zalo_test_bp.name}")
        
        from routes.warehouse import warehouse_bp  
        print(f"✅ warehouse_bp imported: {warehouse_bp.name}")
        
        # Test tạo app đơn giản
        from flask import Flask
        test_app = Flask(__name__)
        
        # Register blueprints
        test_app.register_blueprint(zalo_test_bp, url_prefix='/api/zalo-test')
        test_app.register_blueprint(warehouse_bp, url_prefix='/warehouse')
        
        print("✅ Blueprints registered")
        
        # Check routes
        routes = list(test_app.url_map.iter_rules())
        print(f"Total routes: {len(routes)}")
        
        zalo_routes = [r.rule for r in routes if 'zalo-test' in r.rule]
        warehouse_routes = [r.rule for r in routes if 'warehouse' in r.rule]
        
        print(f"Zalo-test routes: {zalo_routes}")
        print(f"Warehouse routes: {warehouse_routes}")
        
        # Check specific missing routes
        missing_routes = [
            '/api/zalo-test/processor-status',
            '/api/zalo-test/unprocessed-messages', 
            '/api/zalo-test/property-tree'
        ]
        
        print("\nChecking missing routes:")
        for missing_route in missing_routes:
            found = any(missing_route in route.rule for route in routes)
            print(f"  {missing_route}: {'✅ Found' if found else '❌ Missing'}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_routes()
