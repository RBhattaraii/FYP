import re

with open('app/product/[id].tsx', 'r', encoding='utf-8') as f:
    content = f.read()

missing_block = """
    try {
      const supported = await Linking.canOpenURL(url);
      if (supported) {
        await Linking.openURL(url);
      } else {
        console.error('Cannot open URL:', url);
      }
    } catch (openError) {
      console.error('Failed to open store URL:', openError);
    }
  };

  const handleSetPriceAlert = () => {
    if (!product) {
      Alert.alert('Error', 'No product to create an alert for.');
      return;
    }
    const defaultTarget = Math.round((product.price || 0) * 0.9);
    setTargetPriceInput(defaultTarget.toString());
    setIsAlertModalVisible(true);
  };

  const submitPriceAlert = async () => {
    if (!product) return;
    try {
      setIsCreating(true);
      const targetNumber = parseFloat(targetPriceInput.replace(/,/g, ''));
      if (isNaN(targetNumber) || targetNumber <= 0) {
        Alert.alert('Invalid Price', 'Please enter a valid target price.');
        setIsCreating(false);
        return;
      }
      
      const payload = {
        product_id: product.id,
        target_price: targetNumber,
        product_title: product.title,
        store_name: product.store_name,
        url: product.url,
        image_url: product.image_url,
        current_price: product.price
      };
      
      await createPriceAlert(payload);
      setIsCreating(false);
      setAlertSuccess(true);
      
    } catch (err: any) {
      console.error('Failed to create price alert', err);
      Alert.alert('Error', err.message || 'Could not create price alert.');
      setIsCreating(false);
    }
  };

  const handleAddToFavorites = async () => {
    if (product) {
      await addItem(product);
      Alert.alert('Success', 'Added to favorites');
    }
  };

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#6E4B3A" />
        <Text style={styles.loadingText}>Loading product details...</Text>
      </View>
    );
  }

  if (error || !product) {
    return (
      <View style={styles.centerContainer}>
        <Ionicons name="alert-circle-outline" size={64} color="#D32F2F" />
        <Text style={styles.errorTitle}>Oops!</Text>
        <Text style={styles.errorMessage}>{error || 'Product not found'}</Text>
        <TouchableOpacity style={styles.backButton} onPress={() => router.back()}>
          <Text style={styles.backButtonText}>Go Back</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={{ paddingBottom: insets.bottom + 140 }}>
        {/* Top Area */}
        <View style={[styles.header, { marginTop: Math.max(insets.top, 16) }]}>
          <TouchableOpacity style={styles.headerIcon} onPress={() => router.back()}>
            <Ionicons name="chevron-back" size={24} color="#111111" />
          </TouchableOpacity>
          
          <View style={{ flexDirection: 'row', gap: 12 }}>
            <TouchableOpacity style={styles.headerIcon} onPress={handleAddToFavorites}>
              <Ionicons name="heart-outline" size={24} color="#111111" />
            </TouchableOpacity>
            <TouchableOpacity style={styles.headerIcon} onPress={() => setIsHistoryModalVisible(true)}>
              <Ionicons name="stats-chart-outline" size={24} color="#111111" />
            </TouchableOpacity>
          </View>
        </View>

        {/* Image Section */}
        <View style={styles.imageSection}>
          <Image 
            source={{ uri: appendCacheVersion(product.image_url) }} 
            style={styles.mainImage} 
            resizeMode="contain" 
          />
        </View>

        {/* Content Section */}
        <View style={styles.contentSection}>
          <View style={styles.titleRow}>
            <Text style={styles.categoryText}>{product.category || 'Product'}</Text>
            <View style={styles.ratingBox}>
              <Ionicons name="star" size={16} color="#F5A623" />
              <Text style={styles.ratingText}>4.8</Text>
            </View>
          </View>
          
          <Text style={styles.title}>{product.title}</Text>
          
          <View style={styles.actionButtonsRow}>
             <TouchableOpacity style={styles.actionButton} onPress={handleSetPriceAlert}>
                <Ionicons name="notifications-outline" size={24} color="#6E4B3A" />
                <Text style={styles.actionButtonText}>Price Alert</Text>
             </TouchableOpacity>
             <TouchableOpacity style={styles.actionButton} onPress={() => router.push({ pathname: '/compare-search', params: { id: product.id } })}>
                <Ionicons name="git-compare-outline" size={24} color="#6E4B3A" />
                <Text style={styles.actionButtonText}>Compare</Text>
             </TouchableOpacity>
          </View>
        </View>
      </ScrollView>

      {/* Bottom Bar */}
      <View style={[styles.bottomBar, { paddingBottom: Math.max(insets.bottom, 16) }]}>
        <View style={styles.priceContainer}>
          <Text style={styles.priceLabel}>Current Price</Text>
          <Text style={styles.priceValue}>Rs. {product.price?.toLocaleString() || 'N/A'}</Text>
        </View>
        <TouchableOpacity style={styles.cartButton} onPress={handleOpenStore}>
          <Text style={styles.cartButtonText}>View Store</Text>
          <Ionicons name="open-outline" size={18} color="#FFFFFF" style={{ marginLeft: 8 }} />
        </TouchableOpacity>
      </View>

      {/* Target Price Modal */}
      <Modal
        visible={isAlertModalVisible}
        transparent
        animationType="fade"
        onRequestClose={() => setIsAlertModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            {alertSuccess ? (
              <View style={{ alignItems: 'center', width: '100%' }}>
                <Ionicons name="checkmark-circle" size={80} color="#4CAF50" style={{ marginBottom: 16 }} />
                <Text style={styles.modalTitle}>Success!</Text>
                <Text style={styles.modalSubtitle}>Price alert created successfully. You will be notified when the price drops.</Text>
                <View style={styles.modalButtons}>
                  <TouchableOpacity style={styles.modalCancelBtn} onPress={() => { setAlertSuccess(false); setIsAlertModalVisible(false); }}>
                    <Text style={styles.modalCancelText}>Close</Text>
                  </TouchableOpacity>
                  <TouchableOpacity style={styles.modalSaveBtn} onPress={() => { setAlertSuccess(false); setIsAlertModalVisible(false); router.push('/price-alerts'); }}>
                    <Text style={styles.modalSaveText}>View Alerts</Text>
                  </TouchableOpacity>
                </View>
              </View>
            ) : (
              <>
                <Text style={styles.modalTitle}>Set Price Alert</Text>
                <Text style={styles.modalSubtitle}>Notify me when price drops below:</Text>
                
                <View style={styles.inputContainer}>
                  <Text style={styles.currencyPrefix}>Rs.</Text>
                  <TextInput
                    style={styles.priceInput}
                    value={targetPriceInput}
                    onChangeText={setTargetPriceInput}
                    keyboardType="numeric"
                    placeholder="Enter target price"
                    placeholderTextColor="#A0A0A0"
                    editable={!isCreating}
                  />
                </View>

                <View style={styles.modalButtons}>
                  <TouchableOpacity 
                    style={styles.modalCancelBtn}
                    onPress={() => setIsAlertModalVisible(false)}
                    disabled={isCreating}
                  >
                    <Text style={styles.modalCancelText}>Cancel</Text>
                  </TouchableOpacity>
                  <TouchableOpacity 
                    style={styles.modalSaveBtn}
                    onPress={submitPriceAlert}
                    disabled={isCreating}
                  >
                    {isCreating ? (
                      <ActivityIndicator color="#FFFFFF" size="small" />
                    ) : (
                      <Text style={styles.modalSaveText}>Set Alert</Text>
                    )}
                  </TouchableOpacity>
                </View>
              </>
            )}
          </View>
        </View>
      </Modal>

      {/* History Modal */}
      <PriceHistoryModal
        isVisible={isHistoryModalVisible}
        onClose={() => setIsHistoryModalVisible(false)}
        productId={product?.id || ''}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
"""

parts = content.split('      }\n    }\n    alignItems: \'center\',')
if len(parts) == 2:
    new_content = parts[0] + missing_block + "    alignItems: 'center',\n" + parts[1].lstrip()
    with open('app/product/[id].tsx', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print('SUCCESS! Repaired the file!')
else:
    print('FAILED TO SPLIT:', len(parts))
