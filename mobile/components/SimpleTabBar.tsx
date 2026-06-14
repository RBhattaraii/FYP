import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Platform, Pressable, Button, Alert } from 'react-native';
import { BottomTabBarProps } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

export default function SimpleTabBar({ state, descriptors, navigation }: BottomTabBarProps) {
  const insets = useSafeAreaInsets();

  const testAlert = () => {
    Alert.alert('SUCCESS!', 'Tab bar is receiving touches!');
    console.log('🎉🎉🎉 ALERT BUTTON PRESSED! 🎉🎉🎉');
  };

  return (
    <View style={[styles.container, { 
      paddingBottom: Platform.OS === 'ios' ? insets.bottom : 10 
    }]}>
      <Button title="TEST - PRESS ME" onPress={testAlert} color="#FF0000" />
      
      {state.routes.map((route, index) => {
        const isFocused = state.index === index;

        const onPress = () => {
          console.log('🔥🔥🔥 TAB PRESSED:', route.name, '🔥🔥🔥');
          Alert.alert('Tab Pressed', `You pressed ${route.name}`);
          
          const event = navigation.emit({
            type: 'tabPress',
            target: route.key,
            canPreventDefault: true,
          });

          if (!isFocused && !event.defaultPrevented) {
            console.log('NAVIGATING TO:', route.name);
            navigation.navigate(route.name);
          }
        };

        const onPressIn = () => {
          console.log('👆 PRESS IN:', route.name);
        };

        const onPressOut = () => {
          console.log('👋 PRESS OUT:', route.name);
        };

        let iconName = 'circle';
        if (route.name === 'home') iconName = isFocused ? 'home' : 'home-outline';
        if (route.name === 'explore') iconName = isFocused ? 'search' : 'search-outline';
        if (route.name === 'offers') iconName = isFocused ? 'pricetag' : 'pricetag-outline';
        if (route.name === 'wishlist') iconName = isFocused ? 'heart' : 'heart-outline';
        if (route.name === 'profile') iconName = isFocused ? 'person-circle' : 'person-circle-outline';

        return (
          <Pressable
            key={route.key}
            onPress={onPress}
            onPressIn={onPressIn}
            onPressOut={onPressOut}
            style={({ pressed }) => [
              styles.tab,
              pressed && styles.tabPressed,
              isFocused && styles.tabFocused,
            ]}
          >
            <Ionicons 
              name={iconName as any} 
              size={26} 
              color={isFocused ? '#FF6B00' : '#666'} 
            />
            <Text style={[styles.label, isFocused && styles.labelActive]}>
              {route.name}
            </Text>
          </Pressable>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    backgroundColor: '#FFFF00',
    borderTopWidth: 5,
    borderTopColor: '#FF0000',
    paddingTop: 8,
    paddingHorizontal: 8,
    minHeight: 80,
  },
  tab: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 10,
    backgroundColor: '#FFFFFF',
    marginHorizontal: 2,
    borderRadius: 8,
  },
  tabPressed: {
    backgroundColor: '#CCCCCC',
  },
  tabFocused: {
    backgroundColor: '#FFE5CC',
  },
  label: {
    fontSize: 11,
    marginTop: 4,
    color: '#666',
    fontWeight: '500',
  },
  labelActive: {
    color: '#FF6B00',
    fontWeight: '600',
  },
});
