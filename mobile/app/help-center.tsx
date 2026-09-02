import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Platform, TextInput, LayoutAnimation, UIManager } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Stack, useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';

// Enable layout animation on Android
if (Platform.OS === 'android') {
  if (UIManager.setLayoutAnimationEnabledExperimental) {
    UIManager.setLayoutAnimationEnabledExperimental(true);
  }
}

const FAQS = [
  {
    id: 1,
    question: "Can I track my order's delivery status?",
    answer: "Yes, once your order is placed, you can track it by going to the 'Orders' section in your profile and tapping on the specific order to see its real-time status.",
    category: "Services"
  },
  {
    id: 2,
    question: "Is there a return policy?",
    answer: "We offer a 30-day return policy for most items. If you are not satisfied, you can initiate a return from your order history. Items must be in original condition.",
    category: "General"
  },
  {
    id: 3,
    question: "Can I save my favorite items for later?",
    answer: "Absolutely! Just tap the heart icon on any product page to add it to your wishlist. You can view your saved items anytime from your profile.",
    category: "Account"
  },
  {
    id: 4,
    question: "Can I share products with my friends?",
    answer: "Yes, you can use the share icon on the product details page to send a link to your friends via WhatsApp, Messages, or social media.",
    category: "General"
  },
  {
    id: 5,
    question: "How do I contact customer support?",
    answer: "You can reach us through the 'Contact Us' tab on this Help Center page. We offer support via phone, WhatsApp, and social media.",
    category: "Services"
  },
  {
    id: 6,
    question: "What payment methods are accepted?",
    answer: "We accept all major credit and debit cards, PayPal, and Apple/Google Pay. All transactions are securely encrypted.",
    category: "General"
  },
  {
    id: 7,
    question: "How to add a review?",
    answer: "Once you have received your order, go to your order history and select the delivered item. Tap 'Write a Review' to share your experience.",
    category: "Account"
  }
];

const CONTACT_METHODS = [
  { id: 'cs', icon: 'headset-outline', title: 'Customer Service', content: 'Call us at: 1-800-123-4567\nHours: Mon-Fri 9am-6pm EST' },
  { id: 'wa', icon: 'logo-whatsapp', title: 'WhatsApp', content: '(480) 555-0103' },
  { id: 'web', icon: 'globe-outline', title: 'Website', content: 'https://www.pricepilot.com' },
  { id: 'fb', icon: 'logo-facebook', title: 'Facebook', content: '@PricePilotOfficial' },
  { id: 'tw', icon: 'logo-twitter', title: 'Twitter', content: '@PricePilotApp' },
  { id: 'ig', icon: 'logo-instagram', title: 'Instagram', content: '@PricePilot' },
];

export default function HelpCenterScreen() {
  const router = useRouter();
  
  const handleBack = () => {
    if (router.canGoBack()) {
      router.back();
    } else {
      router.replace('/(tabs)/profile');
    }
  };
  const [activeTab, setActiveTab] = useState<'FAQ' | 'Contact'>('FAQ');
  const [searchQuery, setSearchQuery] = useState('');
  const [activeCategory, setActiveCategory] = useState('All');
  const [expandedFaqId, setExpandedFaqId] = useState<number | null>(1); // default expanded
  const [expandedContactId, setExpandedContactId] = useState<string | null>('wa'); // default expanded

  const categories = ['All', 'Services', 'General', 'Account'];

  const toggleFaq = (id: number) => {
    LayoutAnimation.configureNext(LayoutAnimation.Presets.easeInEaseOut);
    setExpandedFaqId(expandedFaqId === id ? null : id);
  };

  const toggleContact = (id: string) => {
    LayoutAnimation.configureNext(LayoutAnimation.Presets.easeInEaseOut);
    setExpandedContactId(expandedContactId === id ? null : id);
  };

  const filteredFaqs = FAQS.filter(faq => {
    const matchesCategory = activeCategory === 'All' || faq.category === activeCategory;
    const matchesSearch = faq.question.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <Stack.Screen options={{ headerShown: false }} />
      
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity style={styles.headerIcon} onPress={handleBack}>
          <Ionicons name="arrow-back" size={24} color="#111111" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Help Center</Text>
        <View style={styles.headerPlaceholder} />
      </View>

      {/* Search Bar */}
      <View style={styles.searchContainer}>
        <Ionicons name="search-outline" size={20} color="#666" style={styles.searchIcon} />
        <TextInput
          style={styles.searchInput}
          placeholder="Search"
          placeholderTextColor="#999"
          value={searchQuery}
          onChangeText={setSearchQuery}
        />
      </View>

      {/* Tabs */}
      <View style={styles.tabsContainer}>
        <TouchableOpacity 
          style={[styles.tab, activeTab === 'FAQ' && styles.activeTab]}
          onPress={() => setActiveTab('FAQ')}
        >
          <Text style={[styles.tabText, activeTab === 'FAQ' && styles.activeTabText]}>FAQ</Text>
        </TouchableOpacity>
        <TouchableOpacity 
          style={[styles.tab, activeTab === 'Contact' && styles.activeTab]}
          onPress={() => setActiveTab('Contact')}
        >
          <Text style={[styles.tabText, activeTab === 'Contact' && styles.activeTabText]}>Contact Us</Text>
        </TouchableOpacity>
      </View>

      <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
        
        {activeTab === 'FAQ' ? (
          <>
            {/* Categories */}
            <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.categoriesScroll} contentContainerStyle={{ paddingHorizontal: 24 }}>
              {categories.map((cat) => (
                <TouchableOpacity 
                  key={cat} 
                  style={[styles.categoryChip, activeCategory === cat && styles.activeCategoryChip]}
                  onPress={() => setActiveCategory(cat)}
                >
                  <Text style={[styles.categoryText, activeCategory === cat && styles.activeCategoryText]}>{cat}</Text>
                </TouchableOpacity>
              ))}
            </ScrollView>

            {/* FAQ List */}
            <View style={styles.listContainer}>
              {filteredFaqs.map((faq) => {
                const isExpanded = expandedFaqId === faq.id;
                return (
                  <View key={faq.id} style={styles.accordionItem}>
                    <TouchableOpacity style={styles.accordionHeader} onPress={() => toggleFaq(faq.id)} activeOpacity={0.7}>
                      <Text style={styles.accordionTitle}>{faq.question}</Text>
                      <Ionicons name={isExpanded ? "chevron-up" : "chevron-down"} size={20} color="#6E4B3A" />
                    </TouchableOpacity>
                    {isExpanded && (
                      <View style={styles.accordionContent}>
                        <Text style={styles.accordionText}>{faq.answer}</Text>
                      </View>
                    )}
                  </View>
                );
              })}
            </View>
          </>
        ) : (
          /* Contact Us List */
          <View style={[styles.listContainer, { paddingTop: 20 }]}>
            {CONTACT_METHODS.map((method) => {
              const isExpanded = expandedContactId === method.id;
              return (
                <View key={method.id} style={styles.accordionItem}>
                  <TouchableOpacity style={styles.accordionHeader} onPress={() => toggleContact(method.id)} activeOpacity={0.7}>
                    <View style={styles.contactHeaderLeft}>
                      <Ionicons name={method.icon as any} size={24} color="#6E4B3A" style={styles.contactIcon} />
                      <Text style={styles.accordionTitle}>{method.title}</Text>
                    </View>
                    <Ionicons name={isExpanded ? "chevron-up" : "chevron-down"} size={20} color="#111111" />
                  </TouchableOpacity>
                  {isExpanded && (
                    <View style={[styles.accordionContent, { paddingLeft: 48 }]}>
                      {method.id === 'wa' && <View style={styles.bulletPoint} />}
                      <Text style={[styles.accordionText, method.id === 'wa' && { marginLeft: 12 }]}>{method.content}</Text>
                    </View>
                  )}
                </View>
              );
            })}
          </View>
        )}
        
        <View style={{ height: 40 }} />
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FAFAFA',
    paddingTop: Platform.OS === 'android' ? 25 : 0,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 24,
    paddingBottom: 16,
    paddingTop: 8,
    backgroundColor: '#FAFAFA',
  },
  headerIcon: {
    width: 44,
    height: 44,
    borderRadius: 22,
    borderWidth: 1,
    borderColor: '#EAEAEA',
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
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#EAEAEA',
    borderRadius: 12,
    marginHorizontal: 24,
    paddingHorizontal: 16,
    height: 50,
    marginBottom: 20,
  },
  searchIcon: {
    marginRight: 10,
  },
  searchInput: {
    flex: 1,
    fontFamily: 'Poppins_400Regular',
    fontSize: 14,
    color: '#111',
    height: '100%',
  },
  tabsContainer: {
    flexDirection: 'row',
    borderBottomWidth: 1,
    borderBottomColor: '#EAEAEA',
    paddingHorizontal: 24,
  },
  tab: {
    flex: 1,
    paddingVertical: 12,
    alignItems: 'center',
    borderBottomWidth: 2,
    borderBottomColor: 'transparent',
  },
  activeTab: {
    borderBottomColor: '#6E4B3A',
  },
  tabText: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 15,
    color: '#999999',
  },
  activeTabText: {
    color: '#6E4B3A',
  },
  content: {
    flexGrow: 1,
  },
  categoriesScroll: {
    marginTop: 20,
    marginBottom: 20,
    maxHeight: 40,
  },
  categoryChip: {
    paddingHorizontal: 20,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: '#EAEAEA',
    marginRight: 12,
    height: 38,
    justifyContent: 'center',
  },
  activeCategoryChip: {
    backgroundColor: '#6E4B3A',
  },
  categoryText: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 14,
    color: '#111111',
  },
  activeCategoryText: {
    color: '#FFFFFF',
  },
  listContainer: {
    paddingHorizontal: 24,
  },
  accordionItem: {
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#EAEAEA',
    borderRadius: 12,
    marginBottom: 16,
    overflow: 'hidden',
  },
  accordionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
  },
  contactHeaderLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  contactIcon: {
    marginRight: 12,
  },
  accordionTitle: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 14,
    color: '#111111',
    flex: 1,
  },
  accordionContent: {
    paddingHorizontal: 16,
    paddingBottom: 16,
    flexDirection: 'row',
  },
  accordionText: {
    fontFamily: 'Poppins_400Regular',
    fontSize: 13,
    color: '#666666',
    lineHeight: 20,
    flex: 1,
  },
  bulletPoint: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: '#6E4B3A',
    marginTop: 7,
  }
});
