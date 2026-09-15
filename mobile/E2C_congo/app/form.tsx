import { View, TextInput, Button, Image, ImageBackground } from "react-native";
import { useAuth } from "./auth_context";
import { useRouter } from "expo-router";
import { useState } from "react";
import { LinearGradient } from "expo-linear-gradient";
import { StyleSheet, Text, TouchableOpacity } from "react-native";
export default function Login() {
  const { login } = useAuth();
  const router = useRouter();
  
  const [nom, setNom] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = () => {
    console.log("Login with:", nom, password);

    // ✅ changer l’état
    login();

    // ✅ naviguer
    router.replace("/(tabs)");
  };

  return (
    <ImageBackground

      source={require("../assets/images/bg.jpg")}
      style={styles.ImageBackground}
    >
      <View style={styles.card}>
        <Text style={styles.title}>Bienvenue</Text>
        <Text style={styles.subtitle}></Text>

        <TextInput
          placeholder="Nom "
          placeholderTextColor="#9ca3af"
          style={styles.input}
          value={nom}
          onChangeText={setNom}
          keyboardType="default"
          
        />
        <TextInput
          placeholder="Mot de passe"
          placeholderTextColor="#9ca3af"
          secureTextEntry
          style={styles.input}
          value={password}
          onChangeText={setPassword}
          
        />

        <TouchableOpacity 
          style={[styles.button, !nom && !password && styles.buttonDisabled]} 
          onPress={handleLogin}
          
        >
          <Text style={styles.buttonText}>
            Se connecter
          </Text>
        </TouchableOpacity>

        <Text style={styles.footerText}>Vous n'avez pas de compte ? Inscrivez-vous</Text>
      </View>
    </ImageBackground>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  ImageBackground: {
    flex: 1,
    resizeMode: "cover",
    width: "100%",
    height: "100%",
    justifyContent: "center",
    alignItems: "center",
    left: 0,
    right: 0,
    top: 0,
    bottom: 0,
    
    
  },
  card: {
    width: "85%",
    backgroundColor: "#fff",
    borderRadius: 24,
    padding: 24,
    shadowColor: "#000",
    shadowOpacity: 0.15,
    shadowRadius: 10,
    elevation: 8,
  },
  title: {
    fontSize: 28,
    fontWeight: "700",
    textAlign: "center",
    marginBottom: 6,
  },
  subtitle: {
    fontSize: 14,
    color: "#6b7280",
    textAlign: "center",
    marginBottom: 20,
  },
  input: {
    borderWidth: 1,
    borderColor: "#e5e7eb",
    borderRadius: 14,
    padding: 14,
    marginBottom: 14,
    fontSize: 16,
  },
  button: {
    backgroundColor: "#4f46e5",
    paddingVertical: 14,
    borderRadius: 16,
    alignItems: "center",
    marginTop: 6,
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  buttonText: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "600",
  },
  footerText: {
    textAlign: "center",
    marginTop: 16,
    fontSize: 13,
    color: "#6b7280",
  },
});

