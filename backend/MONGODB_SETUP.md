# MongoDB Setup Documentation

## ✅ What We Have

### Files Created:
- `backend/app/database/mongo.py` - MongoDB connection module
- Updated `backend/main.py` - MongoDB initialization on startup

### Configuration:
- **Database**: `pricepilot_raw`
- **Collection**: `raw_products`
- **Connection**: MongoDB Atlas (cloud)
- **Driver**: `pymongo[srv]` (synchronous, no async)

---

## 🎯 What MongoDB is Used For

MongoDB stores **raw scraped data** from e-commerce websites:

1. **Raw HTML** - Complete webpage HTML before processing
2. **Scraped metadata** - URL, timestamp, source website
3. **Unprocessed data** - Product info before cleaning
4. **Backup data** - Original data in case we need to re-process

### Workflow:
```
Step 1: Scrape website
   ↓
Step 2: Store raw HTML in MongoDB (pricepilot_raw database)
   ↓
Step 3: Process and extract clean data
   ↓
Step 4: Store clean data in PostgreSQL (users, products tables)
   ↓
Step 5: Mobile app uses clean data from PostgreSQL
```

---

## 🔄 Why Two Databases?

### PostgreSQL (Structured Data):
- **What**: Clean, organized data
- **Examples**: User accounts, product info, prices
- **Why**: Fast queries, relationships between tables
- **Schema**: Fixed structure (defined columns)

### MongoDB (Unstructured Data):
- **What**: Raw, messy data
- **Examples**: HTML pages, scraped text, JSON responses
- **Why**: Flexible storage, no fixed structure needed
- **Schema**: Schema-less (any format allowed)

### Analogy:
- **PostgreSQL** = Filing cabinet with labeled folders (organized)
- **MongoDB** = Storage box where you throw everything (flexible)

---

## 📚 Database vs Collection

### Database:
- Like a **folder** that contains multiple collections
- Our database: `pricepilot_raw`

### Collection:
- Like a **table** in SQL
- Stores related documents
- Our collection: `raw_products`

### Document:
- Like a **row** in SQL
- One piece of data (one scraped product)

### Visual Structure:
```
MongoDB Server (Atlas)
└── pricepilot_raw (Database)
    └── raw_products (Collection)
        ├── Document 1 (Product from Amazon)
        ├── Document 2 (Product from Daraz)
        └── Document 3 (Product from Sastodeal)
```

### School Analogy:
- **Database** = School building
- **Collection** = Classroom
- **Document** = Student

---

## 🔌 How pymongo Connects

### Step-by-Step Connection:

1. **Get connection string** from `.env` file:
   ```
   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/...
   ```

2. **Create MongoClient**:
   ```python
   mongo_client = MongoClient(mongodb_uri)
   ```

3. **Select database**:
   ```python
   mongo_db = mongo_client["pricepilot_raw"]
   ```

4. **Access collection**:
   ```python
   collection = mongo_db["raw_products"]
   ```

5. **Perform operations**:
   ```python
   collection.insert_one({"url": "...", "html": "..."})
   ```

### Connection Flow:
```
.env file
   ↓ (read MONGODB_URI)
MongoClient
   ↓ (connect to Atlas)
Database (pricepilot_raw)
   ↓ (select collection)
Collection (raw_products)
   ↓ (insert/find/update/delete)
Documents
```

---

## 🛡️ Security: Safe Queries

### ✅ SAFE - Using pymongo methods:
```python
# Safe insert
collection.insert_one({"url": user_input, "html": scraped_html})

# Safe find
collection.find_one({"url": user_input})

# Safe update
collection.update_one(
    {"url": user_input},
    {"$set": {"processed": True}}
)
```

### Why Safe?
pymongo automatically handles data sanitization. User input is treated as **data**, not as **commands**.

### ❌ UNSAFE - String concatenation (DON'T DO THIS):
```python
# This is vulnerable to NoSQL injection
query = f"{{url: '{user_input}'}}"  # DON'T DO THIS!
```

---

## 📝 Common Operations

### Insert a scraped product:
```python
from app.database.mongo import get_raw_products_collection

collection = get_raw_products_collection()

product_data = {
    "url": "https://daraz.com.np/product/123",
    "html": "<html>...</html>",
    "scraped_at": "2024-01-15T10:30:00",
    "source": "daraz.com.np"
}

result = collection.insert_one(product_data)
print(f"Inserted with ID: {result.inserted_id}")
```

### Find a product by URL:
```python
collection = get_raw_products_collection()

product = collection.find_one({"url": "https://daraz.com.np/product/123"})

if product:
    print(f"Found: {product['url']}")
    print(f"Scraped at: {product['scraped_at']}")
```

### Update a product:
```python
collection = get_raw_products_collection()

result = collection.update_one(
    {"url": "https://daraz.com.np/product/123"},
    {"$set": {"processed": True, "processed_at": "2024-01-15T11:00:00"}}
)

print(f"Modified {result.modified_count} document(s)")
```

### Delete a product:
```python
collection = get_raw_products_collection()

result = collection.delete_one({"url": "https://daraz.com.np/product/123"})

print(f"Deleted {result.deleted_count} document(s)")
```

---

## 🧪 Testing MongoDB Connection

### Start the server:
```bash
cd backend
uvicorn main:app --reload
```

### Expected output:
```
✅ PostgreSQL connection pool created successfully
✅ MongoDB connected successfully
   Database: pricepilot_raw
   Collection: raw_products
🚀 PricePilot API started successfully
```

### If MongoDB fails:
```
❌ MongoDB connection failed: ...
⚠️  Warning: MongoDB connection failed, but API will continue
✅ PostgreSQL connection pool created successfully
🚀 PricePilot API started successfully
```

The API will still work even if MongoDB fails (only affects scraping features).

---

## 🎓 Viva Questions & Answers

### Q1: What is MongoDB?
**A**: MongoDB is a NoSQL database that stores data in flexible, JSON-like documents instead of tables with rows and columns.

### Q2: Why use MongoDB for this project?
**A**: We use MongoDB to store raw scraped data (HTML, unprocessed text) because it's flexible and doesn't require a fixed structure. PostgreSQL stores the clean, structured data.

### Q3: What's the difference between a database and a collection?
**A**: 
- **Database** = Container for collections (like a folder)
- **Collection** = Group of related documents (like a table)
- **Document** = One piece of data (like a row)

### Q4: Why not use motor (async MongoDB)?
**A**: pymongo is simpler and sufficient for our use case. Scraping happens in background tasks, not during user requests, so async isn't necessary.

### Q5: How does pymongo prevent injection attacks?
**A**: pymongo treats user input as data, not commands. When we use `collection.find_one({"url": user_input})`, the user_input is safely handled as a value, not as part of the query structure.

### Q6: What data will you store in MongoDB?
**A**: 
- Raw HTML from scraped product pages
- Product URLs
- Scraping timestamps
- Source website names
- Any unprocessed data before cleaning

### Q7: How do you access MongoDB in your code?
**A**: 
```python
from app.database.mongo import get_raw_products_collection

collection = get_raw_products_collection()
collection.insert_one({"url": "...", "html": "..."})
```

### Q8: What happens if MongoDB connection fails?
**A**: The API prints a warning but continues to work. Only scraping features would be affected. User authentication and product viewing (from PostgreSQL) still work.

---

## 📊 Data Flow Example

### Scraping a Product:

1. **Scrape website**:
   ```python
   html = scrape_product_page("https://daraz.com.np/product/123")
   ```

2. **Store raw data in MongoDB**:
   ```python
   collection = get_raw_products_collection()
   collection.insert_one({
       "url": "https://daraz.com.np/product/123",
       "html": html,
       "scraped_at": datetime.now(),
       "source": "daraz.com.np"
   })
   ```

3. **Process HTML**:
   ```python
   product_name = extract_name(html)
   product_price = extract_price(html)
   product_image = extract_image(html)
   ```

4. **Store clean data in PostgreSQL**:
   ```python
   await db.execute(
       "INSERT INTO products (name, price, image_url, source_url) VALUES ($1, $2, $3, $4)",
       product_name, product_price, product_image, "https://daraz.com.np/product/123"
   )
   ```

5. **Mobile app fetches from PostgreSQL**:
   ```python
   products = await db.fetch("SELECT * FROM products WHERE name LIKE $1", search_term)
   ```

---

## ✅ Summary

### What We Built:
- ✅ MongoDB connection module (`mongo.py`)
- ✅ Synchronous connection using pymongo
- ✅ Connection test on startup
- ✅ Safe query functions
- ✅ Integration with FastAPI

### What MongoDB Does:
- Stores raw scraped HTML and data
- Provides flexible storage for unstructured data
- Acts as a backup before processing
- Complements PostgreSQL (structured data)

### Key Concepts:
- **Database** = pricepilot_raw (container)
- **Collection** = raw_products (like a table)
- **Document** = One scraped product (like a row)
- **pymongo** = Python driver for MongoDB (synchronous)
