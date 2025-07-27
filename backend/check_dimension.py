#!/usr/bin/env python3
"""
Script kiểm tra dimension của embedding model - Hỗ trợ tiếng Việt
"""

import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

# Load environment
load_dotenv()

def check_embedding_dimensions():
    """Kiểm tra dimension của các embedding model hỗ trợ tiếng Việt"""
    
    print("🔍 Checking embedding model dimensions for Vietnamese support...")
    print("="*60)
    
    # Danh sách các model hỗ trợ tiếng Việt tốt
    models = [
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",  # Tốt nhất cho tiếng Việt
        "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",   # Chính xác hơn nhưng chậm
        "sentence-transformers/all-MiniLM-L6-v2",                       # Nhanh nhưng ít hỗ trợ tiếng Việt
        "sentence-transformers/all-mpnet-base-v2",                      # Chính xác nhưng không đa ngôn ngữ
        "sentence-transformers/distiluse-base-multilingual-cased-v2"    # Universal Sentence Encoder
    ]
    
    # Test với cả tiếng Anh và tiếng Việt
    test_texts = [
        "This is a test sentence in English.",
        "Đây là một câu thử nghiệm bằng tiếng Việt.",
        "Machine learning algorithms are powerful.",
        "Thuật toán học máy rất mạnh mẽ.",
        "Artificial intelligence and natural language processing.",
        "Trí tuệ nhân tạo và xử lý ngôn ngữ tự nhiên."
    ]
    
    for model_name in models:
        try:
            print(f"\n🤖 Testing model: {model_name}")
            
            # Load model
            model = SentenceTransformer(model_name)
            
            # Test với text đầu tiên
            embedding = model.encode(test_texts[0])
            dimension = len(embedding)
            
            print(f"  📏 Dimension: {dimension}")
            print(f"  📊 Sample values: {embedding[:5]}")
            
            # Test với tiếng Việt
            vi_embedding = model.encode(test_texts[1])
            print(f"  🇻🇳 Vietnamese test: {vi_embedding[:5]}")
            
            # So sánh với cấu hình hiện tại
            config_dim = int(os.getenv('MILVUS_DIMENSION', '384'))
            if dimension == config_dim:
                print(f"  ✅ Matches config dimension ({config_dim})")
            else:
                print(f"  ❌ Mismatch! Config: {config_dim}, Model: {dimension}")
                
        except Exception as e:
            print(f"  ❌ Error loading model: {e}")
    
    print(f"\n📋 Current configuration:")
    print(f"  MILVUS_DIMENSION: {os.getenv('MILVUS_DIMENSION', '384')}")
    print(f"  EMBEDDING_MODEL: {os.getenv('EMBEDDING_MODEL', 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')}")

def test_vietnamese_similarity():
    """Test similarity giữa các câu tiếng Việt"""
    print(f"\n🇻🇳 Testing Vietnamese similarity...")
    print("="*60)
    
    try:
        model_name = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        model = SentenceTransformer(model_name)
        
        # Test sentences
        sentences = [
            "Học máy là một nhánh của trí tuệ nhân tạo",
            "Machine learning is a branch of artificial intelligence",
            "Thuật toán học máy rất quan trọng",
            "Machine learning algorithms are very important",
            "Xử lý ngôn ngữ tự nhiên",
            "Natural language processing"
        ]
        
        # Tạo embeddings
        embeddings = model.encode(sentences)
        
        # Tính similarity
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np
        
        similarity_matrix = cosine_similarity(embeddings)
        
        print("📊 Similarity Matrix:")
        for i, sent1 in enumerate(sentences):
            for j, sent2 in enumerate(sentences):
                if i < j:  # Chỉ in nửa trên của matrix
                    sim = similarity_matrix[i][j]
                    print(f"  '{sent1[:30]}...' vs '{sent2[:30]}...': {sim:.3f}")
                    
    except Exception as e:
        print(f"❌ Error testing Vietnamese similarity: {e}")

def recommend_model():
    """Đề xuất model phù hợp cho tiếng Việt"""
    print(f"\n💡 Recommendations for Vietnamese:")
    print("="*60)
    
    print("1. 🥇 BEST for Vietnamese (Recommended):")
    print("   MILVUS_DIMENSION=384")
    print("   EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    print("   ✅ Hỗ trợ 50+ ngôn ngữ, bao gồm tiếng Việt")
    print("   ✅ Nhanh và hiệu quả")
    print("   ✅ Được train trên dữ liệu đa ngôn ngữ")
    
    print("\n2. 🥈 Better accuracy but slower:")
    print("   MILVUS_DIMENSION=768")
    print("   EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-mpnet-base-v2")
    print("   ✅ Chính xác hơn nhưng chậm hơn")
    print("   ✅ Hỗ trợ tiếng Việt tốt")
    
    print("\n3. 🥉 Universal Sentence Encoder:")
    print("   MILVUS_DIMENSION=512")
    print("   EMBEDDING_MODEL=sentence-transformers/distiluse-base-multilingual-cased-v2")
    print("   ✅ Được Google phát triển")
    print("   ✅ Hỗ trợ 16 ngôn ngữ chính")
    
    print("\n4. ⚠️ NOT recommended for Vietnamese:")
    print("   - all-MiniLM-L6-v2 (chỉ hỗ trợ tiếng Anh tốt)")
    print("   - all-mpnet-base-v2 (không đa ngôn ngữ)")

def show_vietnamese_examples():
    """Hiển thị ví dụ sử dụng tiếng Việt"""
    print(f"\n📝 Vietnamese Usage Examples:")
    print("="*60)
    
    examples = [
        {
            "query": "học máy",
            "expected_results": ["machine learning", "thuật toán học máy", "AI algorithms"]
        },
        {
            "query": "xử lý ngôn ngữ tự nhiên", 
            "expected_results": ["natural language processing", "NLP", "text analysis"]
        },
        {
            "query": "trí tuệ nhân tạo",
            "expected_results": ["artificial intelligence", "AI", "machine intelligence"]
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. Query: '{example['query']}'")
        print(f"   Expected similar results:")
        for result in example['expected_results']:
            print(f"   - {result}")

if __name__ == "__main__":
    check_embedding_dimensions()
    test_vietnamese_similarity()
    recommend_model()
    show_vietnamese_examples() 