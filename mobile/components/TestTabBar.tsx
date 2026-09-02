import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Platform } from 'react-native';
import { BottomTabBarProps } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

export default function TestTabBar({ state, descriptors, navigation }: BottomTabBarProps) {
  const insets = useSafeAreaInsets();

  console.log('========================================');
  console.log('TestTabBar RENDERING');
  console.log('Current route index:', state.index);
  console.log('Routes:', state.routes.map(r => r.name));
  console.log('Bottom inset:', insets.bottom);
  console.log('========================================');

  const testPress = () => {
    console.log('BANNER TAPPED!!!');
  };

  return (
    <View 
      style={[styles.container, { 
        paddingBottom: Platform.OS === 'ios' ? Math.max(insets.bottom, 20) : Math.max(insets.bottom, 10) 
      }]}
    >
      <TouchableOpacity 
        style={styles.debugBanner} 
        onPress={testPress}
        activeOpacity={0.5}
      >
        <Text style={styles.debugText}>TAB BAR - TAP ME!</Text>
      </TouchableOpacity>
      <View style={styles.tabRow}>
        {state.routes.map((route, index) => {
        const isFocused = state.index === index;
        const label = route.name;

        const handlePress = () => {
          console.log('========================================');
          console.log('TAB PRESSED:', route.name);
          console.log('Was focused:', isFocused);
          console.log('========================================');
          
          const event = navigation.emit({
            type: 'tabPress',
            target: route.key,
            canPreventDefault: true,
          });

          if (!isFocused && !event.defaultPrevented) {
            console.log('NAVIGATING TO:', route.name);
            navigation.navigate(route.name);
          } else {
            console.log('Navigation prevented or already focused');
          }
        };

        let iconName = 'circle';
        if (route.name === 'home') iconName = 'home';
        if (route.name === 'explore') iconName = 'search';
        if (route.name === 'offers') iconName = 'pricetag';
        if (route.name === 'wishlist') iconName = 'heart';
        if (route.name === 'profile') iconName = 'person';

        return (
          <TouchableOpacity
            key={route.key}
            onPress={handlePress}
            style={[styles.tabItem, isFocused && styles.tabItemFocused]}
          >
            <Ionicons 
              name={iconName as any} 
              size={24} 
              color={isFocused ? '#FF6B00' : '#666'} 
            />
            <Text style={[styles.label, isFocused && styles.labelFocused]}>
              {label}
            </Text>
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
    bottom: 0,
    left: 0,
    right: 0,
    flexDirection: 'column',
    backgroundColor: '#FF0000',
    borderTopWidth: 3,
    borderTopColor: '#00FF00',
    paddingTop: 10,
    paddingHorizontal: 10,
    elevation: 999,
    zIndex: 999,
    ...Platform.select({
      web: {
        boxShadow: '0px -2px 10px rgba(0, 0, 0, 0.5)',
      },
      default: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: -2 },
        shadowOpacity: 0.5,
        shadowRadius: 10,
      },
    }) as any,
  },
  debugBanner: {
    backgroundColor: '#FFFF00',
    padding: 5,
    marginBottom: 5,
    alignItems: 'center',
  },
  debugText: {
    color: '#FF0000',
    fontWeight: 'bold',
    fontSize: 16,
  },
  tabRow: {
    flexDirection: 'row',
    backgroundColor: '#FFFFFF',
  },
  tabItem: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 8,
  },
  tabItemFocused: {
    backgroundColor: 'rgba(255, 107, 0, 0.1)',
    borderRadius: 8,
  },
  label: {
    fontSize: 10,
    marginTop: 4,
    color: '#666',
  },
  labelFocused: {
    color: '#FF6B00',
    fontWeight: 'bold',
  },
});
