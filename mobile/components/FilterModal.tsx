import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, Modal, TouchableOpacity, TouchableWithoutFeedback, ScrollView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors, typography, spacing, borderRadius } from '../constants/theme';
import RangeSlider from './RangeSlider';

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

const THEME_COLOR = '#6E4B3A';

export default function FilterModal({ visible, onClose, onApply, initialFilters }: FilterModalProps) {
  const [type, setType] = useState(initialFilters.type || 'Products');
  const [platforms, setPlatforms] = useState<string[]>(initialFilters.platforms || []);
  const [categories, setCategories] = useState<string[]>(initialFilters.categories || []);
  const [minPrice, setMinPrice] = useState(initialFilters.minPrice || '0');
  const [maxPrice, setMaxPrice] = useState(initialFilters.maxPrice || '160000');

  useEffect(() => {
    if (visible) {
      setType(initialFilters.type || 'Products');
      setPlatforms(initialFilters.platforms || []);
      setCategories(initialFilters.categories || []);
      setMinPrice(initialFilters.minPrice || '0');
      setMaxPrice(initialFilters.maxPrice || '1600000');
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
                  <Ionicons name="close" size={24} color="#111111" />
                </TouchableOpacity>
                <Text style={styles.title}>Filter</Text>
                <TouchableOpacity onPress={() => {
                  setPlatforms([]);
                  setCategories([]);
                  setMinPrice('0');
                  setMaxPrice('1600000');
                }}>
                  <Text style={styles.resetText}>Reset</Text>
                </TouchableOpacity>
              </View>

              <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={styles.scrollContent}>
                {/* Type toggle removed */}

                {/* Platforms Section */}
                <View style={styles.section}>
                  <View style={styles.sectionHeader}>
                    <Text style={styles.sectionTitle}>Platform</Text>
                  </View>
                  {renderPills(['Daraz', 'CG Digital', 'Hukut', 'KoreanBP', 'Oliz'], platforms, togglePlatform)}
                </View>

                {/* Categories Section */}
                <View style={styles.section}>
                  <View style={styles.sectionHeader}>
                    <Text style={styles.sectionTitle}>Category</Text>
                  </View>
                  {renderPills(['Laptops', 'Phones', 'Audio', 'Gaming', 'Accessories', 'Components'], categories, toggleCategory)}
                </View>

                {/* Price Section */}
                <View style={styles.section}>
                  <View style={styles.sectionHeader}>
                    <Text style={styles.sectionTitle}>Price Range</Text>
                  </View>
                  <RangeSlider
                    min={0}
                    max={1600000}
                    step={1000}
                    initialMin={isNaN(parseInt(minPrice, 10)) ? 0 : parseInt(minPrice, 10)}
                    initialMax={isNaN(parseInt(maxPrice, 10)) ? 1600000 : parseInt(maxPrice, 10)}
                    onValuesChange={(min, max) => {
                      setMinPrice(min.toString());
                      setMaxPrice(max.toString());
                    }}
                  />
                </View>

              </ScrollView>

              {/* Footer */}
              <View style={styles.footer}>
                <TouchableOpacity style={styles.applyBtn} onPress={handleApply}>
                  <Text style={styles.applyText}>Apply Filter</Text>
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
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'flex-end',
  },
  modalContainer: {
    backgroundColor: '#FFFFFF',
    flex: 1,
    width: '100%',
    paddingTop: 20, // To avoid status bar
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 24,
    paddingTop: 24,
    paddingBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#F5F5F5',
  },
  title: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 18,
    color: '#111111',
  },
  resetText: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 14,
    color: '#757575',
  },
  backBtn: {
    padding: 4,
  },
  scrollContent: {
    paddingHorizontal: 24,
    paddingTop: 24,
    paddingBottom: 40,
  },
  toggleRow: {
    flexDirection: 'row',
    marginBottom: 32,
    backgroundColor: '#F5F5F5',
    borderRadius: 9999,
    padding: 4,
  },
  toggleBtn: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 9999,
    alignItems: 'center',
    justifyContent: 'center',
  },
  toggleBtnActive: {
    backgroundColor: '#FFFFFF',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  toggleText: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 14,
    color: '#757575',
  },
  toggleTextActive: {
    fontFamily: 'Poppins_600SemiBold',
    color: '#111111',
  },
  section: {
    marginBottom: 32,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  sectionTitle: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 16,
    color: '#111111',
  },
  pillsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  pill: {
    backgroundColor: '#F5F5F5',
    paddingVertical: 10,
    paddingHorizontal: 16,
    borderRadius: 9999,
    borderWidth: 1,
    borderColor: '#F5F5F5',
  },
  pillSelected: {
    backgroundColor: THEME_COLOR,
    borderColor: THEME_COLOR,
  },
  pillText: {
    fontFamily: 'Poppins_400Regular',
    color: '#111111',
    fontSize: 14,
  },
  pillTextSelected: {
    fontFamily: 'Poppins_500Medium',
    color: '#FFFFFF',
  },
  footer: {
    paddingHorizontal: 24,
    paddingVertical: 20,
    backgroundColor: '#FFFFFF',
    borderTopWidth: 1,
    borderTopColor: '#F5F5F5',
  },
  applyBtn: {
    backgroundColor: THEME_COLOR,
    paddingVertical: 16,
    borderRadius: 9999,
    alignItems: 'center',
    shadowColor: THEME_COLOR,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 8,
    elevation: 4,
  },
  applyText: {
    fontFamily: 'Poppins_600SemiBold',
    color: '#FFFFFF',
    fontSize: 16,
  },
});
