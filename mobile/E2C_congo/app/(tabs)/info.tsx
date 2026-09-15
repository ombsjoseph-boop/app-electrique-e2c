import React, { useRef, useEffect, useState } from "react";
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  Dimensions,
  Image,
} from "react-native";

import MapView, { Marker, Circle } from "react-native-maps";

const { width } = Dimensions.get("window");

// Données carousel
const carouselImages = [
  "https://images.unsplash.com/photo-1600585154340-be6161a56a0c",
  "https://images.unsplash.com/photo-1600585154340-be6161a56a0c",
  "https://images.unsplash.com/photo-1600585154340-be6161a56a0c",
];

// Grids factures et impayés
const unpaidInfo = [
  { name: "Jean Mavoungou", amount: 120 },
  { name: "Patrick Okemba", amount: 75 },
  { name: "Arnaud Nzambe", amount: 150 },
];

const billInfo = [
  { title: "Factures traitées", value: 120 },
  { title: "Factures en retard", value: 12 },
  { title: "Clients réguliers", value: 85 },
  { title: "Clients en impayé", value: 5 },
];

// Données zones
const zones = [
  {
    id: 1,
    name: "Centre-ville",
    status: "Fonctionnel",
    latitude: -4.261,
    longitude: 15.242,
  },
  {
    id: 2,
    name: "Quartier Nord",
    status: "Maintenance",
    latitude: -4.258,
    longitude: 15.245,
  },
  {
    id: 3,
    name: "Secteur Est",
    status: "Hors-service",
    latitude: -4.264,
    longitude: 15.248,
  },
];

export default function Info() {
  const carouselRef = useRef<ScrollView>(null);
  const [activeIndex, setActiveIndex] = useState(0);
  let index = 0;

  // AUTO SCROLL CAROUSEL
  useEffect(() => {
    const interval = setInterval(() => {
      index = (index + 1) % carouselImages.length;
      setActiveIndex(index);
      carouselRef.current?.scrollTo({
        x: index * (width * 0.85 + 12),
        animated: true,
      });
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* HEADER */}
      <View style={styles.header}>
        <Image
          source={{
            uri: "https://images.unsplash.com/photo-1556761175-4b46a572b786",
          }}
          style={styles.headerImage}
        />
        <View style={styles.headerOverlay}>
          <Text style={styles.headerTitle}>⚡ Infos Agent Électricité</Text>
          <Text style={styles.headerSubtitle}>
            Suivi factures, impayés et zones
          </Text>
        </View>
      </View>

      {/* CAROUSEL */}
      <Text style={styles.sectionTitle}>🏙️ Interventions terrain</Text>
      <ScrollView
        ref={carouselRef}
        horizontal
        showsHorizontalScrollIndicator={false}
      >
        {carouselImages.map((img, i) => (
          <Image
            key={i}
            source={{ uri: img }}
            style={styles.carouselImage}
          />
        ))}
      </ScrollView>

      <View style={styles.pagination}>
        {carouselImages.map((_, i) => (
          <View
            key={i}
            style={[styles.dot, i === activeIndex ? styles.activeDot : null]}
          />
        ))}
      </View>

      {/* GRID FACTURES */}
      <Text style={styles.sectionTitle}>💳 Statistiques factures</Text>
      <View style={styles.grid}>
        {billInfo.map((item, i) => (
          <View key={i} style={styles.gridCard}>
            <Text style={styles.gridValue}>{item.value}</Text>
            <Text style={styles.gridLabel}>{item.title}</Text>
          </View>
        ))}
      </View>

      {/* GRID IMPAYÉS */}
      <Text style={styles.sectionTitle}>❌ Clients en impayé</Text>
      <View style={styles.grid}>
        {unpaidInfo.map((client, i) => (
          <View key={i} style={styles.gridCard}>
            <Text style={styles.gridValue}>{client.amount} FCFA</Text>
            <Text style={styles.gridLabel}>{client.name}</Text>
          </View>
        ))}
      </View>

      {/* MAP */}
      <Text style={styles.sectionTitle}>🗺️ Zones réseau</Text>
      <MapView
        style={styles.map}
        initialRegion={{
          latitude: -4.261,
          longitude: 15.242,
          latitudeDelta: 0.01,
          longitudeDelta: 0.01,
        }}
      >
        {zones.map((zone) => (
          <Marker
            key={zone.id}
            coordinate={{ latitude: zone.latitude, longitude: zone.longitude }}
            title={zone.name}
            description={zone.status}
            pinColor={
              zone.status === "Maintenance"
                ? "#FBBF24"
                : zone.status === "Hors-service"
                ? "#DC2626"
                : "#16A34A"
            }
          />
        ))}

        {/* Cercle autour des zones (optionnel) */}
        {zones.map((zone) => (
          <Circle
            key={`circle-${zone.id}`}
            center={{ latitude: zone.latitude, longitude: zone.longitude }}
            radius={50}
            strokeColor={
              zone.status === "Maintenance"
                ? "orange"
                : zone.status === "Hors-service"
                ? "red"
                : "green"
            }
            fillColor={
              zone.status === "Maintenance"
                ? "rgba(251,191,24,0.3)"
                : zone.status === "Hors-service"
                ? "rgba(220,38,38,0.3)"
                : "rgba(22,163,52,0.3)"
            }
          />
        ))}
      </MapView>

      {/* INFOS SUPPLÉMENTAIRES */}
      <View style={[styles.card, styles.lastCard]}>
        <Text style={styles.cardTitle}>🦺 Consignes sécurité</Text>
        <Text style={styles.cardText}>
          • Porter EPI{"\n"}• Vérifier absence de tension{"\n"}• Travailler en binôme
        </Text>
      </View>

      <View style={[styles.card, styles.lastCard]}>
        <Text style={styles.cardTitle}>📞 Contacts</Text>
        <Text style={styles.cardText}>
          Chef d’équipe : +242 06 xxx xxxx{"\n"}
          Dispatching : +242 05 xxx xxxx{"\n"}
          Urgences : 111
        </Text>
      </View>

      <View style={{ height: 40 }} />
    </ScrollView>
  );
}
const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#F3F4F6", paddingHorizontal: 16, paddingTop: 16 },

  header: { height: 180, borderRadius: 16, overflow: "hidden", marginBottom: 16, position: "relative" },
  headerImage: { width: "100%", height: "100%" },
  headerOverlay: {
    position: "absolute", top: 0, left: 0, right: 0, bottom: 0,
    backgroundColor: "rgba(37, 99, 235, 0.5)",
    justifyContent: "center", alignItems: "center", padding: 16,
  },
  headerTitle: { color: "#fff", fontSize: 22, fontWeight: "bold", textAlign: "center" },
  headerSubtitle: { color: "#DBEAFE", fontSize: 14, marginTop: 4, textAlign: "center" },

  sectionTitle: { fontSize: 18, fontWeight: "600", marginVertical: 12 },

  carouselImage: { width: width * 0.85, height: 150, borderRadius: 16, marginRight: 12 },

  pagination: { flexDirection: "row", justifyContent: "center", marginVertical: 6 },
  dot: { width: 8, height: 8, borderRadius: 4, backgroundColor: "#D1D5DB", marginHorizontal: 4 },
  activeDot: { backgroundColor: "#2563EB" },

  grid: { flexDirection: "row", flexWrap: "wrap", justifyContent: "space-between", marginBottom: 16 },
  gridCard: { width: "48%", backgroundColor: "#FFFFFF", borderRadius: 16, padding: 18, marginBottom: 12, elevation: 3, alignItems: "center" },
  gridValue: { fontSize: 20, fontWeight: "bold", color: "#1E40AF" },
  gridLabel: { fontSize: 14, color: "#6B7280", marginTop: 4, textAlign: "center" },

  map: { width: "100%", height: 250, borderRadius: 16, marginBottom: 16 },

  card: { backgroundColor: "#FFFFFF", borderRadius: 16, padding: 20, marginBottom: 16, elevation: 3 },
  lastCard: { marginBottom: 20 },
  cardTitle: { fontSize: 18, fontWeight: "600", marginBottom: 8 },
  cardText: { fontSize: 14, color: "#374151", lineHeight: 20 },
});
