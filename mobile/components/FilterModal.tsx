import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, Modal, TouchableOpacity, TouchableWithoutFeedback, ScrollView, TextInput } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors, typography, spacing, borderRadius } from '../constants/theme';

export interface FilterState {
  type: string;
  platforms: string[];
  categories: string[];
  minPrice: string;
  maxPrice: string;
}

interface FilterModalProps {
  visible: boolean;
  onClose: () => void;
  onApply: (filters: FilterState) => void;
  initialFilters: FilterState;
}

const THEME_RED = '#E53935';

export default function FilterModal({ visible, onClose, onApply, initialFilters }: FilterModalProps) {
  const [type, setType] = useState(initialFilters.type || 'Products');
  const [platforms, setPlatforms] = useState<string[]>(initialFilters.platforms || []);
  const [categories, setCategories] = useState<string[]>(initialFilters.categories || []);
  const [minPrice, setMinPrice] = useState(initialFilters.minPrice || '0');
  const [maxPrice, setMaxPrice] = useState(initialFilters.maxPrice || '16000');

  useEffect(() => {
    if (visible) {
      setType(initialFilters.type || 'Products');
      setPlatforms(initialFilters.platforms || []);
      setCategories(initialFilters.categories || []);
      setMinPrice(initialFilters.minPrice || '0');
      setMaxPrice(initialFilters.maxPrice || '16000');
    }
  }, [visible, initialFilters]);

  const togglePlatform = (platform: string) => {
    setPlatforms(prev => prev.includes(platform) ? prev.filter(p => p !== platform) : [...prev, platform]);
  };

  const toggleCategory = (cat: string) => {
    setCategories(prev => prev.includes(cat) ? prev.filter(c => c !== cat) : [...prev, cat]);
  };

  const handleApply = () => {
    onApply({
      type,
      platforms,
      categories,
      minPrice,
      maxPrice,
    });
  };

  const renderPills = (options: string[], selected: string[], onToggle: (item: string) => void) => (
    <View style={styles.pillsContainer}>
      {options.map((option) => {
        const isSelected = selected.includes(option);
        return (
          <TouchableOpacity 
            key={option}
            style={[styles.pill, isSelected && styles.pillSelected]}
            onPress={() => onToggle(option)}
          >
            <Text style={[styles.pillText, isSelected && styles.pillTextSelected]}>{option}</Text>
          </TouchableOpacity>
        );
      })}
    </View>
  );

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
                  <Ionicons name="chevron-back" size={24} color={colors.gray900} />
                </TouchableOpacity>
                <Text style={styles.title}>Filter by</Text>
                <View style={{ width: 24 }} />
              </View>

              <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={styles.scrollContent}>
                
                {/* Type Toggle */}
                <View style={styles.toggleRow}>
                  <TouchableOpacity 
                    style={[styles.toggleBtn, type === 'Products' && styles.toggleBtnActive]}
                    onPress={() => setType('Products')}
                  >
                    <View style={styles.radioOuter}>
                      {type === 'Products' && <View style={styles.radioInner} />}
                    </View>
                    <Text style={[styles.toggleText, type === 'Products' && styles.toggleTextActive]}>By Products</Text>
                  </TouchableOpacity>

                  <TouchableOpacity 
                    style={[styles.toggleBtn, type === 'Stores' && styles.toggleBtnActive]}
                    onPress={() => setType('Stores')}
                  >
                    <View style={styles.radioOuter}>
                      {type === 'Stores' && <View style={styles.radioInner} />}
                    </View>
                    <Text style={[styles.toggleText, type === 'Stores' && styles.toggleTextActive]}>By Stores</Text>
                  </TouchableOpacity>
                </View>

                {/* Platforms Section */}
                <View style={styles.section}>
                  <View style={styles.sectionHeader}>
                    <Text style={styles.sectionTitle}>Platform</Text>
                    <Ionicons name="chevron-down" size={20} color={colors.gray600} />
                  </View>
                  {renderPills(['Daraz', 'Hamrobazar', 'Sastodeal', 'Amazon', 'eBay', 'AliExpress'], platforms, togglePlatform)}
                </View>

                {/* Categories Section */}
                <View style={styles.section}>
                  <View style={styles.sectionHeader}>
                    <Text style={styles.sectionTitle}>Category</Text>
                    <Ionicons name="chevron-down" size={20} color={colors.gray600} />
                  </View>
                  {renderPills(['Electronics', 'Fashion', 'Home Decor', 'Beauty', 'Sports', 'Toys'], categories, toggleCategory)}
                </View>

                {/* Price Section */}
                <View style={styles.section}>
                  <View style={styles.sectionHeader}>
                    <Text style={styles.sectionTitle}>Price</Text>
                    <Ionicons name="chevron-down" size={20} color={colors.gray600} />
                  </View>
                  <Text style={styles.priceRangeText}>0.00 - 16000.00</Text>
                  
                  {/* Slider Visual */}
                  <View style={styles.sliderContainer}>
                    <View style={styles.sliderTrack}>
                      <View style={styles.sliderActiveTrack} />
                      <View style={[styles.sliderKnob, { left: '10%' }]} />
                      <View style={[styles.sliderKnob, { left: '60%' }]} />
                    </View>
                  </View>
                </View>

              </ScrollView>

              {/* Footer */}
              <View style={styles.footer}>
                <TouchableOpacity style={styles.applyBtn} onPress={handleApply}>
                  <Text style={styles.applyText}>Apply</Text>
                </TouchableOpacity>
              </View>
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
    backgroundColor: 'rgba(0,0,0,0.4)',
    justifyContent: 'flex-end',
  },
  modalContainer: {
    backgroundColor: colors.white,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    height: '85%',
    width: '100%',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.xl,
    paddingBottom: spacing.md,
  },
  title: {
    fontSize: typography.fontSize.h3,
    fontWeight: typography.fontWeight.bold,
    color: colors.gray900,
  },
  backBtn: {
    padding: spacing.xs,
  },
  scrollContent: {
    paddingHorizontal: spacing.lg,
    paddingBottom: spacing.xl,
  },
  toggleRow: {
    flexDirection: 'row',
    marginBottom: spacing.xl,
    gap: spacing.md,
  },
  toggleBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    borderRadius: borderRadius.full,
    borderWidth: 1,
    borderColor: colors.gray200,
    backgroundColor: colors.gray50,
  },
  toggleBtnActive: {
    backgroundColor: THEME_RED,
    borderColor: THEME_RED,
  },
  radioOuter: {
    width: 16,
    height: 16,
    borderRadius: 8,
    backgroundColor: colors.white,
    borderWidth: 1,
    borderColor: colors.gray300,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.sm,
  },
  radioInner: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: THEME_RED,
  },
  toggleText: {
    fontSize: typography.fontSize.body,
    color: colors.gray600,
    fontWeight: typography.fontWeight.medium,
  },
  toggleTextActive: {
    color: colors.white,
    fontWeight: typography.fontWeight.bold,
  },
  section: {
    borderBottomWidth: 1,
    borderBottomColor: colors.gray100,
    paddingBottom: spacing.lg,
    marginBottom: spacing.lg,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  sectionTitle: {
    fontSize: typography.fontSize.bodyLarge,
    fontWeight: typography.fontWeight.bold,
    color: colors.gray900,
  },
  pillsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
  },
  pill: {
    backgroundColor: colors.gray50,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    borderRadius: borderRadius.medium,
  },
  pillSelected: {
    backgroundColor: colors.white,
    borderWidth: 1,
    borderColor: THEME_RED,
  },
  pillText: {
    color: colors.gray600,
    fontSize: typography.fontSize.body,
  },
  pillTextSelected: {
    color: THEME_RED,
    fontWeight: typography.fontWeight.bold,
  },
  priceRangeText: {
    fontSize: typography.fontSize.body,
    color: colors.gray600,
    marginBottom: spacing.xl,
  },
  sliderContainer: {
    paddingHorizontal: spacing.sm,
    paddingBottom: spacing.md,
  },
  sliderTrack: {
    height: 4,
    backgroundColor: colors.gray200,
    borderRadius: 2,
    position: 'relative',
    width: '100%',
  },
  sliderActiveTrack: {
    position: 'absolute',
    left: '10%',
    width: '50%',
    height: '100%',
    backgroundColor: THEME_RED,
  },
  sliderKnob: {
    position: 'absolute',
    top: -8,
    width: 20,
    height: 20,
    borderRadius: 10,
    backgroundColor: THEME_RED,
  },
  footer: {
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    paddingBottom: spacing.xl,
    backgroundColor: colors.white,
  },
  applyBtn: {
    backgroundColor: THEME_RED,
    paddingVertical: 16,
    borderRadius: 30,
    alignItems: 'center',
  },
  applyText: {
    color: colors.white,
    fontSize: typography.fontSize.bodyLarge,
    fontWeight: typography.fontWeight.bold,
  },
});
