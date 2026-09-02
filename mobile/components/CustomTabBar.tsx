import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Animated, Dimensions } from 'react-native';
import { BottomTabBarProps } from '@react-navigation/bottom-tabs';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { colors, spacing, borderRadius, shadows } from '../constants/theme';

interface TabBarItemProps {
  route: any;
  options: any;
  isFocused: boolean;
  onPress: () => void;
  onLongPress: () => void;
}

function TabBarItem({ route, options, isFocused, onPress, onLongPress }: TabBarItemProps) {
  let iconName = 'ellipse-outline';
  if (route.name === 'home') iconName = isFocused ? 'home' : 'home-outline';
  if (route.name === 'explore') iconName = isFocused ? 'storefront' : 'storefront-outline';
  if (route.name === 'favorites' || route.name === 'wishlist') iconName = isFocused ? 'heart' : 'heart-outline';
  if (route.name === 'profile') iconName = isFocused ? 'person' : 'person-outline';

  // Individual tab item animations
  const scaleAnim = React.useRef(new Animated.Value(isFocused ? 1.1 : 1)).current;

  React.useEffect(() => {
    Animated.spring(scaleAnim, {
      toValue: isFocused ? 1.1 : 1,
      useNativeDriver: true,
      damping: 12,
      mass: 0.8,
      stiffness: 140,
    }).start();
  }, [isFocused]);

  return (
    <TouchableOpacity
      accessibilityRole="button"
      accessibilityState={isFocused ? { selected: true } : {}}
      accessibilityLabel={options.tabBarAccessibilityLabel}
      testID={options.tabBarTestID}
      onPress={onPress}
      onLongPress={onLongPress}
      style={styles.tabItem}
      activeOpacity={0.8}
    >
      <Animated.View style={[styles.iconContainer, isFocused && styles.iconContainerActive, { transform: [{ scale: scaleAnim }] }]}>
        <Ionicons
          name={iconName as any}
          size={24}
          color={isFocused ? '#704F38' : '#FFFFFF'}
        />
      </Animated.View>
    </TouchableOpacity>
  );
}

export default function CustomTabBar({ state, descriptors, navigation }: BottomTabBarProps) {
  const insets = useSafeAreaInsets();
  const currentRouteName = state.routes[state.index]?.name;

  // Hide footer completely on the admin screen.
  if (currentRouteName === 'admin') {
    return null;
  }

  const visibleRoutes = state.routes.filter((route) => route.name !== 'admin' && route.name !== 'offers');
  const [containerWidth, setContainerWidth] = React.useState(0);
  const tabWidth = containerWidth ? containerWidth / visibleRoutes.length : 0;
  
  const translateX = React.useRef(new Animated.Value(0)).current;

  React.useEffect(() => {
    if (tabWidth > 0) {
      Animated.spring(translateX, {
        toValue: state.index * tabWidth,
        useNativeDriver: true,
        damping: 15,
        mass: 1,
        stiffness: 120,
      }).start();
    }
  }, [state.index, tabWidth]);

  return (
    <View 
      style={[
        styles.wrapper, 
        { bottom: Math.max(insets.bottom, 16) }
      ]}
      onLayout={(e) => {
        setContainerWidth(e.nativeEvent.layout.width);
      }}
    > 
      <View style={styles.tabBar}>
        {/* Animated Sliding Pill */}
        {tabWidth > 0 && (
          <Animated.View 
            style={[
              styles.activeIndicator,
              {
                width: tabWidth - spacing.md * 2,
                left: spacing.md,
                transform: [{ translateX }]
              }
            ]}
          />
        )}

        {visibleRoutes.map((route, index) => {
          const { options } = descriptors[route.key];
          const isFocused = route.name === currentRouteName;

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

          return (
            <TabBarItem
              key={route.key}
              route={route}
              options={options}
              isFocused={isFocused}
              onPress={onPress}
              onLongPress={onLongPress}
            />
          );
        })}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: {
    position: 'absolute',
    left: '5%',
    right: '5%',
    width: '90%',
    borderRadius: 9999,
    backgroundColor: '#704F38', // Theme background
    ...shadows.glow,
    overflow: 'hidden',
  },
  tabBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 8,
    minHeight: 70,
    position: 'relative',
  },
  activeIndicator: {
    display: 'none', // We use individual icon container backgrounds instead
  },
  tabItem: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  iconContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'transparent',
  },
  iconContainerActive: {
    backgroundColor: '#F5EBE1',
  },
});
