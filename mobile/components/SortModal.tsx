import React from 'react';
import { View, Text, StyleSheet, Modal, TouchableOpacity, TouchableWithoutFeedback } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors, typography, spacing, borderRadius } from '../constants/theme';

interface SortModalProps {
  visible: boolean;
  onClose: () => void;
  selectedSort: string;
  onSelectSort: (sort: string) => void;
}

const THEME_RED = '#E53935';

export default function SortModal({ visible, onClose, selectedSort, onSelectSort }: SortModalProps) {
  const sortOptions = [
    'Relevance',
    'Popularity',
    'Price Low to High',
    'Price High to Low',
    'Newest First'
  ];

  return (
    <Modal
      visible={visible}
      transparent={true}
      animationType="fade"
      onRequestClose={onClose}
    >
      <TouchableWithoutFeedback onPress={onClose}>
        <View style={styles.overlay}>
          <TouchableWithoutFeedback>
            <View style={styles.modalContainer}>
              {sortOptions.map((option) => {
                const isSelected = selectedSort === option;
                return (
                  <TouchableOpacity 
                    key={option} 
                    style={styles.sortRow}
                    onPress={() => {
                      onSelectSort(option);
                      onClose();
                    }}
                  >
                    <Text style={[styles.sortText, isSelected && styles.sortTextSelected]}>{option}</Text>
                    <View style={[styles.radioOuter, isSelected && styles.radioOuterSelected]}>
                      {isSelected && <View style={styles.radioInner} />}
                    </View>
                  </TouchableOpacity>
                );
              })}
            </View>
          </TouchableWithoutFeedback>
        </View>
      </TouchableWithoutFeedback>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.2)',
    alignItems: 'center',
    paddingTop: 120, // Moved slightly up to anchor closer to search bar
  },
  modalContainer: {
    width: '100%',
    backgroundColor: colors.white,
    borderBottomLeftRadius: borderRadius.large,
    borderBottomRightRadius: borderRadius.large,
    paddingTop: spacing.md,
    paddingBottom: spacing.xl,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 12,
    elevation: 5,
  },
  sortRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: spacing.lg, // Larger touch target
    paddingHorizontal: spacing.xl,
  },
  sortText: {
    fontSize: typography.fontSize.bodyLarge, // Larger font
    color: colors.gray900,
    fontWeight: typography.fontWeight.medium,
  },
  sortTextSelected: {
    fontWeight: typography.fontWeight.bold,
  },
  radioOuter: {
    width: 20,
    height: 20,
    borderRadius: 10,
    borderWidth: 2,
    borderColor: colors.gray400,
    justifyContent: 'center',
    alignItems: 'center',
  },
  radioOuterSelected: {
    borderColor: THEME_RED,
  },
  radioInner: {
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: THEME_RED,
  },
});
