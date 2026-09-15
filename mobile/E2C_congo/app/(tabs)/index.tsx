import React from "react";
import { LinearGradient } from "expo-linear-gradient";
import {
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
  FlatList,
  ScrollView,
  Dimensions,
  ImageBackground,
} from "react-native";

const { width: screenWidth } = Dimensions.get("window");

interface GridItem {
  id: string;
  title: string;
  icon: string;
}

interface CarouselItem {
  id: string;
  title: string;
  description: string;
}

export default function Home() {
  // Grille fonctionnelle pour un agent
  const gridData: GridItem[] = [
    { id: "1", title: "Zones Réseau", icon: "🗺️" },
    { id: "2", title: "Factures", icon: "💳" },
    { id: "3", title: "Alertes", icon: "🚨" },
    { id: "4", title: "Contacts", icon: "📞" },
  ];

  // Carousel pour interventions / alertes
  const carouselData: CarouselItem[] = [
    { id: "1", title: "Maintenance en cours", description: "Quartier Nord - Ligne T14" },
    { id: "2", title: "Coupure planifiée", description: "Secteur Est - 08h à 12h" },
    { id: "3", title: "Incident résolu", description: "Centre-ville - Transformateur T2" },
  ];

  const renderGridItem = ({ item }: { item: GridItem }) => (
    <TouchableOpacity style={styles.gridItem}>
      <Text style={styles.gridIcon}>{item.icon}</Text>
      <Text style={styles.gridText}>{item.title}</Text>
    </TouchableOpacity>
  );

  const renderCarouselSlide = ({ item }: { item: CarouselItem }) => (
    <View style={styles.carouselSlide}>
      <ImageBackground
        source={require("./../../assets/images/bg.jpg")}
        style={StyleSheet.absoluteFill}
        resizeMode="cover"
      />
      <LinearGradient
        colors={["rgba(0,0,0,0.6)", "rgba(0,0,0,0.3)", "rgba(0,0,0,0)"]}
        style={styles.carouselGradient}
      >
        <Text style={styles.carouselTitle}>{item.title}</Text>
        <Text style={styles.carouselDescription}>{item.description}</Text>
      </LinearGradient>
    </View>
  );

  return (
    <ScrollView style={styles.scrollContainer} showsVerticalScrollIndicator={false}>
      {/* HEADER */}
      <ImageBackground
        source={require("./../../assets/images/bg.jpg")}
        style={styles.header}
        resizeMode="cover"
      >
        <View style={styles.headerOverlay}>
          <Text style={styles.title}>E2C Congo - Agent</Text>
          <Text style={styles.subtitle}>Gestion du réseau et suivi terrain</Text>
        </View>
      </ImageBackground>

      {/* Carousel interventions */}
      <View style={styles.carouselContainer}>
        <Text style={styles.sectionTitle}>📌 Interventions / Alertes</Text>
        <FlatList
          data={carouselData}
          renderItem={renderCarouselSlide}
          keyExtractor={(item) => item.id}
          horizontal
          pagingEnabled
          showsHorizontalScrollIndicator={false}
          scrollEventThrottle={16}
          snapToInterval={screenWidth - 40}
          decelerationRate="fast"
        />
      </View>

      {/* Grille fonctions */}
      <View style={styles.gridContainer}>
        <Text style={styles.sectionTitle}>⚡ Accès rapide</Text>
        <FlatList
          data={gridData}
          renderItem={renderGridItem}
          keyExtractor={(item) => item.id}
          numColumns={2}
          columnWrapperStyle={styles.columnWrapper}
          scrollEnabled={false}
        />
      </View>

      {/* Bloc info / consignes */}
      <View style={styles.textBlock}>
        <Text style={styles.blockTitle}>Consignes de sécurité</Text>
        <Text style={styles.blockText}>
          • Toujours porter les EPI{"\n"}
          • Vérifier absence de tension avant intervention{"\n"}
          • Travailler en binôme sur le terrain
        </Text>
      </View>

      <View style={styles.textBlock}>
        <Text style={styles.blockTitle}>Contacts utiles</Text>
        <Text style={styles.blockText}>
          Chef d’équipe : +242 06 xxx xxxx{"\n"}
          Dispatching : +242 05 xxx xxxx{"\n"}
          Urgences : 111
        </Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  scrollContainer: { flex: 1, backgroundColor: "#f9fafb" },

  header: { height: 180, justifyContent: "center", alignItems: "center" },
  headerOverlay: { flex: 1, justifyContent: "center", alignItems: "center" },
  title: { fontSize: 28, fontWeight: "bold", color: "#fff", marginBottom: 6 },
  subtitle: { fontSize: 16, color: "#DBEAFE" },

  sectionTitle: { fontSize: 20, fontWeight: "700", color: "#1f2937", marginLeft: 15, marginBottom: 10 },

  carouselContainer: { marginVertical: 20 },
  carouselSlide: { width: screenWidth - 40, marginHorizontal: 10, borderRadius: 15, overflow: "hidden", height: 150 },
  carouselGradient: { flex: 1, justifyContent: "center", alignItems: "center", padding: 20 },
  carouselTitle: { fontSize: 20, fontWeight: "700", color: "#fff", marginBottom: 6, textAlign: "center" },
  carouselDescription: { fontSize: 14, color: "#e0e7ff", textAlign: "center" },

  gridContainer: { marginVertical: 20 },
  columnWrapper: { justifyContent: "space-between", paddingHorizontal: 15, marginBottom: 15 },
  gridItem: { width: "48%", backgroundColor: "#fff", borderRadius: 12, padding: 20, alignItems: "center", justifyContent: "center", minHeight: 140, elevation: 3 },
  gridIcon: { fontSize: 40, marginBottom: 10 },
  gridText: { fontSize: 14, fontWeight: "600", color: "#1f2937", textAlign: "center" },

  textBlock: { backgroundColor: "#fff", marginHorizontal: 15, marginVertical: 10, padding: 20, borderRadius: 12, elevation: 3 },
  blockTitle: { fontSize: 18, fontWeight: "700", marginBottom: 8, color: "#1f2937" },
  blockText: { fontSize: 14, color: "#6b7280", lineHeight: 20 },
});
