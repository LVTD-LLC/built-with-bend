module.exports = {
  darkMode: 'class',
  content: [
    './frontend/templates/**/*.html',
    './frontend/src/js/**/*.js',
    './apps/**/*.py',
    './built_with_bend/**/*.py',
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('@tailwindcss/forms'),
  ],
};
