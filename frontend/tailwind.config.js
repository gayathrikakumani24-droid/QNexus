/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        qnx: {
          cream: '#F7F4EA',
          'cream-paper': '#FCFAF5',
          'cream-card': '#FFFFFF',
          olive: '#40513B',
          'olive-dark': '#2C3928',
          'olive-light': '#51664C',
          sage: '#8FA58A',
          'sage-soft': '#E5EBDD',
          'sage-light': '#F2F6ED',
          terracotta: '#C96F52',
          'terracotta-soft': '#F2D6CB',
          'terracotta-light': '#FAECE6',
          mustard: '#D9A52E',
          'mustard-soft': '#F5E5B8',
          'mustard-light': '#FCF6E5',
          blue: '#7198C8',
          'blue-soft': '#DCE7F4',
          'blue-light': '#EEF4FB',
          text: '#202820',
          muted: '#667066',
          border: '#E5E0D0',
          'border-light': '#EFECE1',
        }
      },
      fontFamily: {
        serif: ['"DM Serif Display"', '"Playfair Display"', 'Georgia', 'serif'],
        sans: ['"DM Sans"', '"Inter"', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'paper-sm': '0 1px 3px rgba(32, 40, 32, 0.05)',
        'paper': '0 4px 12px rgba(32, 40, 32, 0.06)',
        'paper-md': '0 8px 24px rgba(32, 40, 32, 0.08)',
        'paper-lg': '0 16px 36px rgba(32, 40, 32, 0.1)',
        'paper-lift': '0 12px 28px -4px rgba(64, 81, 59, 0.12)',
      },
      borderRadius: {
        'card': '14px',
        'badge': '8px',
      }
    },
  },
  plugins: [],
}
