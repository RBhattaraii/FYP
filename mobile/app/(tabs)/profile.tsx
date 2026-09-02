import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image, ScrollView, ActivityIndicator, Platform, Alert, Modal } from 'react-native';
import { SafeAreaView, useSafeAreaInsets } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { authStorage } from '../../lib/authStorage';
import { useFocusEffect } from '@react-navigation/native';
import { fetchUserProfile } from '../../services/api';

// Using a male profile image that closely matches the user's screenshot
const DEFAULT_AVATAR = 'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=200&h=200&fit=crop';

const PROFILE_OPTIONS = [
  { id: 'alerts', icon: 'notifications-outline', label: 'Price Alerts', route: '/price-alerts' },
  { id: 'stores', icon: 'storefront-outline', label: 'Preferred Stores', route: '/preferred-stores' },
  { id: 'settings', icon: 'settings-outline', label: 'Settings', route: '/settings' },
  { id: 'help', icon: 'help-circle-outline', label: 'Help Center', route: '/help-center' },
  { id: 'privacy', icon: 'shield-checkmark-outline', label: 'Privacy Policy', route: '/privacy-policy' },
];

export default function ProfileScreen() {
  const router = useRouter();
  const [userName, setUserName] = React.useState('Loading...');
  const [loading, setLoading] = React.useState(true);
  const [logoutModalVisible, setLogoutModalVisible] = React.useState(false);
  const insets = useSafeAreaInsets();

  useFocusEffect(
    React.useCallback(() => {
      loadUserName();
    }, [])
  );

  const loadUserName = async () => {
    try {
      setLoading(false);
      
      const storedEmail = await authStorage.getItemAsync('email');
      const storedName = await authStorage.getItemAsync('full_name');
      
      if (storedEmail) {
        if (storedName) {
          setUserName(storedName);
        } else {
          const namePart = storedEmail.split('@')[0];
          setUserName(namePart.charAt(0).toUpperCase() + namePart.slice(1));
        }
      }

      const token = await authStorage.getItemAsync('token');
      if (token) {
        try {
          const profileData = await fetchUserProfile(token);
          if (profileData) {
            setUserName(profileData.full_name || 'User');
            await authStorage.setItemAsync('email', profileData.email);
            if (profileData.full_name) {
              await authStorage.setItemAsync('full_name', profileData.full_name);
            }
          }
        } catch (error: any) {
          if (error.message && error.message.includes('401')) {
            await authStorage.deleteItemAsync('token');
            router.replace('/(auth)/login');
            return;
          }
        }
      }
    } catch (error) {
      console.error('Failed to load user profile:', error);
      setLoading(false);
    }
  };

  const handleChangePicture = () => {
    Alert.alert(
      "Change Profile Picture",
      "Where would you like to choose your new photo from?",
      [
        { text: "Camera", onPress: () => console.log("Camera chosen") },
        { text: "Gallery", onPress: () => console.log("Gallery chosen") },
        { text: "Cancel", style: "cancel" }
      ]
    );
  };

  const confirmLogout = async () => {
    setLogoutModalVisible(false);
    try {
      await authStorage.deleteItemAsync('token');
      await authStorage.deleteItemAsync('email');
      await authStorage.deleteItemAsync('rememberMe');
      await authStorage.deleteItemAsync('savedEmail');
      await authStorage.deleteItemAsync('full_name');
      await authStorage.deleteItemAsync('phone');
    } catch (error) {
      console.error('Error clearing logout storage:', error);
    }
    router.replace('/(auth)/login');
  };

  const handleLogoutPress = () => {
    setLogoutModalVisible(true);
  };

  return (
    <SafeAreaView style={[styles.safeArea, { paddingTop: Platform.OS === 'ios' ? Math.max(insets.top - 15, 20) : insets.top }]} edges={['right', 'bottom', 'left']}>
      <View style={styles.header}>
        <TouchableOpacity style={styles.headerIcon} onPress={() => router.canGoBack() ? router.back() : router.replace('/')}>
          <Ionicons name="arrow-back" size={20} color="#111111" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Profile</Text>
        <View style={styles.headerPlaceholder} />
      </View>

      <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={styles.scrollContent}>
        
        {/* Profile Picture & Edit Icon */}
        <View style={styles.profileSection}>
          <View style={styles.avatarContainer}>
            <Image source={{ uri: DEFAULT_AVATAR }} style={styles.avatar} />
            <TouchableOpacity style={styles.editAvatarBtn} activeOpacity={0.8} onPress={handleChangePicture}>
              <Ionicons name="pencil" size={14} color="#FFFFFF" />
            </TouchableOpacity>
          </View>
          
          {loading ? (
            <ActivityIndicator size="small" color="#6E4B3A" style={{ marginTop: 16 }} />
          ) : (
            <Text style={styles.userName}>{userName}</Text>
          )}

          {/* Quick Actions (Points & Checkout) */}
          <View style={styles.quickActionsContainer}>
            <TouchableOpacity 
              style={styles.quickActionCard}
              activeOpacity={0.8}
              onPress={() => router.push('/points')}
            >
              <View style={[styles.quickActionIconCircle, { backgroundColor: '#FFF5F0' }]}>
                <Ionicons name="star-outline" size={24} color="#FF6B35" />
              </View>
              <Text style={styles.quickActionText}>Points</Text>
            </TouchableOpacity>

            <TouchableOpacity 
              style={styles.quickActionCard}
              activeOpacity={0.8}
              onPress={() => router.push('/mock-checkout')}
            >
              <View style={[styles.quickActionIconCircle, { backgroundColor: '#F0F9FF' }]}>
                <Ionicons name="cart-outline" size={24} color="#0EA5E9" />
              </View>
              <Text style={styles.quickActionText}>Checkout</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Options List */}
        <View style={styles.optionsContainer}>
          {PROFILE_OPTIONS.map((option, index) => (
            <View key={option.id}>
              <TouchableOpacity 
                style={styles.optionRow}
                activeOpacity={0.7}
                onPress={() => option.route ? router.push(option.route as any) : null}
              >
                <View style={styles.optionIconLeft}>
                  <Ionicons name={option.icon as any} size={22} color="#6E4B3A" />
                </View>
                <Text style={styles.optionLabel}>{option.label}</Text>
                <Ionicons name="chevron-forward" size={20} color="#111111" />
              </TouchableOpacity>
              <View style={styles.divider} />
            </View>
          ))}
          
          {/* Logout Option */}
          <TouchableOpacity 
            style={styles.optionRow}
            activeOpacity={0.7}
            onPress={handleLogoutPress}
          >
            <View style={styles.optionIconLeft}>
              <Ionicons name="log-out-outline" size={22} color="#6E4B3A" style={{ transform: [{ scaleX: -1 }] }} />
            </View>
            <Text style={styles.optionLabel}>Log out</Text>
            <Ionicons name="chevron-forward" size={20} color="#111111" />
          </TouchableOpacity>
          <View style={styles.divider} />
        </View>

      </ScrollView>

      {/* Logout Bottom Sheet Modal */}
      <Modal
        visible={logoutModalVisible}
        transparent={true}
        animationType="slide"
        onRequestClose={() => setLogoutModalVisible(false)}
      >
        <TouchableOpacity 
          style={styles.modalOverlay} 
          activeOpacity={1} 
          onPress={() => setLogoutModalVisible(false)}
        >
          <TouchableOpacity 
            activeOpacity={1} 
            style={styles.bottomSheet}
          >
            <View style={styles.bottomSheetHandle} />
            <Text style={styles.logoutTitle}>Logout</Text>
            <View style={styles.logoutDivider} />
            <Text style={styles.logoutMessage}>Are you sure you want to log out?</Text>
            
            <View style={styles.logoutActionRow}>
              <TouchableOpacity 
                style={styles.cancelBtn} 
                onPress={() => setLogoutModalVisible(false)}
              >
                <Text style={styles.cancelBtnText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity 
                style={styles.confirmLogoutBtn} 
                onPress={confirmLogout}
              >
                <Text style={styles.confirmLogoutBtnText}>Yes, Logout</Text>
              </TouchableOpacity>
            </View>
          </TouchableOpacity>
        </TouchableOpacity>
      </Modal>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#FAFAFA', // Matching the off-white background
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 24,
    paddingBottom: 16,
    paddingTop: 8,
  },
  headerIcon: {
    width: 44,
    height: 44,
    borderRadius: 22,
    borderWidth: 1,
    borderColor: '#EEEEEE',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
  },
  headerTitle: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 16,
    color: '#111111',
  },
  headerPlaceholder: {
    width: 44,
  },
  scrollContent: {
    paddingBottom: 120, // Space for the floating bottom bar
  },
  profileSection: {
    alignItems: 'center',
    marginTop: 24,
    marginBottom: 40,
  },
  avatarContainer: {
    position: 'relative',
    marginBottom: 16,
  },
  avatar: {
    width: 100,
    height: 100,
    borderRadius: 50,
  },
  editAvatarBtn: {
    position: 'absolute',
    bottom: 0,
    right: 0,
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#6E4B3A',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#FAFAFA',
  },
  userName: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 18,
    color: '#111111',
  },
  quickActionsContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 16,
    width: '100%',
    paddingHorizontal: 24,
    marginTop: 24,
  },
  quickActionCard: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    paddingVertical: 20,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  quickActionIconCircle: {
    width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  quickActionText: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 14,
    color: '#111111',
  },
  optionsContainer: {
    paddingHorizontal: 24,
  },
  optionRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 18,
  },
  optionIconLeft: {
    marginRight: 16,
    width: 24,
    alignItems: 'center',
  },
  optionLabel: {
    flex: 1,
    fontFamily: 'Poppins_500Medium',
    fontSize: 16,
    color: '#111111',
  },
  divider: {
    height: 1,
    backgroundColor: '#F0F0F0',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.4)',
    justifyContent: 'flex-end',
  },
  bottomSheet: {
    backgroundColor: '#FFFFFF',
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    paddingHorizontal: 24,
    paddingBottom: Platform.OS === 'ios' ? 40 : 24,
    paddingTop: 12,
    alignItems: 'center',
  },
  bottomSheetHandle: {
    width: 40,
    height: 4,
    backgroundColor: '#E0E0E0',
    borderRadius: 2,
    marginBottom: 20,
  },
  logoutTitle: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 18,
    color: '#111111',
    marginBottom: 16,
  },
  logoutDivider: {
    width: '100%',
    height: 1,
    backgroundColor: '#F0F0F0',
    marginBottom: 24,
  },
  logoutMessage: {
    fontFamily: 'Poppins_400Regular',
    fontSize: 16,
    color: '#757575',
    marginBottom: 32,
  },
  logoutActionRow: {
    flexDirection: 'row',
    gap: 16,
    width: '100%',
  },
  cancelBtn: {
    flex: 1,
    paddingVertical: 16,
    borderRadius: 9999,
    borderWidth: 1,
    borderColor: '#6E4B3A',
    alignItems: 'center',
    justifyContent: 'center',
  },
  cancelBtnText: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 16,
    color: '#6E4B3A',
  },
  confirmLogoutBtn: {
    flex: 1,
    paddingVertical: 16,
    borderRadius: 9999,
    backgroundColor: '#6E4B3A',
    alignItems: 'center',
    justifyContent: 'center',
  },
  confirmLogoutBtnText: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 16,
    color: '#FFFFFF',
  }
});
