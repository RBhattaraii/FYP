import React from 'react';
import { View, TextInput, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors, typography, spacing, dimensions, borderRadius } from '../constants/theme';

interface SearchBarProps {
  onPress?: () => void;
  onVoicePress?: () => void;
}

export default function SearchBar({ onPress, onVoicePress }: SearchBarProps) {
  return (
    <TouchableOpacity 
      style={styles.container}
      onPress={onPress}
      activeOpacity={0.7}
      accessibilityLabel="Search"
      accessibilityRole="button"
    >
      <View style={styles.inputWrapper}>
        {/* Search Icon */}
        <Ionicons 
          name="search" 
          size={20} 
          color={colors.gray400} 
          style={styles.searchIcon}
        />
        
        {/* Placeholder Text */}
        <View style={styles.placeholderContainer}>
          <TextInput
            style={styles.placeholder}
            placeholder="Search to compare prices"
            placeholderTextColor={colors.gray400}
            editable={false}
            pointerEvents="none"
          />
        </View>
        
        {/* Voice Search Icon */}
        <TouchableOpacity 
          style={styles.voiceButton}
          onPress={onVoicePress}
          accessibilityLabel="Voice search"
          accessibilityRole="button"
        >
          <Ionicons name="mic-outline" size={20} color={colors.gray600} />
        </TouchableOpacity>
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: {
    height: dimensions.searchBar.height + 4,
    marginHorizontal: spacing.lg,
    marginTop: spacing.sm,
    marginBottom: spacing.md,
  },
  inputWrapper: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.gray100,
    borderRadius: borderRadius.full,
    paddingHorizontal: spacing.lg,
  },
  searchIcon: {
    marginRight: spacing.sm,
  },
  placeholderContainer: {
    flex: 1,
  },
  placeholder: {
    fontSize: typography.fontSize.bodyLarge,
    color: colors.gray900,
  },
  voiceButton: {
    width: dimensions.touchTarget.min,
    height: dimensions.touchTarget.min,
    justifyContent: 'center',
    alignItems: 'flex-end',
    marginRight: -spacing.sm,
  },
});
