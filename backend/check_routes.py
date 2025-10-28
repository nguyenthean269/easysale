#!/usr/bin/env python3
"""
Check registered routes in Flask app
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_routes():
    """Kiểm tra các routes đã được đăng ký"""
    try:
        from app import app
        
        print("=== REGISTERED ROUTES ===\n")
        
        # Lấy tất cả routes
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods),
                'rule': rule.rule
            })
        
        # Sort theo rule
        routes.sort(key=lambda x: x['rule'])
        
        # Filter các routes liên quan đến zalo-test và warehouse
        relevant_routes = [r for r in routes if 'zalo-test' in r['rule'] or 'warehouse' in r['rule'] or 'zalo-processor' in r['rule']]
        
        print("Zalo Test & Warehouse Related Routes:")
        for route in relevant_routes:
            print(f"  {route['rule']} [{', '.join(route['methods'])}] -> {route['endpoint']}")
        
        print(f"\nTotal routes found: {len(routes)}")
        print(f"Relevant routes: {len(relevant_routes)}")
        
        # Kiểm tra cụ thể các routes bị 404
        missing_routes = [
            '/api/zalo-test/processor-status',
            '/api/zalo-test/unprocessed-messages',
            '/api/zalo-test/property-tree'
        ]
        
        print("\nChecking for missing routes:")
        for missing_route in missing_routes:
            found = any(missing_route in route['rule'] for route in routes)
            print(f"  {missing_route}: {'✅ Found' if found else '❌ Missing'}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_routes()
