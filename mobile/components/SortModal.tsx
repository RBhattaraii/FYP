import React from 'react';
import { View, Text, StyleSheet, Modal, TouchableOpacity, TouchableWithoutFeedback, Platform } from 'react-native';
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
      animationType="slide"
      onRequestClose={onClose}
    >
      <TouchableWithoutFeedback onPress={onClose}>
        <View style={styles.overlay}>
          <TouchableWithoutFeedback>
            <View style={styles.modalContainer}>
              <View style={styles.header}>
                <TouchableOpacity onPress={onClose} style={styles.backBtn}>
                  <Ionicons name="close" size={24} color="#111111" />
                </TouchableOpacity>
                <Text style={styles.title}>Sort By</Text>
                <View style={{ width: 24 }} />
              </View>
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
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'flex-end',
  },
  modalContainer: {
    backgroundColor: colors.white,
    borderTopLeftRadius: 32,
    borderTopRightRadius: 32,
    width: '100%',
    paddingBottom: Platform.OS === 'ios' ? 40 : 20,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: '#EEEEEE',
    marginBottom: spacing.md,
  },
  backBtn: {
    padding: spacing.xs,
  },
  title: {
    fontSize: typography.fontSize.h3,
    fontWeight: typography.fontWeight.semibold,
    color: colors.gray900,
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
