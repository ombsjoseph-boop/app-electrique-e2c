import React, { useState } from "react";
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  FlatList,
  TextInput,
  TouchableOpacity,
  Image,
  Alert,
} from "react-native";
import * as ImagePicker from "expo-image-picker";

// Exemple de données
const elementsData = [
  { id: "1", name: "Transformateur T1", status: "Fonctionnel" },
  { id: "2", name: "Ligne BT-14", status: "Maintenance" },
  { id: "3", name: "Quartier Nord", status: "Hors-service" },
];

export default function Explore() {
  const [message, setMessage] = useState("");
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [reports, setReports] = useState<
    { id: string; message: string; image?: string }[]
  >([]);

  // Envoyer un message / rapport
  const sendReport = () => {
    if (!message && !selectedImage) {
      Alert.alert("Erreur", "Veuillez ajouter un message ou une photo.");
      return;
    }
    const newReport = {
      id: Date.now().toString(),
      message,
      image: selectedImage || undefined,
    };
    setReports([newReport, ...reports]);
    setMessage("");
    setSelectedImage(null);
  };

  // Prendre une photo
  const takePhoto = async () => {
    const permissionResult =
      await ImagePicker.requestCameraPermissionsAsync();
    if (!permissionResult.granted) {
      Alert.alert("Permission refusée", "Accès à la caméra nécessaire.");
      return;
    }

    const result = await ImagePicker.launchCameraAsync({
      quality: 0.5,
      allowsEditing: true,
    });

    if (!result.canceled) {
      setSelectedImage(result.assets[0].uri);
    }
  };

  return (
    <ScrollView style={styles.container}>
      {/* Liste des éléments */}
      <Text style={styles.sectionTitle}>🔌 Éléments du réseau</Text>
      <FlatList
        data={elementsData}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>{item.name}</Text>
            <Text
              style={[
                styles.cardStatus,
                item.status === "Hors-service"
                  ? { color: "#DC2626" }
                  : item.status === "Maintenance"
                  ? { color: "#FBBF24" }
                  : { color: "#16A34A" },
              ]}
            >
              {item.status}
            </Text>
          </View>
        )}
        scrollEnabled={false}
      />

      {/* Envoyer un message / rapport */}
      <Text style={styles.sectionTitle}>✉️ Envoyer un rapport</Text>
      <View style={styles.inputContainer}>
        <TextInput
          placeholder="Votre message"
          value={message}
          onChangeText={setMessage}
          style={styles.input}
          multiline
        />
        {selectedImage && (
          <Image source={{ uri: selectedImage }} style={styles.previewImage} />
        )}
        <View style={styles.buttonRow}>
          <TouchableOpacity style={styles.button} onPress={takePhoto}>
            <Text style={styles.buttonText}>📸 Prendre photo</Text>
          </TouchableOpacity>
          <TouchableOpacity style={[styles.button, styles.sendButton]} onPress={sendReport}>
            <Text style={[styles.buttonText, { color: "#fff" }]}>📤 Envoyer</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Liste des rapports envoyés */}
      <Text style={styles.sectionTitle}>📝 Rapports envoyés</Text>
      {reports.map((report) => (
        <View key={report.id} style={styles.reportCard}>
          {report.image && <Image source={{ uri: report.image }} style={styles.reportImage} />}
          <Text style={styles.reportText}>{report.message}</Text>
        </View>
      ))}

      <View style={{ height: 40 }} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#F3F4F6", paddingHorizontal: 16, paddingTop: 16 },

  sectionTitle: { fontSize: 20, fontWeight: "700", marginVertical: 12 },

  card: { backgroundColor: "#fff", borderRadius: 16, padding: 16, marginBottom: 12, elevation: 3 },
  cardTitle: { fontSize: 16, fontWeight: "600" },
  cardStatus: { fontSize: 14, marginTop: 4 },

  inputContainer: { backgroundColor: "#fff", borderRadius: 16, padding: 16, marginBottom: 20, elevation: 3 },
  input: { minHeight: 80, fontSize: 14, padding: 10, backgroundColor: "#F9FAFB", borderRadius: 10 },
  buttonRow: { flexDirection: "row", justifyContent: "space-between", marginTop: 12 },
  button: { paddingVertical: 10, paddingHorizontal: 16, borderRadius: 12, backgroundColor: "#E5E7EB" },
  sendButton: { backgroundColor: "#2563EB" },
  buttonText: { fontWeight: "600", fontSize: 14 },

  previewImage: { width: "100%", height: 150, borderRadius: 12, marginTop: 10 },

  reportCard: { backgroundColor: "#fff", borderRadius: 16, padding: 16, marginBottom: 12, elevation: 2 },
  reportImage: { width: "100%", height: 150, borderRadius: 12, marginBottom: 8 },
  reportText: { fontSize: 14, color: "#374151" },
});
