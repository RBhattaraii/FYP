import { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  ScrollView,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter, Stack } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { API_URL, fetchWithTimeout } from '../../constants/api';
import { authStorage } from '../../lib/authStorage';
import { useEffect } from 'react';
import { BackHandler } from 'react-native';

export default function CompleteProfileScreen() {
  const router = useRouter();

  // Prevent hardware back press
  useEffect(() => {
    const onBackPress = () => true; // returning true disables the back button
    const subscription = BackHandler.addEventListener('hardwareBackPress', onBackPress);
    return () => subscription.remove();
  }, []);
  
  // State for form inputs
  const [nickname, setNickname] = useState('');
  const [dob, setDob] = useState('');
  const [phone, setPhone] = useState('');
  const [gender, setGender] = useState('');
  
  // State for UI
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState('');

  const handleContinue = async () => {
    setLoading(true);
    setApiError('');
    
    try {
      if (phone.trim()) await authStorage.setItemAsync('phone', phone.trim());
      
      // Mark profile as completed
      await authStorage.setItemAsync('profile_completed', 'true');
      
      // Artificial delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Redirect to index so the root routing logic (notifications) kicks in
      router.replace('/');
    } catch (error: any) {
      console.log('❌ Error completing profile:', error.message);
      setApiError('Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSkip = () => {
    // Navigate to root to continue the auth flow without marking profile as completed
    router.replace('/');
  };

  return (
    <SafeAreaView style={styles.safeArea} edges={['top', 'bottom']}>
      <Stack.Screen options={{ headerShown: false }} />
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.flex}
      >
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          keyboardShouldPersistTaps="handled"
          showsVerticalScrollIndicator={false}
        >
          {/* Header */}
          <View style={styles.header}>
            <Text style={styles.title}>Fill Your Profile</Text>
            <TouchableOpacity onPress={handleSkip} style={styles.skipButton}>
              <Text style={styles.skipText}>Skip</Text>
            </TouchableOpacity>
          </View>

          {/* Avatar Section */}
          <View style={styles.avatarSection}>
            <View style={styles.avatarContainer}>
              <View style={styles.avatarPlaceholder}>
                <Ionicons name="person" size={70} color="#E0E0E0" />
              </View>
              <TouchableOpacity style={styles.editAvatarButton} activeOpacity={0.8}>
                <Ionicons name="pencil" size={14} color="#FFFFFF" />
              </TouchableOpacity>
            </View>
          </View>

          {/* API Error Message */}
          {apiError ? (
            <View style={styles.errorBanner}>
              <Ionicons name="alert-circle" size={18} color="#EF4444" />
              <Text style={styles.errorBannerText}>{apiError}</Text>
            </View>
          ) : null}

          <View style={styles.formContainer}>


            {/* Nickname */}
            <View style={styles.inputBox}>
              <TextInput
                style={styles.input}
                placeholder="Nickname"
                placeholderTextColor="#9E9E9E"
                value={nickname}
                onChangeText={setNickname}
                autoCapitalize="words"
                editable={!loading}
              />
            </View>

            {/* Date of Birth */}
            <TouchableOpacity style={styles.inputBox} activeOpacity={0.7}>
              <TextInput
                style={styles.input}
                placeholder="Date of Birth"
                placeholderTextColor="#9E9E9E"
                value={dob}
                editable={false}
              />
              <Ionicons name="calendar-outline" size={20} color="#9E9E9E" />
            </TouchableOpacity>



            {/* Phone Number */}
            <View style={styles.inputBox}>
              <TouchableOpacity style={styles.countryCodeSelector} activeOpacity={0.7}>
                <Text style={styles.flagEmoji}>🇺🇸</Text>
                <Ionicons name="chevron-down" size={14} color="#111111" style={styles.chevron} />
              </TouchableOpacity>
              
              <TextInput
                style={styles.input}
                placeholder="+1 111 467 378 399"
                placeholderTextColor="#9E9E9E"
                value={phone}
                onChangeText={setPhone}
                keyboardType="phone-pad"
                editable={!loading}
              />
            </View>

            {/* Gender */}
            <TouchableOpacity 
              style={styles.inputBox}
              activeOpacity={0.7}
              onPress={() => setGender(gender === 'Male' ? 'Female' : 'Male')}
            >
              <Text style={[styles.input, { color: gender ? '#111111' : '#9E9E9E' }]}>
                {gender || 'Gender'}
              </Text>
              <Ionicons name="caret-down" size={18} color="#9E9E9E" />
            </TouchableOpacity>
          </View>

          <View style={styles.bottomSpacer} />

          {/* Continue Button */}
          <TouchableOpacity
            style={[styles.primaryButton, loading && styles.primaryButtonDisabled]}
            onPress={handleContinue}
            disabled={loading}
            activeOpacity={0.8}
          >
            {loading ? (
              <ActivityIndicator color="#FFF" />
            ) : (
              <Text style={styles.primaryButtonText}>Continue</Text>
            )}
          </TouchableOpacity>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  flex: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    paddingHorizontal: 24,
    paddingTop: 20,
    paddingBottom: 40,
  },
  
  // ── Header ──
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 40,
  },
  backButton: {
    marginRight: 16,
  },
  title: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 22,
    color: '#111111',
  },
  skipButton: {
    padding: 8,
  },
  skipText: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 16,
    color: '#704F38',
  },

  // ── Avatar Section ──
  avatarSection: {
    alignItems: 'center',
    marginBottom: 40,
  },
  avatarContainer: {
    position: 'relative',
  },
  avatarPlaceholder: {
    width: 140,
    height: 140,
    borderRadius: 70,
    backgroundColor: '#F5F5F5',
    justifyContent: 'center',
    alignItems: 'center',
    overflow: 'hidden',
  },
  editAvatarButton: {
    position: 'absolute',
    bottom: 8,
    right: 8,
    width: 32,
    height: 32,
    borderRadius: 8, // Rounded square
    backgroundColor: '#704F38',
    borderWidth: 2,
    borderColor: '#FFFFFF',
    justifyContent: 'center',
    alignItems: 'center',
  },

  // ── Error Banner ──
  errorBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FEF2F2',
    padding: 12,
    borderRadius: 12,
    marginBottom: 20,
    gap: 8,
  },
  errorBannerText: {
    flex: 1,
    color: '#EF4444',
    fontFamily: 'Poppins_400Regular',
    fontSize: 13,
  },

  // ── Form Fields ──
  formContainer: {
    gap: 20,
  },
  inputBox: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FAFAFA', // Light grey fill, no borders
    borderRadius: 16,
    paddingHorizontal: 20,
    height: 56,
  },
  input: {
    flex: 1,
    fontFamily: 'Poppins_500Medium',
    fontSize: 14,
    color: '#111111',
  },
  
  // ── Phone Input Specific ──
  countryCodeSelector: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 12,
  },
  flagEmoji: {
    fontSize: 18,
  },
  chevron: {
    marginLeft: 6,
  },

  bottomSpacer: {
    height: 40,
  },

  // ── Primary Button ──
  primaryButton: {
    backgroundColor: '#704F38',
    height: 56,
    borderRadius: 28, // Pill shape
    justifyContent: 'center',
    alignItems: 'center',
  },
  primaryButtonDisabled: {
    backgroundColor: '#9E9E9E',
  },
  primaryButtonText: {
    color: '#FFFFFF',
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 16,
  },
});
