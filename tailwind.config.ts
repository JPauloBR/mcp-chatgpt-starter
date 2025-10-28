// tailwind.config.js
export default {
  content: [
    "./src/**/*.{html,js,ts,jsx,tsx}",
    "./host/**/*.{html,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'att-blue': '#00468B',
        'att-blue-light': '#0057A3',
        'att-blue-dark': '#003566',
        'att-cyan': '#007AB8',
        'att-gray': '#5A5A5A',
      },
    },
  },
  plugins: [],
};
