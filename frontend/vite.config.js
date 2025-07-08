import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import istanbul from 'vite-plugin-istanbul';

// https://vite.dev/config/
export default defineConfig({
  plugins: [
      react(),
    tailwindcss(),
    process.env.NODE_ENV !== 'production' && istanbul({
      include: 'src/*',
      exclude: [
        'node_modules',
        'test/',
        'cypress/',
        '**/*.cy.js',
        '**/*.test.js',
        '**/*.spec.js',
        'src/main.jsx'
      ],
      extension: ['.js', '.jsx', '.ts', '.tsx'],
      requireEnv: false,
      cypress: true,
      checkProd: false
    })
  ].filter(Boolean),
  define: {
    // Nécessaire pour certaines bibliothèques
    global: 'globalThis',
  },
  server: {
    // Configuration pour les tests
    open: false,
    host: true
  },
});

