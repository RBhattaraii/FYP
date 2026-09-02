import { View, Text, FlatList, TouchableOpacity, RefreshControl, StyleSheet, Platform, SafeAreaView } from 'react-native';
import { useEffect, useState, useMemo } from 'react';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { authStorage } from '../lib/authStorage';
import { getNotifications, markNotificationRead, markAllNotificationsRead, Notification, getLocalNotifications, markLocalNotificationRead, markAllLocalNotificationsRead } from '../services/notifications';

export default function NotificationsScreen() {
  const router = useRouter();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadNotifications();
  }, []);

  const loadNotifications = async () => {
    try {
      const token = await authStorage.getItemAsync('token');
      const local = await getLocalNotifications();
      let remote: Notification[] = [];
      let remoteUnreadCount = 0;
      
      if (token) {
        try {
          const data = await getNotifications(token);
          remote = data.notifications;
          remoteUnreadCount = data.unread_count;
        } catch (e) {
          console.warn('Failed to load remote notifications');
        }
      }

      // Merge and sort
      const merged = [...remote, ...local].sort(
        (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      );
      
      setNotifications(merged);
      const localUnreadCount = local.filter(n => !n.is_read).length;
      setUnreadCount(remoteUnreadCount + localUnreadCount);
    } catch (error) {
      console.error('Load notifications error:', error);
      setNotifications([]);
      setUnreadCount(0);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = () => {
    setRefreshing(true);
    loadNotifications();
  };

  const handleNotificationPress = async (notification: Notification) => {
    try {
      const token = await authStorage.getItemAsync('token');

      if (!notification.is_read) {
        if (notification.user_id === 'local') {
          await markLocalNotificationRead(notification.id);
        } else if (token) {
          await markNotificationRead(token, notification.id);
        }
        
        setNotifications(prev =>
          prev.map(n => n.id === notification.id ? { ...n, is_read: true } : n)
        );
        setUnreadCount(prev => Math.max(0, prev - 1));
      }

      if (notification.product_id) {
        router.push(`/product/${notification.product_id}`);
      }
    } catch (error) {
      console.error('Mark notification read error:', error);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      const token = await authStorage.getItemAsync('token');

      await markAllLocalNotificationsRead();
      if (token) {
        await markAllNotificationsRead(token);
      }
      
      setNotifications(prev =>
        prev.map(n => ({ ...n, is_read: true }))
      );
      setUnreadCount(0);
    } catch (error) {
      console.error('Mark all read error:', error);
    }
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'price_alert':
      case 'flash_sale':
        return 'pricetag-outline';
      case 'order':
        return 'cube-outline'; // using cube for packages
      case 'payment':
        return 'wallet-outline';
      case 'people-outline':
        return 'people-outline';
      case 'review':
        return 'star-outline';
      case 'favorite':
        return 'heart-outline';
      case 'system':
      default:
        return 'notifications-outline';
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (hours < 24) return `${Math.max(1, hours)}h`;
    return `${days}d`;
  };

  // Group notifications for the UI
  const groupedData = useMemo(() => {
    const today: Notification[] = [];
    const yesterday: Notification[] = [];
    
    const now = new Date();
    
    notifications.forEach(n => {
      const date = new Date(n.created_at);
      const diffTime = Math.abs(now.getTime() - date.getTime());
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)); 
      
      if (diffDays <= 1) {
        today.push(n);
      } else {
        yesterday.push(n);
      }
    });

    return [
      { title: 'TODAY', data: today },
      { title: 'YESTERDAY', data: yesterday }
    ].filter(section => section.data.length > 0);
  }, [notifications]);

  const renderNotification = (item: Notification) => (
    <TouchableOpacity
      key={item.id}
      style={[
        styles.notificationRow,
        !item.is_read && styles.unreadNotification
      ]}
      onPress={() => handleNotificationPress(item)}
      activeOpacity={0.7}
    >
      <View style={styles.iconContainer}>
        <Ionicons
          name={getNotificationIcon(item.notification_type) as any}
          size={20}
          color="#6E4B3A"
        />
      </View>

      <View style={styles.notificationContent}>
        <View style={styles.notificationHeader}>
          <Text style={styles.notificationTitle}>{item.title}</Text>
          <Text style={styles.notificationTime}>{formatDate(item.created_at)}</Text>
        </View>
        <Text style={styles.notificationMessage} numberOfLines={3}>
          {item.message || 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'}
        </Text>
      </View>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.container}>
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity onPress={() => router.back()} style={styles.headerIcon}>
            <Ionicons name="arrow-back" size={20} color="#111111" />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Notification</Text>
          {unreadCount > 0 ? (
            <View style={styles.badge}>
              <Text style={styles.badgeText}>{unreadCount} NEW</Text>
            </View>
          ) : (
            <View style={styles.headerPlaceholder} />
          )}
        </View>

        <FlatList
          data={groupedData}
          keyExtractor={(item) => item.title}
          contentContainerStyle={styles.listContent}
          showsVerticalScrollIndicator={false}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
          }
          renderItem={({ item: section }) => (
            <View style={styles.sectionContainer}>
              <View style={styles.sectionHeader}>
                <Text style={styles.sectionTitle}>{section.title}</Text>
                {section.title === 'TODAY' && unreadCount > 0 && (
                  <TouchableOpacity onPress={handleMarkAllRead}>
                    <Text style={styles.markAllRead}>Mark all as read</Text>
                  </TouchableOpacity>
                )}
              </View>
              {section.data.map(renderNotification)}
            </View>
          )}
          ListEmptyComponent={
            !loading ? (
              <View style={styles.emptyContainer}>
                <Ionicons name="notifications-off-outline" size={64} color="#D1D1D1" />
                <Text style={styles.emptyText}>No notifications yet</Text>
              </View>
            ) : null
          }
        />
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#FAFAFA',
    paddingTop: Platform.OS === 'android' ? 25 : 0,
  },
  container: {
    flex: 1,
    backgroundColor: '#FAFAFA',
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
  badge: {
    backgroundColor: '#6E4B3A',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
  },
  badgeText: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 10,
    color: '#FFFFFF',
  },
  headerPlaceholder: {
    width: 44,
  },
  listContent: {
    paddingBottom: 40,
  },
  sectionContainer: {
    marginBottom: 24,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 24,
    marginBottom: 16,
    marginTop: 8,
  },
  sectionTitle: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 12,
    color: '#9E9E9E',
    letterSpacing: 1,
  },
  markAllRead: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 12,
    color: '#6E4B3A',
  },
  notificationRow: {
    flexDirection: 'row',
    paddingHorizontal: 24,
    paddingVertical: 16,
    backgroundColor: '#FAFAFA',
    borderBottomWidth: 1,
    borderBottomColor: '#F5F5F5',
  },
  unreadNotification: {
    backgroundColor: '#FFFFFF',
  },
  iconContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#F5F5F5',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  notificationContent: {
    flex: 1,
  },
  notificationHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  notificationTitle: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 15,
    color: '#111111',
    flex: 1,
  },
  notificationTime: {
    fontFamily: 'Poppins_400Regular',
    fontSize: 12,
    color: '#9E9E9E',
    marginLeft: 8,
  },
  notificationMessage: {
    fontFamily: 'Poppins_400Regular',
    fontSize: 13,
    color: '#757575',
    lineHeight: 18,
  },
  emptyContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 120,
  },
  emptyText: {
    fontFamily: 'Poppins_400Regular',
    fontSize: 16,
    color: '#9E9E9E',
    marginTop: 16,
  },
});
