"""
MongoDB Database Connection using pymongo
Synchronous connection (no motor, no async)
Used for storing raw scraped data
"""

import os
import sys

# CRITICAL FIX for Python 3.12 + OpenSSL 3.x + Windows
# Must be set BEFORE importing pymongo
os.environ['OPENSSL_CONF'] = ''

# Try to enable OpenSSL legacy provider for older TLS versions
try:
    import ssl
    # Create a custom SSL context that allows legacy protocols
    ssl._create_default_https_context = ssl._create_unverified_context
except Exception:
    pass

import certifi
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Global MongoDB client variable
mongo_client = None
mongo_db = None


def connect_mongodb():
    """
    Connect to MongoDB Atlas.
    
    This function creates a connection to MongoDB and tests it.
    Should be called once when the FastAPI app starts.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    global mongo_client, mongo_db
    
    try:
        # Get MongoDB URI from environment variables
        mongodb_uri = os.getenv("MONGODB_URI")
        
        if not mongodb_uri:
            print("MONGODB_URI not found in environment variables")
            return False
        
        # Create MongoDB client
        # serverSelectionTimeoutMS: How long to wait for server connection (5 seconds)
        # tlsAllowInvalidCertificates: Required workaround for Python 3.12 + OpenSSL 3.x
        mongo_client = MongoClient(
            mongodb_uri,
            serverSelectionTimeoutMS=5000,
            tlsAllowInvalidCertificates=True
        )
        
        # Connect to the database
        # Database name: pricepilot_raw (stores raw scraped data)
        mongo_db = mongo_client["pricepilot_raw"]
        
        # Test the connection by pinging the server
        # This forces an actual connection attempt
        mongo_client.admin.command('ping')
        
        print("MongoDB connected successfully")
        print(f"   Database: pricepilot_raw")
        print(f"   Collection: raw_products")
        return True
        
    except ConnectionFailure as e:
        print(f"MongoDB connection failed: {e}")
        return False
    except ServerSelectionTimeoutError as e:
        print(f"MongoDB connection timeout: {e}")
        return False
    except Exception as e:
        print(f"MongoDB connection error: {e}")
        return False


def close_mongodb():
    """
    Close the MongoDB connection.
    
    This function should be called when the FastAPI app shuts down
    to properly close the database connection.
    """
    global mongo_client
    
    if mongo_client:
        mongo_client.close()
        print("MongoDB connection closed")


def get_raw_products_collection():
    """
    Get the raw_products collection from MongoDB.
    
    This collection stores raw HTML and data scraped from e-commerce websites.
    
    Returns:
        pymongo.collection.Collection: The raw_products collection
    
    Raises:
        RuntimeError: If MongoDB is not connected
    
    Usage:
        collection = get_raw_products_collection()
        collection.insert_one({"url": "...", "html": "...", "scraped_at": "..."})
    """
    global mongo_db
    
    if mongo_db is None:
        raise RuntimeError("MongoDB not connected. Call connect_mongodb() first.")
    
    # Return the raw_products collection
    # Collections in MongoDB are like tables in SQL databases
    return mongo_db["raw_products"]


# Example safe query functions

def example_safe_insert(product_data: dict):
    """
    ✅ SAFE: Insert data using pymongo's built-in methods
    
    pymongo automatically handles data sanitization, so this is safe.
    """
    collection = get_raw_products_collection()
    result = collection.insert_one(product_data)
    return result.inserted_id


def example_safe_find(product_url: str):
    """
    ✅ SAFE: Find documents using pymongo's query operators
    
    Using dictionary queries is safe because pymongo handles the data properly.
    """
    collection = get_raw_products_collection()
    result = collection.find_one({"url": product_url})
    return result


def example_safe_update(product_url: str, new_data: dict):
    """
    ✅ SAFE: Update documents using pymongo's operators
    
    Using $set operator ensures safe updates.
    """
    collection = get_raw_products_collection()
    result = collection.update_one(
        {"url": product_url},  # Filter
        {"$set": new_data}     # Update using $set operator
    )
    return result.modified_count


def example_safe_delete(product_url: str):
    """
    ✅ SAFE: Delete documents using pymongo's methods
    """
    collection = get_raw_products_collection()
    result = collection.delete_one({"url": product_url})
    return result.deleted_count


# Common MongoDB operations

def insert_raw_product(product_data: dict):
    """
    Insert a raw scraped product into MongoDB.
    
    Args:
        product_data: Dictionary containing scraped data
            Example: {
                "url": "https://example.com/product",
                "html": "<html>...</html>",
                "scraped_at": "2024-01-01T12:00:00",
                "source": "example.com"
            }
    
    Returns:
        ObjectId: The ID of the inserted document
    """
    collection = get_raw_products_collection()
    result = collection.insert_one(product_data)
    return result.inserted_id


def find_raw_product_by_url(url: str):
    """
    Find a raw product by its URL.
    
    Args:
        url: The product URL to search for
    
    Returns:
        dict: The product document, or None if not found
    """
    collection = get_raw_products_collection()
    return collection.find_one({"url": url})


def find_all_raw_products(limit: int = 100):
    """
    Find all raw products (with limit).
    
    Args:
        limit: Maximum number of documents to return
    
    Returns:
        list: List of product documents
    """
    collection = get_raw_products_collection()
    return list(collection.find().limit(limit))


def update_raw_product(url: str, updated_data: dict):
    """
    Update a raw product by URL.
    
    Args:
        url: The product URL to update
        updated_data: Dictionary of fields to update
    
    Returns:
        int: Number of documents modified
    """
    collection = get_raw_products_collection()
    result = collection.update_one(
        {"url": url},
        {"$set": updated_data}
    )
    return result.modified_count


def delete_raw_product(url: str):
    """
    Delete a raw product by URL.
    
    Args:
        url: The product URL to delete
    
    Returns:
        int: Number of documents deleted
    """
    collection = get_raw_products_collection()
    result = collection.delete_one({"url": url})
    return result.deleted_count


# ============================================================================
# EXPLANATION FOR VIVA
# ============================================================================

"""
Q: What is MongoDB used for in this project?
A: MongoDB stores raw scraped data from e-commerce websites. When we scrape 
   a product page, we save the entire HTML and raw data in MongoDB before 
   processing it. This gives us a backup of the original data.

Q: Why store raw scraped data separately from PostgreSQL?
A: 
   1. Different data types:
      - PostgreSQL: Structured data (clean product info, prices, users)
      - MongoDB: Unstructured data (raw HTML, messy scraped data)
   
   2. Flexibility:
      - MongoDB is schema-less, so we can store any format of scraped data
      - PostgreSQL requires a fixed schema (defined columns)
   
   3. Performance:
      - MongoDB is faster for storing large text/HTML documents
      - PostgreSQL is faster for structured queries and relationships
   
   4. Workflow:
      - Step 1: Scrape website → Store raw HTML in MongoDB
      - Step 2: Process HTML → Extract clean data
      - Step 3: Store clean data in PostgreSQL → Use in app

Q: How does pymongo connect to MongoDB?
A: 
   1. We provide a connection string (MONGODB_URI) from MongoDB Atlas
   2. pymongo creates a MongoClient using this connection string
   3. The client connects to the database (pricepilot_raw)
   4. We access collections (raw_products) through the database
   5. We can then insert, find, update, or delete documents

Q: What is a collection vs a database?
A: 
   - Database: Like a folder that contains multiple collections
     Example: pricepilot_raw (our database)
   
   - Collection: Like a table in SQL, stores related documents
     Example: raw_products (stores scraped product data)
   
   Analogy:
   - Database = School
   - Collection = Classroom
   - Document = Student
   
   In our project:
   - Database: pricepilot_raw
   - Collection: raw_products
   - Document: One scraped product (HTML, URL, timestamp, etc.)

Q: Why use pymongo instead of motor?
A: 
   - pymongo: Synchronous (blocking) - simpler, easier to understand
   - motor: Asynchronous (non-blocking) - more complex, better performance
   
   For this project, pymongo is sufficient because:
   1. Scraping happens in background tasks (not during user requests)
   2. Simpler code is easier to maintain and explain
   3. Performance difference is minimal for our use case
"""
