import { Tabs } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { colors, typography, dimensions } from '../../constants/theme';
import CustomTabBar from '../../components/CustomTabBar';

export default function TabsLayout() {
  return (
    <Tabs
      tabBar={(props) => <CustomTabBar {...props} />}
      screenOptions={{
        headerShown: false,
      }}
    >
      <Tabs.Screen 
        name="home" 
        options={{ 
          title: 'Home',
          tabBarIcon: ({ color, focused }) => (
            <Ionicons 
              name={focused ? 'home' : 'home-outline'} 
              size={24} 
              color={color} 
            />
          ),
        }} 
      />
      <Tabs.Screen 
        name="notifications" 
        options={{ 
          title: 'Barcode',
          tabBarIcon: ({ color, focused }) => (
            <Ionicons 
              name={focused ? 'barcode' : 'barcode-outline'} 
              size={24} 
              color={color} 
            />
          ),
        }} 
      />
      <Tabs.Screen 
        name="wishlist" 
        options={{ 
          title: 'Saved Deals',
          tabBarIcon: ({ color, focused }) => (
            <Ionicons 
              name={focused ? 'bookmark' : 'bookmark-outline'} 
              size={24} 
              color={color} 
            />
          ),
        }} 
      />
      <Tabs.Screen 
        name="profile" 
        options={{ 
          title: 'Profile',
          tabBarIcon: ({ color, focused }) => (
            <Ionicons 
              name={focused ? 'person-circle' : 'person-circle-outline'} 
              size={24} 
              color={color} 
            />
          ),
        }} 
      />
    </Tabs>
  );
}
