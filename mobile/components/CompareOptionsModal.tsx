import React from 'react';
import { View, Text, StyleSheet, Modal, TouchableOpacity, TouchableWithoutFeedback } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Product } from '../services/api';

const THEME_BROWN = '#6E4B3A';

interface CompareOptionsModalProps {
  visible: boolean;
  onClose: () => void;
  currentProduct: Product;
  onCompareWithSaved: () => void;
  onSearchToCompare: () => void;
  onViewComparisons: () => void;
}

export default function CompareOptionsModal({
  visible,
  onClose,
  currentProduct,
  onCompareWithSaved,
  onSearchToCompare,
  onViewComparisons,
}: CompareOptionsModalProps) {
  return (
    <Modal
      visible={visible}
      transparent
      animationType="fade"
      statusBarTranslucent
      onRequestClose={onClose}
    >
      <View style={styles.overlay}>
        <TouchableWithoutFeedback onPress={onClose}>
          <View style={styles.backdrop} />
        </TouchableWithoutFeedback>
        
        <View style={styles.sheetContent}>
          {/* Drag Handle */}
          <View style={styles.dragHandleContainer}>
            <View style={styles.dragHandle} />
          </View>
          
          <Text style={styles.sheetTitle}>Compare Options</Text>
          <Text style={styles.sheetSubtitle}>Choose how you want to compare</Text>

          {/* Primary Action - Saved Products */}
          <TouchableOpacity style={[styles.actionButton, styles.primaryButton]} onPress={onCompareWithSaved} activeOpacity={0.8}>
            <View style={styles.buttonLeft}>
              <Ionicons name="heart" size={22} color="#FFFFFF" />
              <Text style={styles.primaryButtonText}>Saved Products</Text>
            </View>
            <Ionicons name="arrow-forward" size={20} color="rgba(255,255,255,0.7)" />
          </TouchableOpacity>

          {/* Secondary Actions */}
          <View style={styles.secondaryActionsGroup}>
            <TouchableOpacity style={styles.secondaryButton} onPress={onSearchToCompare} activeOpacity={0.8}>
              <View style={styles.buttonLeft}>
                <Ionicons name="search" size={22} color={THEME_BROWN} />
                <Text style={styles.secondaryButtonText}>Search the Market</Text>
              </View>
              <Ionicons name="chevron-forward" size={20} color="#BDBDBD" />
            </TouchableOpacity>

            <View style={styles.divider} />

            <TouchableOpacity style={styles.secondaryButton} onPress={onViewComparisons} activeOpacity={0.8}>
              <View style={styles.buttonLeft}>
                <Ionicons name="layers" size={22} color={THEME_BROWN} />
                <Text style={styles.secondaryButtonText}>Comparison History</Text>
              </View>
              <Ionicons name="chevron-forward" size={20} color="#BDBDBD" />
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    justifyContent: 'flex-end',
  },
  backdrop: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0, 0, 0, 0.4)',
  },
  sheetContent: {
    backgroundColor: '#FAFAFA',
    borderTopLeftRadius: 32,
    borderTopRightRadius: 32,
    paddingHorizontal: 24,
    paddingBottom: 40,
    paddingTop: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: -4 },
    shadowOpacity: 0.1,
    shadowRadius: 16,
    elevation: 20,
  },
  dragHandleContainer: {
    alignItems: 'center',
    marginBottom: 20,
  },
  dragHandle: {
    width: 40,
    height: 5,
    borderRadius: 3,
    backgroundColor: '#E0E0E0',
  },
  sheetTitle: {
    fontFamily: 'Poppins_700Bold',
    fontSize: 20,
    color: '#111111',
    textAlign: 'center',
    marginBottom: 4,
  },
  sheetSubtitle: {
    fontFamily: 'Poppins_400Regular',
    fontSize: 14,
    color: '#757575',
    textAlign: 'center',
    marginBottom: 28,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 18,
    paddingHorizontal: 20,
    borderRadius: 20,
    marginBottom: 16,
  },
  primaryButton: {
    backgroundColor: THEME_BROWN,
    shadowColor: THEME_BROWN,
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.25,
    shadowRadius: 12,
    elevation: 6,
  },
  buttonLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  primaryButtonText: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 16,
    color: '#FFFFFF',
  },
  secondaryActionsGroup: {
    backgroundColor: '#FFFFFF',
    borderRadius: 24,
    paddingHorizontal: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.03,
    shadowRadius: 8,
    elevation: 2,
    borderWidth: 1,
    borderColor: '#EEEEEE',
  },
  secondaryButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 18,
  },
  secondaryButtonText: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 15,
    color: '#111111',
  },
  divider: {
    height: 1,
    backgroundColor: '#F5F5F5',
    marginLeft: 34,
  },
});
