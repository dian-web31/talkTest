/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
  './templates/**/*.html',
    './static/**/*.js',
  ],
  theme: {
    extend: {
      maxHeight: {
        'custom': '290px', // Define una clase personalizada para max-height
      },
    },
  },
  plugins: [],
}

