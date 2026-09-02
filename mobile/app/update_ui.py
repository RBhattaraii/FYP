import os
import re

file_path = r'c:\Users\NITOR 5\Desktop\FYP\mobile\app\my-comparisons.tsx'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

if 'LinearGradient' not in content:
    content = content.replace('import { SafeAreaView } from \'react-native-safe-area-context\';', 
                              'import { SafeAreaView } from \'react-native-safe-area-context\';\nimport { LinearGradient } from \'expo-linear-gradient\';')

if 'const getStoreColor =' not in content:
    content = content.replace('  const loadComparisons = async () => {', 
                              '  const getStoreColor = (storeName: string) => {\n    if (!storeName) return \'#64748B\';\n    const name = storeName.toLowerCase();\n    if (name.includes(\'daraz\')) return \'#F97316\';\n    if (name.includes(\'hukut\')) return \'#8B5CF6\';\n    if (name.includes(\'sasto\')) return \'#EAB308\';\n    return \'#64748B\';\n  };\n\n  const loadComparisons = async () => {')

pattern = re.compile(r'  const renderComparisonItem = \(\{ item \}: \{ item: ProductComparison \}\) => \{.*?\n  \};\n', re.DOTALL)

replacement = """  const renderComparisonItem = ({ item }: { item: ProductComparison }) => {
    if (!item.items || item.items.length < 2) {
      return (
        <View style={styles.comparisonCard}>
          <View style={styles.cardHeader}>
            <Text style={styles.comparisonName}>{item.comparison_name}</Text>
            <Text style={styles.dateText}>{new Date(item.created_at).toLocaleDateString()}</Text>
          </View>
          <View style={[styles.cardBody, { padding: 16 }]}>
            <Text style={{ fontFamily: 'Poppins_400Regular', color: '#EF4444' }}>
              Invalid comparison (missing products)
            </Text>
          </View>
        </View>
      );
    }
    const item1 = item.items[0];
    const item2 = item.items[1];

    let name1 = item1.product_title || 'Product 1';
    let name2 = item2.product_title || 'Product 2';
    if (item.comparison_name && item.comparison_name.includes(' vs ')) {
       const parts = item.comparison_name.split(' vs ');
       name1 = parts[0];
       name2 = parts[1];
    }

    return (
      <TouchableOpacity
        style={styles.comparisonCard}
        onPress={() => handleComparisonSelect(item)}
        activeOpacity={0.85}
      >
        <LinearGradient
           colors={['#ffffff', '#fdfbf9']}
           style={StyleSheet.absoluteFillObject}
        />
        
        <View style={styles.cardHeader}>
          <View style={styles.titleWrapper}>
            <Text style={styles.comparisonName} numberOfLines={1}>{name1}</Text>
            <Text style={styles.comparisonSubName} numberOfLines={1}>vs {name2}</Text>
          </View>
          <Text style={styles.dateText}>
            {new Date(item.created_at).toLocaleDateString(undefined, {month: 'short', day: 'numeric'})}
          </Text>
        </View>

        <View style={styles.productsRow}>
          {/* Product 1 */}
          <View style={styles.productColumn}>
            <View style={styles.imageWrapper}>
              <Image 
                source={{ uri: item1.product_image_url || 'https://via.placeholder.com/120' }} 
                style={styles.productImage} 
                resizeMode="contain"
              />
              <View style={[styles.storeBadge, { backgroundColor: getStoreColor(item1.store_name) }]}>
                <Text style={styles.storeBadgeText}>{item1.store_name}</Text>
              </View>
            </View>
            <Text style={styles.priceText} numberOfLines={1}>Rs {Number(item1.product_price).toLocaleString()}</Text>
          </View>

          {/* VS Badge */}
          <View style={styles.vsBadgeContainer}>
            <LinearGradient 
              colors={['#FF6B6B', '#FF8E53']} 
              start={{x: 0, y: 0}} 
              end={{x: 1, y: 1}}
              style={styles.vsBadgeGradient}
            >
              <Text style={styles.vsBadgeText}>VS</Text>
            </LinearGradient>
          </View>

          {/* Product 2 */}
          <View style={styles.productColumn}>
            <View style={styles.imageWrapper}>
              <Image 
                source={{ uri: item2.product_image_url || 'https://via.placeholder.com/120' }} 
                style={styles.productImage} 
                resizeMode="contain"
              />
              <View style={[styles.storeBadge, { backgroundColor: getStoreColor(item2.store_name) }]}>
                <Text style={styles.storeBadgeText}>{item2.store_name}</Text>
              </View>
            </View>
            <Text style={styles.priceText} numberOfLines={1}>Rs {Number(item2.product_price).toLocaleString()}</Text>
          </View>
        </View>
      </TouchableOpacity>
    );
  };
"""

content = pattern.sub(replacement, content)

style_pattern = re.compile(r'  comparisonCard: \{.*?\n\}\);\n', re.DOTALL)
new_styles = """  comparisonCard: {
    backgroundColor: '#ffffff',
    borderRadius: 24,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: 'rgba(0,0,0,0.04)',
    shadowColor: '#6E4B3A',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.08,
    shadowRadius: 16,
    elevation: 5,
    overflow: 'hidden',
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    paddingHorizontal: 20,
    paddingTop: 20,
    paddingBottom: 16,
  },
  titleWrapper: {
    flex: 1,
    paddingRight: 12,
  },
  comparisonName: {
    fontSize: 16,
    fontFamily: 'Poppins_600SemiBold',
    color: '#2d3748',
    marginBottom: 2,
  },
  comparisonSubName: {
    fontSize: 14,
    fontFamily: 'Poppins_400Regular',
    color: '#718096',
  },
  dateText: {
    fontSize: 13,
    fontFamily: 'Poppins_500Medium',
    color: '#a0aec0',
    backgroundColor: '#edf2f7',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
    overflow: 'hidden',
  },
  productsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 20,
    paddingBottom: 24,
  },
  productColumn: {
    flex: 1,
    alignItems: 'center',
  },
  imageWrapper: {
    width: 100,
    height: 100,
    borderRadius: 20,
    backgroundColor: '#ffffff',
    padding: 12,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 3,
    borderWidth: 1,
    borderColor: '#f7fafc',
  },
  productImage: {
    width: '100%',
    height: '100%',
  },
  storeBadge: {
    position: 'absolute',
    bottom: -10,
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  storeBadgeText: {
    color: '#ffffff',
    fontSize: 10,
    fontFamily: 'Poppins_700Bold',
    textTransform: 'uppercase',
  },
  priceText: {
    fontSize: 17,
    fontFamily: 'Poppins_700Bold',
    color: '#1a202c',
    marginTop: 4,
  },
  vsBadgeContainer: {
    width: 44,
    height: 44,
    marginHorizontal: 12,
    zIndex: 10,
    shadowColor: '#FF6B6B',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 6,
  },
  vsBadgeGradient: {
    width: '100%',
    height: '100%',
    borderRadius: 22,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 3,
    borderColor: '#ffffff',
  },
  vsBadgeText: {
    color: '#ffffff',
    fontFamily: 'Poppins_700Bold',
    fontSize: 14,
  },
  cardBody: {
    padding: 16,
  }
});
"""

content = style_pattern.sub(new_styles, content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
