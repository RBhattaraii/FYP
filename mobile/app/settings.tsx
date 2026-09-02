import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Platform, Modal, TextInput, ActivityIndicator, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Stack, useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { authStorage } from '../lib/authStorage';
import { deleteAccount } from '../services/api';

export default function SettingsScreen() {
  const router = useRouter();
  
  const handleBack = () => {
    if (router.canGoBack()) {
      router.back();
    } else {
      router.replace('/(tabs)/profile');
    }
  };
  
  const [isPasswordModalVisible, setPasswordModalVisible] = useState(false);
  const [isConfirmModalVisible, setConfirmModalVisible] = useState(false);
  const [password, setPassword] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);

  const handleNext = () => {
    if (!password) {
      Alert.alert('Error', 'Please enter your password');
      return;
    }
    setPasswordModalVisible(false);
    setTimeout(() => {
      setConfirmModalVisible(true);
    }, 500); // slight delay to allow first modal to close smoothly
  };

  const handleConfirmDelete = async () => {
    const token = await authStorage.getItemAsync('token');
    if (!token) return;
    setIsDeleting(true);
    try {
      await deleteAccount(token, password);
      setConfirmModalVisible(false);
      Alert.alert('Account Deleted', 'Your account has been permanently deleted.', [
        { 
          text: 'OK', 
          onPress: async () => {
            await authStorage.deleteItemAsync('token');
            await authStorage.deleteItemAsync('email');
            await authStorage.deleteItemAsync('full_name');
            router.replace('/login');
          } 
        }
      ]);
    } catch (error: any) {
      setIsDeleting(false);
      setConfirmModalVisible(false);
      Alert.alert('Error', error.message || 'Failed to delete account');
      setPassword('');
    }
  };

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <Stack.Screen options={{ headerShown: false }} />
      
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity style={styles.headerIcon} onPress={handleBack}>
          <Ionicons name="arrow-back" size={24} color="#111111" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Settings</Text>
        <View style={styles.headerPlaceholder} />
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        {/* Personal Information */}
        <TouchableOpacity style={styles.row} activeOpacity={0.7} onPress={() => router.push('/personal-info')}>
          <View style={styles.rowLeft}>
            <Ionicons name="person-outline" size={24} color="#6E4B3A" />
            <Text style={styles.rowText}>Personal Information</Text>
          </View>
          <Ionicons name="chevron-forward" size={20} color="#111111" />
        </TouchableOpacity>
        <View style={styles.divider} />

        {/* Password Manager */}
        <TouchableOpacity style={styles.row} activeOpacity={0.7} onPress={() => router.push('/password-manager')}>
          <View style={styles.rowLeft}>
            <Ionicons name="key-outline" size={24} color="#6E4B3A" />
            <Text style={styles.rowText}>Password Manager</Text>
          </View>
          <Ionicons name="chevron-forward" size={20} color="#111111" />
        </TouchableOpacity>
        <View style={styles.divider} />

        {/* Delete Account */}
        <TouchableOpacity style={styles.row} activeOpacity={0.7} onPress={() => setPasswordModalVisible(true)}>
          <View style={styles.rowLeft}>
            <Ionicons name="card-outline" size={24} color="#6E4B3A" />
            <Text style={styles.rowText}>Delete Account</Text>
          </View>
          <Ionicons name="chevron-forward" size={20} color="#111111" />
        </TouchableOpacity>
      </ScrollView>

      {/* Password Modal */}
      <Modal visible={isPasswordModalVisible} transparent animationType="fade">
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Enter Password</Text>
            <Text style={styles.modalText}>Please enter your password to proceed with account deletion.</Text>
            
            <TextInput
              style={styles.input}
              placeholder="••••••••"
              placeholderTextColor="#999"
              secureTextEntry
              value={password}
              onChangeText={setPassword}
              autoFocus
            />

            <View style={styles.modalButtons}>
              <TouchableOpacity style={styles.modalCancelButton} onPress={() => { setPasswordModalVisible(false); setPassword(''); }}>
                <Text style={styles.modalCancelText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.modalConfirmButton} onPress={handleNext}>
                <Text style={styles.modalConfirmText}>Next</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>

      {/* Confirmation Modal */}
      <Modal visible={isConfirmModalVisible} transparent animationType="fade">
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Ionicons name="warning" size={48} color="#FF3B30" style={{ alignSelf: 'center', marginBottom: 16 }} />
            <Text style={styles.modalTitle}>Are you sure?</Text>
            <Text style={styles.modalText}>Do you really want to permanently delete your account? This action cannot be undone.</Text>
            
            <View style={styles.modalButtons}>
              <TouchableOpacity style={styles.modalCancelButton} onPress={() => { setConfirmModalVisible(false); setPassword(''); }} disabled={isDeleting}>
                <Text style={styles.modalCancelText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity style={[styles.modalConfirmButton, { backgroundColor: '#FF3B30' }]} onPress={handleConfirmDelete} disabled={isDeleting}>
                {isDeleting ? <ActivityIndicator color="#FFF" /> : <Text style={styles.modalConfirmText}>Delete</Text>}
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    paddingTop: Platform.OS === 'android' ? 25 : 0,
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
    fontSize: 18,
    color: '#111111',
  },
  headerPlaceholder: {
    width: 44,
  },
  content: {
    paddingHorizontal: 24,
    paddingTop: 16,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 16,
  },
  rowLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  rowText: {
    fontFamily: 'Poppins_400Regular',
    fontSize: 17,
    color: '#111111',
    marginLeft: 16,
  },
  divider: {
    height: 1,
    backgroundColor: '#F5F5F5',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  modalContent: {
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    padding: 24,
    width: '100%',
  },
  modalTitle: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 20,
    color: '#111111',
    marginBottom: 12,
    textAlign: 'center',
  },
  modalText: {
    fontFamily: 'Poppins_400Regular',
    fontSize: 14,
    color: '#666666',
    marginBottom: 24,
    textAlign: 'center',
    lineHeight: 22,
  },
  input: {
    backgroundColor: '#F5F5F5',
    borderRadius: 12,
    paddingHorizontal: 16,
    height: 50,
    fontFamily: 'Poppins_400Regular',
    fontSize: 14,
    color: '#111',
    marginBottom: 24,
  },
  modalButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  modalCancelButton: {
    flex: 1,
    height: 50,
    borderRadius: 25,
    borderWidth: 1,
    borderColor: '#EAEAEA',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 8,
  },
  modalCancelText: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 16,
    color: '#111111',
  },
  modalConfirmButton: {
    flex: 1,
    height: 50,
    borderRadius: 25,
    backgroundColor: '#8B5A2B',
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: 8,
  },
  modalConfirmText: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 16,
    color: '#FFFFFF',
  },
});
