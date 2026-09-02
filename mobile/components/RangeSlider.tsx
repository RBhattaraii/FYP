import React, { useRef, useState } from 'react';
import { View, StyleSheet, PanResponder, Animated, Text, Dimensions } from 'react-native';

const KNOB_SIZE = 24;
const PADDING_HORIZONTAL = 48; // 24 on each side from FilterModal
const SLIDER_WIDTH = Dimensions.get('window').width - PADDING_HORIZONTAL - KNOB_SIZE;

export default function RangeSlider({ 
  min = 0, 
  max = 1600000, 
  step = 1000,
  initialMin = 0,
  initialMax = 1600000,
  onValuesChange 
}: { 
  min?: number; 
  max?: number; 
  step?: number;
  initialMin?: number;
  initialMax?: number;
  onValuesChange: (min: number, max: number) => void;
}) {
  const [minVal, setMinVal] = useState(initialMin);
  const [maxVal, setMaxVal] = useState(initialMax);

  const getPositionFromValue = (value: number) => {
    return ((value - min) / (max - min)) * SLIDER_WIDTH;
  };

  const minPos = useRef(new Animated.Value(getPositionFromValue(initialMin))).current;
  const maxPos = useRef(new Animated.Value(getPositionFromValue(initialMax))).current;

  const startMinPosRef = useRef(getPositionFromValue(initialMin));
  const startMaxPosRef = useRef(getPositionFromValue(initialMax));
  
  const currentMinPosRef = useRef(startMinPosRef.current);
  const currentMaxPosRef = useRef(startMaxPosRef.current);

  const currentMinValRef = useRef(initialMin);
  const currentMaxValRef = useRef(initialMax);

  const calculateValue = (pos: number) => {
    const ratio = pos / SLIDER_WIDTH;
    let val = min + ratio * (max - min);
    val = Math.round(val / step) * step;
    return Math.min(Math.max(val, min), max);
  };

  const updateMin = (pos: number) => {
    pos = Math.min(Math.max(pos, 0), currentMaxPosRef.current - KNOB_SIZE);
    minPos.setValue(pos);
    currentMinPosRef.current = pos;
    const val = calculateValue(pos);
    currentMinValRef.current = val;
    setMinVal(val);
  };

  const updateMax = (pos: number) => {
    pos = Math.min(Math.max(pos, currentMinPosRef.current + KNOB_SIZE), SLIDER_WIDTH);
    maxPos.setValue(pos);
    currentMaxPosRef.current = pos;
    const val = calculateValue(pos);
    currentMaxValRef.current = val;
    setMaxVal(val);
  };

  const minPanResponder = useRef(PanResponder.create({
    onStartShouldSetPanResponder: () => true,
    onStartShouldSetPanResponderCapture: () => true,
    onMoveShouldSetPanResponder: () => true,
    onMoveShouldSetPanResponderCapture: () => true,
    onPanResponderTerminationRequest: () => false,
    onPanResponderGrant: () => {
      startMinPosRef.current = currentMinPosRef.current;
    },
    onPanResponderMove: (e, gestureState) => {
      updateMin(startMinPosRef.current + gestureState.dx);
    },
    onPanResponderRelease: () => {
      onValuesChange(currentMinValRef.current, currentMaxValRef.current);
    }
  })).current;

  const maxPanResponder = useRef(PanResponder.create({
    onStartShouldSetPanResponder: () => true,
    onStartShouldSetPanResponderCapture: () => true,
    onMoveShouldSetPanResponder: () => true,
    onMoveShouldSetPanResponderCapture: () => true,
    onPanResponderTerminationRequest: () => false,
    onPanResponderGrant: () => {
      startMaxPosRef.current = currentMaxPosRef.current;
    },
    onPanResponderMove: (e, gestureState) => {
      updateMax(startMaxPosRef.current + gestureState.dx);
    },
    onPanResponderRelease: () => {
      onValuesChange(currentMinValRef.current, currentMaxValRef.current);
    }
  })).current;

  return (
    <View style={styles.container}>
      <Text style={styles.label}>
        Rs {minVal.toLocaleString()} - Rs {maxVal.toLocaleString()}
      </Text>
      <View style={styles.trackWrapper}>
        <View style={styles.trackContainer}>
          <View style={styles.track} />
          <Animated.View 
            style={[
              styles.activeTrack,
              {
                left: minPos,
                width: Animated.subtract(maxPos, minPos)
              }
            ]} 
          />
        </View>
        
        <Animated.View 
          style={[styles.knob, { left: minPos }]} 
          {...minPanResponder.panHandlers} 
        />
        <Animated.View 
          style={[styles.knob, { left: maxPos }]} 
          {...maxPanResponder.panHandlers} 
        />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    paddingVertical: 8,
  },
  label: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 14,
    color: '#757575',
    marginBottom: 20,
  },
  trackWrapper: {
    position: 'relative',
    height: KNOB_SIZE,
    justifyContent: 'center',
    width: SLIDER_WIDTH + KNOB_SIZE,
  },
  trackContainer: {
    position: 'absolute',
    left: KNOB_SIZE / 2,
    right: KNOB_SIZE / 2,
    height: 4,
    justifyContent: 'center',
  },
  track: {
    height: 4,
    backgroundColor: '#EEEEEE',
    borderRadius: 2,
    width: '100%',
    position: 'absolute',
  },
  activeTrack: {
    height: 4,
    backgroundColor: '#6E4B3A',
    borderRadius: 2,
    position: 'absolute',
  },
  knob: {
    width: KNOB_SIZE,
    height: KNOB_SIZE,
    borderRadius: KNOB_SIZE / 2,
    backgroundColor: '#6E4B3A',
    position: 'absolute',
    top: 0,
    shadowColor: '#6E4B3A',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 5,
  }
});
