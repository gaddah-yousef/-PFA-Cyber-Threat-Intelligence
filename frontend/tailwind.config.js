/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#18231f',
        canvas: '#f3f6f4',
        mint: '#d8f5e8',
        emerald: '#087f5b',
        lime: '#b9f24a',
      },
      boxShadow: { soft: '0 18px 50px rgba(24, 35, 31, 0.08)' },
    },
  },
  plugins: [],
}
