import { useEffect, useState } from 'react';
import { Redirect } from 'expo-router';
import { authStorage } from '../lib/authStorage';
import { View, Text, StyleSheet, Dimensions } from 'react-native';

const { width } = Dimensions.get('window');

export default function Index() {
  const [authState, setAuthState] = useState<'loading' | 'unauthenticated' | 'authenticated_incomplete' | 'authenticated_notifications_pending' | 'authenticated_complete'>('loading');

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = await authStorage.getItemAsync('token');
        const profileCompleted = await authStorage.getItemAsync('profile_completed');
        const notificationsOptIn = await authStorage.getItemAsync('notifications_opt_in');
        
        // Small delay to show the nice splash screen
        setTimeout(() => {
          if (token) {
            if (profileCompleted !== 'true') {
              setAuthState('authenticated_incomplete');
            } else if (notificationsOptIn !== 'true') {
              setAuthState('authenticated_notifications_pending');
            } else {
              setAuthState('authenticated_complete');
            }
          } else {
            setAuthState('unauthenticated');
          }
        }, 1500);
      } catch (error) {
        setAuthState('unauthenticated');
      }
    };
    checkAuth();
  }, []);

  // Show loading screen while checking auth
  if (authState === 'loading') {
    return (
      <View style={styles.container}>
        {/* Decorative Top Right Circle */}
        <View style={[styles.circle, styles.topRightCircle]} />
        
        {/* Decorative Bottom Left Circle */}
        <View style={[styles.circle, styles.bottomLeftCircle]} />

        {/* Logo Container */}
        <View style={styles.logoContainer}>
          <View style={styles.iconCircle}>
            <Text style={styles.iconText}>f</Text>
          </View>
          <Text style={styles.brandText}>
            fashion<Text style={styles.brandDot}>.</Text>
          </Text>
        </View>
      </View>
    );
  }

  // Redirect based on auth status
  if (authState === 'unauthenticated') {
    return <Redirect href="/(auth)/welcome" />;
  } else if (authState === 'authenticated_incomplete') {
    return <Redirect href="/(auth)/complete-profile" />;
  } else if (authState === 'authenticated_notifications_pending') {
    return <Redirect href="/(auth)/notifications-prompt" />;
  }
  
  return <Redirect href="/(tabs)/home" />;
}

const circleSize = width * 0.7;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    justifyContent: 'center',
    alignItems: 'center',
  },
  circle: {
    position: 'absolute',
    width: circleSize,
    height: circleSize,
    borderRadius: circleSize / 2,
    borderWidth: 1,
    borderColor: '#EDEDED',
  },
  topRightCircle: {
    top: -circleSize * 0.25,
    right: -circleSize * 0.25,
  },
  bottomLeftCircle: {
    bottom: -circleSize * 0.25,
    left: -circleSize * 0.25,
  },
  logoContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  iconCircle: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: '#704F38',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 10,
  },
  iconText: {
    color: '#FFFFFF',
    fontSize: 40,
    fontFamily: 'serif', // using serif since the logo 'f' has serifs
    fontWeight: 'bold',
    includeFontPadding: false,
    textAlignVertical: 'center',
    marginTop: -4,
  },
  brandText: {
    color: '#1F2029',
    fontSize: 42,
    fontFamily: 'serif', // using serif since the logo text has serifs
    fontWeight: 'bold',
    letterSpacing: -1.5,
  },
  brandDot: {
    color: '#704F38',
  },
});
