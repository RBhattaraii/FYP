import React from 'react';
import { View, Text, StyleSheet, Image, TouchableOpacity, Dimensions, ScrollView } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import Svg, { Path } from 'react-native-svg';

const SCREEN_W = Dimensions.get('window').width;
const SCREEN_H = Dimensions.get('window').height;

// Collage geometry calculations
const COLLAGE_HEIGHT = SCREEN_H * 0.56;

// Top Right Oval
const TR_OVAL_W = SCREEN_W * 0.43;
const TR_OVAL_H = TR_OVAL_W * 1.25;
const TR_OVAL_X = SCREEN_W * 0.53; // Gap of 0.06
const TR_OVAL_Y = COLLAGE_HEIGHT * 0.05;

// Bottom Right Circle
const BR_CIRCLE_SIZE = SCREEN_W * 0.43;
const BR_CIRCLE_X = SCREEN_W * 0.53;
const BR_CIRCLE_Y = TR_OVAL_Y + TR_OVAL_H + (SCREEN_W * 0.04); // Vertical gap

// Left Capsule (tall again, top-aligned with oval, bottom-aligned with circle)
const CAPSULE_W = SCREEN_W * 0.43;
const CAPSULE_X = SCREEN_W * 0.04;
const CAPSULE_Y = TR_OVAL_Y;
const CAPSULE_H = (BR_CIRCLE_Y + BR_CIRCLE_SIZE) - CAPSULE_Y;

// Asterisk
const ASTERISK_SIZE = 44;

export default function WelcomeScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();

  return (
    <View style={[styles.container, { paddingTop: insets.top, paddingBottom: insets.bottom + 40 }]}>
      {/* Decorative background lines/arcs */}
      <View style={styles.bgArcTopLeft} />
      <View style={styles.bgArcMidRight} />

      {/* ── Image Collage (absolute positioned) ── */}
      <View style={styles.collageArea}>
        {/* Left capsule image */}
        <View style={[styles.capsule, { 
          width: CAPSULE_W, 
          height: CAPSULE_H, 
          left: CAPSULE_X, 
          top: CAPSULE_Y 
        }]}>
          <Image
            source={require('../../assets/images/welcome-1.png')}
            style={styles.imageFill}
            resizeMode="cover"
          />
        </View>

        {/* Top right oval image */}
        <View style={[styles.capsule, { 
          width: TR_OVAL_W, 
          height: TR_OVAL_H, 
          left: TR_OVAL_X, 
          top: TR_OVAL_Y 
        }]}>
          <Image
            source={require('../../assets/images/welcome-2.png')}
            style={styles.imageFill}
            resizeMode="cover"
          />
        </View>

        {/* Bottom right circle image */}
        <View style={[styles.circle, { 
          width: BR_CIRCLE_SIZE, 
          height: BR_CIRCLE_SIZE, 
          left: BR_CIRCLE_X, 
          top: BR_CIRCLE_Y 
        }]}>
          <Image
            source={require('../../assets/images/welcome-3.png')}
            style={styles.imageFill}
            resizeMode="cover"
          />
        </View>

        {/* Asterisk Icon (floating at bottom left of capsule) */}
        <View style={[styles.asteriskContainer, {
          left: CAPSULE_X - (ASTERISK_SIZE * 0.4),
          top: CAPSULE_Y + CAPSULE_H - (ASTERISK_SIZE * 1.2),
          width: ASTERISK_SIZE,
          height: ASTERISK_SIZE,
        }]}>
          <Svg width="100%" height="100%" viewBox="0 0 24 24">
            <Path
              fill="currentColor"
              d="M12 2L12 22M2 12L22 12M5 5L19 19M5 19L19 5"
              stroke="#704F38"
              strokeWidth="2.5"
              strokeLinecap="round"
            />
          </Svg>
        </View>
      </View>

      {/* ── Text + CTA Section ── */}
      <ScrollView 
        style={{ flex: 1 }} 
        contentContainerStyle={styles.bottomSectionScroll}
        showsVerticalScrollIndicator={false}
        bounces={false}
      >
        <Text style={styles.title}>
          The <Text style={styles.titleAccent}>Smart Way</Text> To{'\n'}Shop And Save
        </Text>
        
        <Text style={styles.subtitle}>
          Compare prices across top e-commerce stores in Nepal and find the best deals instantly.
        </Text>

        <TouchableOpacity 
          style={styles.button}
          onPress={() => router.push('/(auth)/register')}
          activeOpacity={0.8}
        >
          <Text style={styles.buttonText}>Let's Get Started</Text>
        </TouchableOpacity>

        <View style={[styles.signInRow, { paddingBottom: 20 }]}>
          <Text style={styles.signInText}>Already have an account? </Text>
          <TouchableOpacity onPress={() => router.push('/(auth)/login')} activeOpacity={0.7}>
            <Text style={styles.signInLink}>Sign In</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  
  // ── Background Arcs ──
  bgArcTopLeft: {
    position: 'absolute',
    width: SCREEN_W * 1.5,
    height: SCREEN_W * 1.5,
    borderRadius: 9999,
    borderWidth: 1,
    borderColor: '#EAEAEA',
    top: -SCREEN_W * 1.1,
    left: -SCREEN_W * 0.5,
  },
  bgArcMidRight: {
    position: 'absolute',
    width: SCREEN_W * 1.2,
    height: SCREEN_W * 1.2,
    borderRadius: 9999,
    borderWidth: 1,
    borderColor: '#EAEAEA',
    top: SCREEN_H * 0.35,
    left: SCREEN_W * 0.4,
  },

  // ── Collage ──
  collageArea: {
    height: COLLAGE_HEIGHT,
    width: '100%',
    position: 'relative',
  },
  capsule: {
    position: 'absolute',
    borderRadius: 9999,
    overflow: 'hidden',
    backgroundColor: '#F5F5F5',
  },
  circle: {
    position: 'absolute',
    borderRadius: 9999,
    overflow: 'hidden',
    backgroundColor: '#F5F5F5',
  },
  imageFill: {
    width: '100%',
    height: '100%',
  },
  asteriskContainer: {
    position: 'absolute',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 999,
    padding: 6, // creates the white cutout effect around the asterisk
  },

  // ── Bottom section ──
  bottomSectionScroll: {
    flexGrow: 1,
    alignItems: 'center',
    justifyContent: 'flex-start',
    paddingHorizontal: 28,
    paddingTop: 10,
  },
  title: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 26, // Reduced slightly to prevent awkward wrap on small screens
    color: '#1F2029',
    textAlign: 'center',
    marginBottom: 16,
    lineHeight: 34,
  },
  titleAccent: {
    color: '#704F38',
  },
  subtitle: {
    fontFamily: 'Poppins_400Regular',
    fontSize: 13,
    color: '#797979',
    textAlign: 'center',
    lineHeight: 20,
    marginBottom: 35,
    paddingHorizontal: 15,
  },
  button: {
    width: '100%',
    height: 56,
    backgroundColor: '#704F38',
    borderRadius: 28,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 25,
  },
  buttonText: {
    color: '#FFF',
    fontSize: 16,
    fontFamily: 'Poppins_600SemiBold',
  },
  signInRow: {
    flexDirection: 'row',
  },
  signInText: {
    fontSize: 14,
    color: '#1F2029',
    fontFamily: 'Poppins_400Regular',
  },
  signInLink: {
    fontSize: 14,
    color: '#704F38',
    fontFamily: 'Poppins_600SemiBold',
    textDecorationLine: 'underline',
  },
});
