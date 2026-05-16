export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: "#f0f9ff",
          100: "#e0f2fe",
          500: "#0ea5e9",
          600: "#0284c7",
          700: "#0369a1",
          900: "#082f49"
        },
        secondary: {
          50: "#f9fafb",
          500: "#6b7280",
          600: "#4b5563",
          700: "#374151"
        }
      },
      fontFamily: {
        sans: ["InterVar", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["Fira Code", "monospace"]
      }
    }
  },
  plugins: []
}
