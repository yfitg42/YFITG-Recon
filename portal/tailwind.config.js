/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'yfitg-primary': '#011c40',
        'yfitg-secondary': '#1e3877',
        'yfitg-accent': '#2675a6',
      },
    },
  },
  plugins: [],
}

