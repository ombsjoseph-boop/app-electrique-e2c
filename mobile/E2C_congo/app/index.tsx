import { Redirect } from "expo-router";
import { useAuth } from "./auth_context";

export default function Index() {
  const { isLoggedIn } = useAuth();

  if (!isLoggedIn) {
    return <Redirect href="/form" />;
  }

  return <Redirect href="/(tabs)" />;
}
