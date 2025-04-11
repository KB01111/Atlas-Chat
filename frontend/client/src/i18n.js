import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

i18n.use(initReactI18next).init({
  resources: {
    en: {
      translation: {
        welcome: 'Welcome to Atlas Chat frontend scaffold.',
        title: 'Atlas Chat',
      },
    },
    sv: {
      translation: {
        welcome: 'Välkommen till Atlas Chat frontend scaffold.',
        title: 'Atlas Chat',
      },
    },
  },
  lng: 'en',
  fallbackLng: 'en',
  interpolation: {
    escapeValue: false,
  },
});

export default i18n;
