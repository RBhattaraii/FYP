# 🔄 Compare & History Features Implementation Guide

## ✅ Backend Implementation Complete

Your backend now has **full Compare and History functionality**:

### 🗄️ **Database Tables Created**
- ✅ `user_history` - Tracks user product views
- ✅ `product_comparisons` - Stores comparison sets  
- ✅ `comparison_items` - Links products to comparisons

### 🚀 **API Endpoints Available**

#### History Endpoints (`/history/`)
- `GET /history/` - Get user's viewing history
- `POST /history/add` - Add product to history (auto-called on product view)
- `DELETE /history/clear` - Clear history (all or specific products)
- `GET /history/stats` - Get history statistics

#### Compare Endpoints (`/compare/`)
- `GET /compare/` - List user's comparisons
- `POST /compare/create` - Create new comparison
- `GET /compare/{id}` - Get comparison details with structured table
- `POST /compare/{id}/add` - Add product to existing comparison
- `DELETE /compare/{id}/remove/{product_id}` - Remove product from comparison
- `DELETE /compare/{id}` - Delete entire comparison
- `POST /compare/search` - Search products to add to comparison
- `POST /compare/quick` - Quick 2-product comparison (no saving)

---

## 📱 Mobile App Frontend Implementation

### **1. History Feature Implementation**

#### **History Button Functionality**
```javascript
// When user clicks History button on product detail screen
const handleHistoryPress = async () => {
  try {
    const token = await getAuthToken(); // Get user's JWT token
    
    const response = await fetch(`${API_BASE_URL}/history/`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (response.ok) {
      const historyData = await response.json();
      // Navigate to History screen with data
      navigation.navigate('History', { historyItems: historyData.items });
    } else {
      showError('Failed to load history');
    }
  } catch (error) {
    showError('Network error');
  }
};
```

#### **Auto-Add to History** (Already Working)
- ✅ **Automatic**: When user views product detail, it's automatically added to history
- ✅ **No extra code needed**: Backend handles this on `/products/{id}` endpoint

#### **History Screen Layout**
```javascript
const HistoryScreen = ({ route }) => {
  const { historyItems } = route.params;
  
  return (
    <FlatList
      data={historyItems}
      renderItem={({ item }) => (
        <ProductHistoryCard
          product={item}
          onPress={() => navigation.navigate('ProductDetail', { productId: item.product_id })}
          onRemove={() => removeFromHistory(item.product_id)}
        />
      )}
      keyExtractor={item => item.id.toString()}
    />
  );
};
```

### **2. Compare Feature Implementation**

#### **Compare Button Functionality**
```javascript
// When user clicks Compare button on product detail screen
const handleComparePress = async () => {
  // Show modal with options:
  // 1. "Compare with Saved Products" 
  // 2. "Search Product to Compare"
  // 3. "Quick Compare" (if they have comparisons)
  
  setCompareModalVisible(true);
};
```

#### **Compare Options Modal**
```javascript
const CompareOptionsModal = ({ visible, onClose, currentProduct }) => {
  return (
    <Modal visible={visible} animationType="slide">
      <View style={styles.modalContent}>
        <Text style={styles.title}>Compare Options</Text>
        
        {/* Option 1: Compare with Saved Products */}
        <TouchableOpacity 
          style={styles.optionButton}
          onPress={() => showSavedProductsForCompare()}
        >
          <Icon name="favorite" />
          <Text>Compare with Saved Products</Text>
        </TouchableOpacity>
        
        {/* Option 2: Search Product to Compare */}
        <TouchableOpacity 
          style={styles.optionButton}
          onPress={() => showSearchForCompare()}
        >
          <Icon name="search" />
          <Text>Search Product to Compare</Text>
        </TouchableOpacity>
        
        {/* Option 3: View My Comparisons */}
        <TouchableOpacity 
          style={styles.optionButton}
          onPress={() => navigation.navigate('MyComparisons')}
        >
          <Icon name="compare" />
          <Text>View My Comparisons</Text>
        </TouchableOpacity>
      </View>
    </Modal>
  );
};
```

#### **Saved Products Selection Screen**
```javascript
const SavedProductsForCompareScreen = ({ currentProduct }) => {
  const [savedProducts, setSavedProducts] = useState([]);
  
  useEffect(() => {
    loadSavedProducts(); // Load from wishlist/favorites
  }, []);
  
  const handleProductSelect = async (selectedProduct) => {
    // Create quick comparison
    const compareResult = await createQuickComparison(currentProduct.id, selectedProduct.id);
    navigation.navigate('ComparisonResult', { comparison: compareResult });
  };
  
  return (
    <FlatList
      data={savedProducts}
      renderItem={({ item }) => (
        <ProductCard
          product={item}
          onPress={() => handleProductSelect(item)}
          showCompareButton={true}
        />
      )}
    />
  );
};
```

#### **Search for Compare Screen**
```javascript
const SearchForCompareScreen = ({ currentProduct }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  
  const searchProducts = async (query) => {
    const response = await fetch(`${API_BASE_URL}/compare/search`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        query: query,
        exclude_product_ids: [currentProduct.id], // Don't show current product
        limit: 20
      })
    });
    
    const data = await response.json();
    setSearchResults(data.results);
  };
  
  const handleProductSelect = async (selectedProduct) => {
    // Create quick comparison
    const compareResult = await createQuickComparison(currentProduct.id, selectedProduct.id);
    navigation.navigate('ComparisonResult', { comparison: compareResult });
  };
  
  return (
    <View>
      <SearchBar
        value={searchQuery}
        onChangeText={setSearchQuery}
        onSubmitEditing={() => searchProducts(searchQuery)}
      />
      
      <FlatList
        data={searchResults}
        renderItem={({ item }) => (
          <ProductCard
            product={item}
            onPress={() => handleProductSelect(item)}
            showCompareButton={true}
          />
        )}
      />
    </View>
  );
};
```

#### **Comparison Result Screen**
```javascript
const ComparisonResultScreen = ({ route }) => {
  const { comparison } = route.params;
  
  return (
    <ScrollView style={styles.container}>
      {/* Product Images Side by Side */}
      <View style={styles.imagesRow}>
        <Image source={{ uri: comparison.product1.image_url }} style={styles.productImage} />
        <Image source={{ uri: comparison.product2.image_url }} style={styles.productImage} />
      </View>
      
      {/* Comparison Table */}
      <View style={styles.comparisonTable}>
        <ComparisonRow 
          label="Price" 
          value1={`Rs ${comparison.product1.price}`}
          value2={`Rs ${comparison.product2.price}`}
          highlight={comparison.comparison_table.price_comparison.lowest_price}
        />
        
        <ComparisonRow 
          label="Store" 
          value1={comparison.product1.store}
          value2={comparison.product2.store}
        />
        
        <ComparisonRow 
          label="Category" 
          value1={comparison.product1.category}
          value2={comparison.product2.category}
        />
        
        {/* Price Difference Highlight */}
        <View style={styles.savingsCard}>
          <Text style={styles.savingsText}>
            💰 Save Rs {comparison.comparison_table.price_comparison.savings.toFixed(2)} 
            by choosing the cheaper option!
          </Text>
        </View>
      </View>
      
      {/* Action Buttons */}
      <View style={styles.actionButtons}>
        <Button 
          title="Save Comparison" 
          onPress={() => saveComparison(comparison)}
        />
        <Button 
          title="View in Store" 
          onPress={() => openStore(comparison.product1)}
        />
      </View>
    </ScrollView>
  );
};
```

### **3. API Integration Functions**

#### **History Functions**
```javascript
export const historyAPI = {
  // Get user history
  getHistory: async (page = 1, limit = 50) => {
    const token = await getAuthToken();
    const response = await fetch(`${API_BASE_URL}/history/?page=${page}&limit=${limit}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    return response.json();
  },
  
  // Clear specific products from history
  clearHistory: async (productIds = null) => {
    const token = await getAuthToken();
    const response = await fetch(`${API_BASE_URL}/history/clear`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ product_ids: productIds })
    });
    return response.json();
  },
  
  // Get history stats
  getHistoryStats: async () => {
    const token = await getAuthToken();
    const response = await fetch(`${API_BASE_URL}/history/stats`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    return response.json();
  }
};
```

#### **Compare Functions**
```javascript
export const compareAPI = {
  // Quick comparison between 2 products
  quickCompare: async (product1Id, product2Id) => {
    const token = await getAuthToken();
    const response = await fetch(`${API_BASE_URL}/compare/quick`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        product1_id: product1Id,
        product2_id: product2Id
      })
    });
    return response.json();
  },
  
  // Create and save comparison
  createComparison: async (name, productIds = []) => {
    const token = await getAuthToken();
    const response = await fetch(`${API_BASE_URL}/compare/create`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        comparison_name: name,
        product_ids: productIds
      })
    });
    return response.json();
  },
  
  // Get user's saved comparisons
  getComparisons: async () => {
    const token = await getAuthToken();
    const response = await fetch(`${API_BASE_URL}/compare/`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    return response.json();
  },
  
  // Search products for comparison
  searchForCompare: async (query, excludeIds = []) => {
    const token = await getAuthToken();
    const response = await fetch(`${API_BASE_URL}/compare/search`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        query: query,
        exclude_product_ids: excludeIds,
        limit: 20
      })
    });
    return response.json();
  }
};
```

---

## 🎯 **Implementation Summary**

### **What You Need to Do in Mobile App:**

1. **History Button** → Call `historyAPI.getHistory()` → Navigate to History screen
2. **Compare Button** → Show options modal → Either:
   - Show saved products for selection
   - Show search screen for product selection  
   - Call `compareAPI.quickCompare()` → Show comparison result
3. **Product Views** → Automatically tracked (no extra code needed)

### **UI Screens to Create:**
- ✅ History Screen (list of viewed products)
- ✅ Compare Options Modal 
- ✅ Saved Products Selection Screen
- ✅ Search for Compare Screen  
- ✅ Comparison Result Screen
- ✅ My Comparisons Screen (optional)

### **Key Features:**
- 🔄 **Auto History Tracking**: Products automatically added to history on view
- 🔍 **Flexible Compare**: Compare with saved products OR search for products
- 💾 **Save Comparisons**: Users can save comparison sets for later
- ⚡ **Quick Compare**: Instant comparison without saving
- 📊 **Structured Data**: Backend provides organized comparison tables

### **Testing:**
- 🧪 API endpoints tested and working
- 📖 Full documentation available at: `http://localhost:8000/docs`
- ✅ Authentication properly handled (optional for product views)

**🎉 Your Compare and History features are now fully implemented on the backend and ready for mobile app integration!**