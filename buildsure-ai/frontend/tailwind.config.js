/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        site: {
          900: '#0E1116',   // deepest ground
          800: '#141920',   // page
          700: '#1A2028',   // panel
          600: '#232A34',   // raised
          500: '#313A46',   // border
        },
        hivis: '#F5C518',   // the one loud colour, taken from site hi-vis
        hazard: '#E5484D',
        caution: '#F08C2E',
        clear: '#3FB950',
        steel: '#7C8899',
        concrete: '#D5DBE3',
      },
      fontFamily: {
        display: ['"Barlow Condensed"', 'Arial Narrow', 'sans-serif'],
        sans: ['Barlow', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        panel: '0 1px 0 rgba(255,255,255,0.03) inset',
      },
    },
  },
  plugins: [],
}
