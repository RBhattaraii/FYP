/**
 * PricePilot Design System
 * Theme constants for consistent styling across the app
 */

// Color Palette
export const colors = {
  // Primary Colors
  white: '#FFFFFF',
  primary: '#2563EB',
  primaryDark: '#1D4ED8',
  
  // Neutral Colors
  gray50: '#F9FAFB',
  gray100: '#F3F4F6',
  gray200: '#E5E7EB',
  gray300: '#D1D5DB',
  gray400: '#9CA3AF',
  gray600: '#4B5563',
  gray900: '#111827',
  
  // Semantic Colors
  successGreen: '#10B981',
  warningOrange: '#F59E0B',
  errorRed: '#EF4444',
  
  // Badge Colors
  badgeRed: '#EF4444',
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
  card: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  featuredCard: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.08,
    shadowRadius: 12,
    elevation: 4,
  },
  button: {
    shadowColor: '#2563EB',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.15,
    shadowRadius: 6,
    elevation: 3,
  },
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
    width: 160,
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
