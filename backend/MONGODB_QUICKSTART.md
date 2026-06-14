# MongoDB Quick Start Guide

## 🚀 Quick Setup

### 1. MongoDB is Already Configured
Your `.env` file already has:
```
MONGODB_URI=mongodb+srv://PricePilot:cfokIUXQkk2asZR2@final-year-project.gejpsy4.mongodb.net/pricepilot_raw?appName=Final-Year-Project
```

### 2. Start the Server
```bash
cd backend
uvicorn main:app --reload
```

### 3. Check Logs
You should see:
```
✅ PostgreSQL connection pool created successfully
✅ MongoDB connected successfully
   Database: pricepilot_raw
   Collection: raw_products
🚀 PricePilot API started successfully
```

---

## 📝 Quick Usage Examples

### Insert a scraped product:
```python
from app.database.mongo import get_raw_products_collection

collection = get_raw_products_collection()

collection.insert_one({
    "url": "https://daraz.com.np/product/123",
    "html": "<html>...</html>",
    "scraped_at": "2024-01-15T10:30:00",
    "source": "daraz.com.np"
})
```

### Find a product:
```python
product = collection.find_one({"url": "https://daraz.com.np/product/123"})
print(product)
```

### Update a product:
```python
collection.update_one(
    {"url": "https://daraz.com.np/product/123"},
    {"$set": {"processed": True}}
)
```

### Delete a product:
```python
collection.delete_one({"url": "https://daraz.com.np/product/123"})
```

---

## 🎓 Quick Viva Answers

**Q: What is MongoDB used for?**  
A: Storing raw scraped HTML and unprocessed data from e-commerce websites.

**Q: Why MongoDB + PostgreSQL?**  
A: MongoDB for flexible/unstructured data (raw HTML), PostgreSQL for structured data (clean products, users).

**Q: What's a collection?**  
A: Like a table in SQL. Our collection is `raw_products`.

**Q: What's a document?**  
A: Like a row in SQL. One scraped product is one document.

**Q: Why pymongo not motor?**  
A: pymongo is simpler (synchronous). Sufficient for background scraping tasks.

---

## 📊 Data Flow

```
Scrape Website
    ↓
Store raw HTML in MongoDB (pricepilot_raw)
    ↓
Process and extract clean data
    ↓
Store clean data in PostgreSQL (products table)
    ↓
Mobile app uses PostgreSQL data
```

---

## ✅ What You Have Now

- ✅ MongoDB connection configured
- ✅ Connection tested on startup
- ✅ Safe query functions ready
- ✅ Documentation complete
- ✅ Ready for scraping implementation
