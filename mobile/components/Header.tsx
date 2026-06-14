import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors, typography, spacing, dimensions } from '../constants/theme';

interface HeaderProps {
  firstName?: string;
  title?: string;
  showBackBtn?: boolean;
  onBackPress?: () => void;
  hasUnreadNotifications?: boolean;
  onNotificationPress?: () => void;
}

export default function Header({ 
  firstName, 
  title,
  showBackBtn = false,
  onBackPress,
  hasUnreadNotifications = false,
  onNotificationPress 
}: HeaderProps) {
  return (
    <View style={styles.container}>
      {/* Left Icon */}
      {showBackBtn ? (
        <TouchableOpacity style={styles.iconButton} onPress={onBackPress}>
          <Ionicons name="arrow-back-outline" size={20} color={colors.gray900} />
        </TouchableOpacity>
      ) : (
        <TouchableOpacity style={styles.iconButton}>
          <Ionicons name="grid-outline" size={20} color={colors.gray900} />
        </TouchableOpacity>
      )}
      
      {/* Greeting / Title */}
      <View style={styles.greetingContainer}>
        {title ? (
          <Text style={styles.title}>{title}</Text>
        ) : firstName ? (
          <Text style={styles.greeting}>Hello {firstName}!</Text>
        ) : null}
      </View>
      
      {/* Right Action Icons */}
      <View style={styles.rightActions}>
        <TouchableOpacity onPress={() => console.log('Profile clicked')}>
          <Image 
            source={{ uri: 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=100&h=100&fit=crop' }} 
            style={styles.profilePic} 
          />
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    height: dimensions.header.height + 10,
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    backgroundColor: 'transparent',
  },
  iconButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: colors.gray100,
    justifyContent: 'center',
    alignItems: 'center',
  },
  greetingContainer: {
    flex: 1,
    marginLeft: spacing.md,
  },
  greeting: {
    fontSize: typography.fontSize.h2,
    fontWeight: typography.fontWeight.semibold,
    color: colors.gray900,
  },
  title: {
    fontSize: typography.fontSize.h2,
    fontWeight: typography.fontWeight.bold,
    color: colors.gray900,
  },
  rightActions: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  profilePic: {
    width: 44,
    height: 44,
    borderRadius: 22,
  },
});
