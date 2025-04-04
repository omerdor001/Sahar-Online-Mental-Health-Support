/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      width: {
        '116': '29rem',
        '80vw': '80vw',
      },
      maxHeight: {
        '88': '22rem', 
        '100vh': '100vh', 
      },
      fontSize: {
        'vw': '2vw', 
      },
    },
  },
  plugins: [],
};
