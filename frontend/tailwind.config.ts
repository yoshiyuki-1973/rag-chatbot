import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}"
  ],
  theme: {
    extend: {
      colors: {
        ink: "#17211b",
        field: "#f7f4ed",
        moss: "#536b4d",
        brick: "#a8513d",
        line: "#d8d0c2"
      }
    }
  },
  plugins: []
};

export default config;

