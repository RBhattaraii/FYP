import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ImageBackground } from 'react-native';
import { colors, typography, spacing, borderRadius } from '../constants/theme';
import { LinearGradient } from 'expo-linear-gradient';

interface FullImageCardProps {
  title: string;
  subtitle: string;
  imageUrl: string;
  onPress: () => void;
  width?: number;
  height?: number;
}

export default function FullImageCard({
  title,
  subtitle,
  imageUrl,
  onPress,
  width = 240,
  height = 240,
}: FullImageCardProps) {
  return (
    <TouchableOpacity
      style={[styles.container, { width, height }]}
      onPress={onPress}
      activeOpacity={0.8}
    >
      <ImageBackground
        source={{ uri: imageUrl }}
        style={styles.imageBackground}
        imageStyle={styles.image}
      >
        <LinearGradient
          colors={['rgba(0,0,0,0.4)', 'rgba(0,0,0,0.1)', 'rgba(0,0,0,0.6)']}
          style={styles.gradient}
        >
          <View style={styles.content}>
            <Text style={styles.subtitle} numberOfLines={1}>{subtitle}</Text>
            <Text style={styles.title} numberOfLines={2}>{title}</Text>
          </View>
        </LinearGradient>
      </ImageBackground>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: {
    borderRadius: borderRadius.large,
    overflow: 'hidden',
  },
  imageBackground: {
    width: '100%',
    height: '100%',
  },
  image: {
    borderRadius: borderRadius.large,
  },
  gradient: {
    flex: 1,
    padding: spacing.lg,
    justifyContent: 'flex-start',
  },
  content: {
    marginTop: spacing.sm,
  },
  subtitle: {
    color: 'rgba(255,255,255,0.9)',
    fontSize: typography.fontSize.caption,
    fontWeight: typography.fontWeight.semibold,
    marginBottom: spacing.xs,
  },
  title: {
    color: colors.white,
    fontSize: typography.fontSize.h3,
    fontWeight: typography.fontWeight.bold,
  },
});
