import { createContext, useContext, useState, useEffect } from "react";
import { api } from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [loading, setLoading] = useState(false);

  const login = async (email, password) => {
    const data = await api.login(email, password);
    localStorage.setItem("token", data.access_token);
    setToken(data.access_token);
  };

  const register = async (email, password) => {
    await api.register(email, password);
    // After registering, log them in automatically
    await login(email, password);
  };

  const logout = () => {
    localStorage.removeItem("token");
    setToken(null);
  };

  const value = {
    token,
    isAuthenticated: !!token,
    login,
    register,
    logout,
    loading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}