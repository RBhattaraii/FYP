import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Platform } from 'react-native';
import { BottomTabBarProps } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { colors, spacing, borderRadius, shadows } from '../constants/theme';

export default function CustomTabBar({ state, descriptors, navigation }: BottomTabBarProps) {
  const insets = useSafeAreaInsets();

  return (
    <View style={[styles.container, { bottom: Platform.OS === 'ios' ? 30 : 20 + insets.bottom }]}>
      <View style={styles.tabBar}>
        {state.routes.map((route, index) => {
          const { options } = descriptors[route.key];
          const isFocused = state.index === index;
          const label = options.title !== undefined ? options.title : route.name;

          const onPress = () => {
            const event = navigation.emit({
              type: 'tabPress',
              target: route.key,
              canPreventDefault: true,
            });

            if (!isFocused && !event.defaultPrevented) {
              navigation.navigate(route.name);
            }
          };

          const onLongPress = () => {
            navigation.emit({
              type: 'tabLongPress',
              target: route.key,
            });
          };

          let iconName = '';
          if (route.name === 'home') iconName = isFocused ? 'home' : 'home-outline';
          if (route.name === 'notifications') iconName = isFocused ? 'wallet' : 'wallet-outline';
          if (route.name === 'wishlist') iconName = isFocused ? 'compass' : 'compass-outline';
          if (route.name === 'profile') iconName = isFocused ? 'person-circle' : 'person-circle-outline';

          return (
            <TouchableOpacity
              key={route.key}
              accessibilityRole="button"
              accessibilityState={isFocused ? { selected: true } : {}}
              accessibilityLabel={options.tabBarAccessibilityLabel}
              onPress={onPress}
              onLongPress={onLongPress}
              style={[styles.tabItem, isFocused && styles.tabItemFocused]}
            >
              <Ionicons 
                name={iconName as any} 
                size={22} 
                color={isFocused ? colors.white : colors.gray900} 
              />
              {isFocused && (
                <Text style={styles.tabText}>
                  {label}
                </Text>
              )}
            </TouchableOpacity>
          );
        })}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    left: 0,
    right: 0,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'transparent',
    paddingHorizontal: spacing.lg,
  },
  tabBar: {
    flexDirection: 'row',
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    borderRadius: borderRadius.full,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    justifyContent: 'space-between',
    alignItems: 'center',
    width: '100%',
    ...shadows.featuredCard,
    borderWidth: 1,
    borderColor: 'rgba(0,0,0,0.05)',
  },
  tabItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    borderRadius: borderRadius.full,
    marginHorizontal: spacing.xs,
  },
  tabItemFocused: {
    backgroundColor: colors.warningOrange, // using warningOrange from theme to mimic the yellow/gold
  },
  tabText: {
    color: colors.white,
    fontWeight: 'bold',
    marginLeft: spacing.xs,
    fontSize: 14,
  },
});
