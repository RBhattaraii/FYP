/**
 * PricePilot Design System
 * Theme constants for consistent styling across the app
 */
import { Platform, ViewStyle } from 'react-native';

// Color Palette
export const colors = {
  // Primary Colors
  white: '#FFFFFF',
  primary: '#FF5A36',      // Vibrant sunset orange
  primaryDark: '#DE3E1B',  // Deep coral dark
  primaryIndigo: '#4F46E5', // Sleek high-tech Indigo
  primaryIndigoLight: '#818CF8',

  // Glassmorphic Colors
  glassWhite: 'rgba(255, 255, 255, 0.85)',
  glassWhiteHeavy: 'rgba(255, 255, 255, 0.92)',
  glassBorder: 'rgba(255, 255, 255, 0.4)',
  glassBorderDark: 'rgba(0, 0, 0, 0.05)',
  
  // Neutral Colors
  gray50: '#F8FAFC',
  gray100: '#F1F5F9',
  gray200: '#E2E8F0',
  gray300: '#CBD5E1',
  gray400: '#94A3B8',
  gray500: '#64748B',
  gray600: '#475569',
  gray700: '#334155',
  gray900: '#0F172A',
  
  // Semantic Colors
  successGreen: '#10B981',
  warningOrange: '#F59E0B',
  errorRed: '#EF4444',
  
  // Badge Colors
  badgeRed: '#EF4444',
  
  // Extended Colors for Price History Feature
  blue50: '#EFF6FF',
  blue200: '#BFDBFE',
  green50: '#F0FDF4',
  green200: '#BBF7D0',
};

// Typography
export const typography = {
  fontFamily: {
    primary: 'System', // SF Pro Display on iOS, Roboto on Android
  },
  fontSize: {
    h1: 28,
    h2: 20,
    h3: 16,
    bodyLarge: 16,
    body: 14,
    small: 13,
    caption: 12,
    button: 16,
  },
  fontWeight: {
    regular: '400' as const,
    medium: '500' as const,
    semibold: '600' as const,
    bold: '700' as const,
  },
  lineHeight: {
    h1: 34,
    h2: 24,
    h3: 19,
    bodyLarge: 24,
    body: 21,
    caption: 18,
    button: 21,
  },
};

// Spacing System (base unit: 4px)
export const spacing = {
  xs: 4,
  sm: 8,
  md: 12,
  base: 16,
  lg: 20,
  xl: 24,
  xxl: 56,
  '2xl': 32,
  '3xl': 40,
  '4xl': 48,
};

// Border Radius
export const borderRadius = {
  small: 8,
  medium: 12,
  large: 16,
  full: 9999,
};

// Shadows
export const shadows = {
  card: Platform.select({
    web: {
      boxShadow: '0px 10px 30px rgba(15, 23, 42, 0.05), 0px 2px 8px rgba(15, 23, 42, 0.02)',
    },
    default: {
      shadowColor: '#0F172A',
      shadowOffset: { width: 0, height: 10 },
      shadowOpacity: 0.05,
      shadowRadius: 30,
      elevation: 4,
    },
  }),
  featuredCard: Platform.select({
    web: {
      boxShadow: '0px 20px 40px rgba(15, 23, 42, 0.08), 0px 4px 12px rgba(15, 23, 42, 0.03)',
    },
    default: {
      shadowColor: '#0F172A',
      shadowOffset: { width: 0, height: 20 },
      shadowOpacity: 0.08,
      shadowRadius: 40,
      elevation: 8,
    },
  }),
  button: Platform.select({
    web: {
      boxShadow: '0px 8px 24px rgba(255, 90, 54, 0.22)',
    },
    default: {
      shadowColor: '#FF5A36',
      shadowOffset: { width: 0, height: 8 },
      shadowOpacity: 0.22,
      shadowRadius: 24,
      elevation: 6,
    },
  }),
  // Extra glow for active navigation floating elements
  glow: Platform.select({
    web: {
      boxShadow: '0px 10px 30px rgba(79, 70, 229, 0.15)',
    },
    default: {
      shadowColor: '#4F46E5',
      shadowOffset: { width: 0, height: 10 },
      shadowOpacity: 0.15,
      shadowRadius: 30,
      elevation: 8,
    },
  }),
};

// Component Dimensions
export const dimensions = {
  header: {
    height: 60,
  },
  searchBar: {
    height: 48,
  },
  categoryPill: {
    height: 40,
  },
  trendingCard: {
    width: 172,
    height: 200,
  },
  recommendedCard: {
    width: 280,
    height: 140,
  },
  bottomTab: {
    height: 64,
  },
  touchTarget: {
    min: 44,
  },
};
