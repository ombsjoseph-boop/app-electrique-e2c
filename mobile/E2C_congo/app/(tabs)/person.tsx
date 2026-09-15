import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  Dimensions,
  TouchableOpacity,
  Linking,
  Image,
  ImageBackground,
} from "react-native";

const { width } = Dimensions.get("window");

const agents = [
  {
    id: 1,
    name: "Jean Mavoungou",
    role: "Chef d’équipe",
    phone: "+242061234567",
    status: "En ligne",
    avatar: "https://i.pravatar.cc/150?img=3",
  },
  {
    id: 2,
    name: "Patrick Okemba",
    role: "Technicien réseau",
    phone: "+242051234567",
    status: "En intervention",
    avatar: "https://i.pravatar.cc/150?img=5",
  },
  {
    id: 3,
    name: "Arnaud Nzambe",
    role: "Agent maintenance",
    phone: "+242041234567",
    status: "Hors ligne",
    avatar: "https://i.pravatar.cc/150?img=7",
  },
  {
    id: 4,
    name: "joseph ",
    role: "Agent support",
    phone: "+242057064520",
    status: "En ligne",
    avatar: "https://i.pravatar.cc/150?img=8",
  },
];

export default function Person() {
  const callAudio = (phone: string) => {
    Linking.openURL(`tel:${phone}`);
  };

  const callVideo = (phone: string) => {
    Linking.openURL(`https://wa.me/${phone.replace("+", "")}`);
  };

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>

      {/* HEADER */}
      <View >
        <ImageBackground
          source={{ uri: "https://i.pravatar.cc/400?img=1" }}
          style={styles.header}
          resizeMode="cover"
        >
         
          <View >
            <Text style={styles.headerTitle}>👷 Agents Électricité</Text>
            <Text style={styles.headerSubtitle}>
              Communication & coordination terrain
            </Text>
          </View>
        </ImageBackground>
      </View>

      {/* GRID STATS */}
      <View style={styles.grid}>
        <View style={styles.gridCard}>
          <Text style={styles.gridValue}>12</Text>
          <Text style={styles.gridLabel}>Agents</Text>
        </View>
        <View style={styles.gridCard}>
          <Text style={styles.gridValue}>7</Text>
          <Text style={styles.gridLabel}>En ligne</Text>
        </View>
        <View style={styles.gridCard}>
          <Text style={styles.gridValue}>3</Text>
          <Text style={styles.gridLabel}>Interventions</Text>
        </View>
        <View style={styles.gridCard}>
          <Text style={styles.gridValue}>2</Text>
          <Text style={styles.gridLabel}>Urgences</Text>
        </View>
      </View>

      {/* CAROUSEL AGENTS */}
      <Text style={styles.sectionTitle}>🟢 Agents disponibles</Text>

      <ScrollView horizontal showsHorizontalScrollIndicator={false}>
        {agents.map((agent) => (
          <View key={agent.id} style={styles.carouselCard}>
            <Image source={{ uri: agent.avatar }} style={styles.avatar} />
            <Text style={styles.agentName}>{agent.name}</Text>
            <Text style={styles.agentRole}>{agent.role}</Text>
            <Text
              style={[
                styles.status,
                agent.status === "En ligne"
                  ? styles.online
                  : agent.status === "En intervention"
                  ? styles.busy
                  : styles.offline,
              ]}
            >
              {agent.status}
            </Text>
          </View>
        ))}
      </ScrollView>

      {/* LISTE AGENTS */}
      <Text style={styles.sectionTitle}>📋 Tous les agents</Text>

      {agents.map((agent) => (
        <View key={agent.id} style={styles.card}>
          <View style={styles.agentRow}>
            <Image source={{ uri: agent.avatar }} style={styles.avatarSmall} />
            <View style={{ flex: 1 }}>
              <Text style={styles.agentName}>{agent.name}</Text>
              <Text style={styles.agentRole}>{agent.role}</Text>
              <Text style={styles.statusSmall}>{agent.status}</Text>
            </View>

            <View style={styles.actions}>
              <TouchableOpacity
                style={styles.callButton}
                onPress={() => callAudio(agent.phone)}
              >
                <Text style={styles.callText}>📞</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={[styles.callButton, styles.videoButton]}
                onPress={() => callVideo(agent.phone)}
              >
                <Text style={styles.callText}>🎥</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      ))}

      <View style={{ height: 40 }} />
    </ScrollView>
  );
}
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#F3F4F6",
    paddingHorizontal: 16,
    paddingTop: 24,
  },

  header: {
    backgroundColor: "#1E40AF",
    borderRadius: 18,
    padding: 22,
    marginBottom: 20,
    elevation: 4,
  },

  headerTitle: {
    color: "#FFFFFF",
    fontSize: 24,
    fontWeight: "bold",
  },

  headerSubtitle: {
    color: "#DBEAFE",
    marginTop: 6,
    fontSize: 14,
  },

  sectionTitle: {
    fontSize: 18,
    fontWeight: "600",
    marginVertical: 12,
  },

  /* GRID */
  grid: {
    flexDirection: "row",
    flexWrap: "wrap",
    justifyContent: "space-between",
    marginBottom: 10,
  },

  gridCard: {
    width: "48%",
    backgroundColor: "#FFFFFF",
    borderRadius: 16,
    padding: 18,
    marginBottom: 12,
    elevation: 2,
    alignItems: "center",
  },

  gridValue: {
    fontSize: 22,
    fontWeight: "bold",
  },

  gridLabel: {
    color: "#6B7280",
    marginTop: 4,
  },

  /* CAROUSEL */
  carouselCard: {
    width: width * 0.6,
    backgroundColor: "#FFFFFF",
    borderRadius: 16,
    padding: 18,
    marginRight: 12,
    alignItems: "center",
    elevation: 3,
  },

  avatar: {
    width: 70,
    height: 70,
    borderRadius: 35,
    marginBottom: 8,
  },

  avatarSmall: {
    width: 48,
    height: 48,
    borderRadius: 24,
    marginRight: 12,
  },

  agentName: {
    fontSize: 16,
    fontWeight: "600",
  },

  agentRole: {
    fontSize: 13,
    color: "#6B7280",
  },

  status: {
    marginTop: 6,
    fontWeight: "600",
  },

  statusSmall: {
    fontSize: 12,
    marginTop: 2,
  },

  online: { color: "#16A34A" },
  busy: { color: "#D97706" },
  offline: { color: "#6B7280" },

  /* CARD */
  card: {
    backgroundColor: "#FFFFFF",
    borderRadius: 16,
    padding: 14,
    marginBottom: 12,
    elevation: 2,
  },

  agentRow: {
    flexDirection: "row",
    alignItems: "center",
  },

  actions: {
    flexDirection: "row",
    gap: 8,
  },

  callButton: {
    backgroundColor: "#2563EB",
    borderRadius: 10,
    padding: 10,
    marginLeft: 6,
  },

  videoButton: {
    backgroundColor: "#059669",
  },

  callText: {
    color: "#FFFFFF",
    fontSize: 16,
  },
});
