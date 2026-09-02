import os
import re

file_path = r'c:\Users\NITOR 5\Desktop\FYP\mobile\app\(tabs)\favorites.tsx'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add LinearGradient import if not present
if 'LinearGradient' not in content:
    content = content.replace('import { SafeAreaView } from \'react-native-safe-area-context\';', 
                              'import { SafeAreaView } from \'react-native-safe-area-context\';\nimport { LinearGradient } from \'expo-linear-gradient\';')

# Replace the grid container code
render_pattern = re.compile(r'          <View style=\{styles\.gridContainer\}>\n.*?          </View>\n        \)\}', re.DOTALL)

new_render = """          <View style={styles.gridContainer}>
            {favoriteItems.map((item) => (
              <TouchableOpacity key={item.id} style={styles.productCard} activeOpacity={0.9} onPress={() => router.push(`/product/${item.id}`)}>
                <View style={styles.imageContainer}>
                  <Image source={{ uri: item.imageUrl }} style={styles.productImage} resizeMode="cover" />
                  <LinearGradient 
                    colors={['rgba(0,0,0,0.4)', 'transparent']} 
                    style={StyleSheet.absoluteFillObject} 
                    start={{x: 0, y: 0}} end={{x: 0, y: 0.4}}
                  />
                  <TouchableOpacity style={styles.heartButton} onPress={() => removeItem(item.id)} activeOpacity={0.7}>
                    <Ionicons name="heart" size={18} color="#FF4757" />
                  </TouchableOpacity>
                </View>
                
                <View style={styles.cardDetails}>
                  <Text style={styles.productName} numberOfLines={2}>{item.title}</Text>
                  
                  <View style={styles.priceRow}>
                    <Text style={styles.productPrice}>Rs {item.price.toLocaleString()}</Text>
                    <View style={styles.ratingBadge}>
                      <Ionicons name="star" size={12} color="#FFA502" />
                      <Text style={styles.ratingText}>4.9</Text>
                    </View>
                  </View>
                </View>
              </TouchableOpacity>
            ))}
          </View>
        )}"""

content = render_pattern.sub(new_render, content)

# Replace the styles starting from gridContainer
styles_pattern = re.compile(r'  gridContainer: \{.*?\n\}\);\n', re.DOTALL)

new_styles = """  gridContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    paddingTop: 8,
  },
  productCard: {
    width: cardWidth,
    marginBottom: 24,
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.06,
    shadowRadius: 16,
    elevation: 4,
  },
  imageContainer: {
    width: '100%',
    height: cardWidth * 1.15,
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    overflow: 'hidden',
    backgroundColor: '#F7F7F7',
  },
  productImage: {
    width: '100%',
    height: '100%',
  },
  heartButton: {
    position: 'absolute',
    top: 12,
    right: 12,
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#FFFFFF',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 5,
  },
  cardDetails: {
    padding: 12,
    paddingTop: 14,
  },
  productName: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 13,
    color: '#2D3436',
    lineHeight: 18,
    height: 36, // Force two lines
    marginBottom: 10,
  },
  priceRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  productPrice: {
    fontFamily: 'Poppins_700Bold',
    fontSize: 15,
    color: '#FF6B6B',
  },
  ratingBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFF8E1',
    paddingHorizontal: 6,
    paddingVertical: 3,
    borderRadius: 8,
    gap: 4,
  },
  ratingText: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 11,
    color: '#FFA502',
  },
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 80,
  },
  emptyTitle: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 16,
    color: '#B2BEC3',
    marginTop: 16,
  }
});
"""

content = styles_pattern.sub(new_styles, content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
