/** @type {import('tailwindcss').Config} */
module.exports = {
    content: ["./{static,pages}/**/*.{html,js}"],
    theme: {
      extend: {
        keyframes:{
          shimmer:{
            '0%': { backgroundPosition: '-100%' },
            '100%': { backgroundPosition: '100%' },
          }
        },
        animation:{
          shimmer: 'shimmer 2s infinite linear',
        },
      },
    },
    plugins: [],
}