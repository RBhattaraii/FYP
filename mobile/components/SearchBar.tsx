import React from 'react';
import { View, TextInput, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface SearchBarProps {
  onPress?: () => void;
  onFilterPress?: () => void;
}

export default function SearchBar({ onPress, onFilterPress }: SearchBarProps) {
  return (
    <View style={styles.container}>
      <TouchableOpacity 
        style={styles.searchInputContainer} 
        onPress={onPress}
        activeOpacity={0.8}
      >
        <Ionicons name="search-outline" size={20} color="#9E9E9E" style={styles.searchIcon} />
        <TextInput
          style={styles.searchInput}
          placeholder="Search"
          placeholderTextColor="#9E9E9E"
          editable={false}
          pointerEvents="none"
        />
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 24,
    marginTop: 16,
    marginBottom: 24,
    gap: 12,
  },
  searchInputContainer: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    height: 52,
    backgroundColor: '#FFFFFF',
    borderRadius: 9999, // Pill shape
    borderWidth: 1,
    borderColor: '#EEEEEE',
    paddingHorizontal: 16,
  },
  searchIcon: {
    marginRight: 10,
  },
  searchInput: {
    flex: 1,
    fontFamily: 'Poppins_400Regular',
    fontSize: 14,
    color: '#111111',
    marginTop: 2, // Slight adjustment for Poppins baseline
  },
  scannerButton: {
    padding: 8,
    marginLeft: 4,
  },
  filterButton: {
    width: 52,
    height: 52,
    backgroundColor: '#704F38',
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
});
