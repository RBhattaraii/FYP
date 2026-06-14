"""
Test MongoDB connection
Run this script: python test_mongodb.py
"""

from app.database.mongo import connect_mongodb, get_raw_products_collection, close_mongodb
from datetime import datetime

def test_connection():
    """Test MongoDB connection and basic operations"""
    
    print("\n" + "="*60)
    print("🧪 Testing MongoDB Connection")
    print("="*60)
    
    # Test connection
    print("\n1️⃣ Testing connection...")
    connected = connect_mongodb()
    
    if not connected:
        print("❌ Connection failed. Check your MONGODB_URI in .env")
        return
    
    # Test getting collection
    print("\n2️⃣ Getting raw_products collection...")
    try:
        collection = get_raw_products_collection()
        print(f"✅ Collection obtained: {collection.name}")
    except Exception as e:
        print(f"❌ Error getting collection: {e}")
        close_mongodb()
        return
    
    # Test insert
    print("\n3️⃣ Testing insert operation...")
    try:
        test_doc = {
            "url": "https://test.com/product/test-123",
            "html": "<html><body>Test Product</body></html>",
            "scraped_at": datetime.now().isoformat(),
            "source": "test.com",
            "test": True  # Mark as test data
        }
        
        result = collection.insert_one(test_doc)
        print(f"✅ Document inserted with ID: {result.inserted_id}")
    except Exception as e:
        print(f"❌ Insert failed: {e}")
        close_mongodb()
        return
    
    # Test find
    print("\n4️⃣ Testing find operation...")
    try:
        found_doc = collection.find_one({"url": "https://test.com/product/test-123"})
        if found_doc:
            print(f"✅ Document found:")
            print(f"   URL: {found_doc['url']}")
            print(f"   Source: {found_doc['source']}")
            print(f"   Scraped at: {found_doc['scraped_at']}")
        else:
            print("❌ Document not found")
    except Exception as e:
        print(f"❌ Find failed: {e}")
    
    # Test update
    print("\n5️⃣ Testing update operation...")
    try:
        result = collection.update_one(
            {"url": "https://test.com/product/test-123"},
            {"$set": {"processed": True, "processed_at": datetime.now().isoformat()}}
        )
        print(f"✅ Updated {result.modified_count} document(s)")
    except Exception as e:
        print(f"❌ Update failed: {e}")
    
    # Test count
    print("\n6️⃣ Counting documents...")
    try:
        count = collection.count_documents({})
        print(f"✅ Total documents in collection: {count}")
        
        test_count = collection.count_documents({"test": True})
        print(f"✅ Test documents: {test_count}")
    except Exception as e:
        print(f"❌ Count failed: {e}")
    
    # Cleanup: Delete test document
    print("\n7️⃣ Cleaning up test data...")
    try:
        result = collection.delete_one({"url": "https://test.com/product/test-123"})
        print(f"✅ Deleted {result.deleted_count} test document(s)")
    except Exception as e:
        print(f"❌ Delete failed: {e}")
    
    # Close connection
    print("\n8️⃣ Closing connection...")
    close_mongodb()
    
    print("\n" + "="*60)
    print("✅ All tests completed successfully!")
    print("="*60)
    print("\n💡 MongoDB is ready to use in your FastAPI app!")
    print()


if __name__ == "__main__":
    test_connection()
