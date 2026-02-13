import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { loadSettings, saveSettings } from '../utils/storage';

const ThemeContext = createContext(null);

export function ThemeProvider({ children }) {
  const [settings, setSettings] = useState(() => loadSettings());

  useEffect(() => {
    saveSettings(settings);
  }, [settings]);

  useEffect(() => {
    const root = document.documentElement;
    root.setAttribute('data-theme', settings.darkMode ? 'dark' : 'light');
    root.setAttribute('data-contrast', settings.highContrast ? 'high' : 'normal');
  }, [settings.darkMode, settings.highContrast]);

  const toggleDarkMode = useCallback(() => {
    setSettings(prev => ({ ...prev, darkMode: !prev.darkMode }));
  }, []);

  const toggleHighContrast = useCallback(() => {
    setSettings(prev => ({ ...prev, highContrast: !prev.highContrast }));
  }, []);

  const toggleHardMode = useCallback(() => {
    setSettings(prev => ({ ...prev, hardMode: !prev.hardMode }));
  }, []);

  return (
    <ThemeContext.Provider value={{ settings, setSettings, toggleDarkMode, toggleHighContrast, toggleHardMode }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error('useTheme must be inside ThemeProvider');
  return ctx;
}
