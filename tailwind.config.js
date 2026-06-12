/* Config estratta dall'inline <script id="tailwind-config"> delle pagine (identica su tutte e 15).
   Per ricompilare il CSS: npm install && npm run build:css */
const cfg = {
        darkMode: "class",
        theme: {
          extend: {
            "colors": {
                    "secondary-fixed": "#c7ebd4",
                    "on-secondary-fixed-variant": "#2d4d3c",
                    "surface-container-low": "#fff2d9",
                    "on-tertiary-fixed": "#321200",
                    "secondary-fixed-dim": "#abcfb9",
                    "on-primary": "#ffffff",
                    "on-surface": "#211b0c",
                    "inverse-primary": "#efbc9b",
                    "tertiary": "#4b1f00",
                    "on-secondary": "#ffffff",
                    "tertiary-fixed": "#ffdbc8",
                    "on-background": "#211b0c",
                    "tertiary-fixed-dim": "#ffb68b",
                    "secondary-container": "#c4e8d1",
                    "surface-container": "#f9edd3",
                    "tertiary-container": "#6d3000",
                    "primary-fixed-dim": "#efbc9b",
                    "inverse-on-surface": "#fcf0d6",
                    "outline-variant": "#d4c3b9",
                    "on-tertiary-container": "#f89555",
                    "surface": "#fff8f1",
                    "on-tertiary-fixed-variant": "#753400",
                    "error-container": "#ffdad6",
                    "surface-tint": "#7c563b",
                    "primary": "#42240d",
                    "surface-bright": "#fff8f1",
                    "on-secondary-fixed": "#002113",
                    "surface-variant": "#ede1c8",
                    "primary-container": "#5c3a21",
                    "on-primary-fixed": "#2f1502",
                    "secondary": "#456553",
                    "on-error-container": "#93000a",
                    "on-primary-fixed-variant": "#623f25",
                    "on-primary-container": "#d4a484",
                    "on-secondary-container": "#496a57",
                    "outline": "#82746c",
                    "on-surface-variant": "#50443d",
                    "primary-fixed": "#ffdcc6",
                    "inverse-surface": "#36301f",
                    "surface-container-highest": "#ede1c8",
                    "background": "#fff8f1",
                    "surface-container-high": "#f3e7ce",
                    "on-error": "#ffffff",
                    "surface-dim": "#e5d9c0",
                    "surface-container-lowest": "#ffffff",
                    "error": "#ba1a1a",
                    "on-tertiary": "#ffffff"
            },
            "borderRadius": {
                    "DEFAULT": "0.125rem",
                    "lg": "0.25rem",
                    "xl": "0.5rem",
                    "full": "0.75rem"
            },
            "fontFamily": {
                    "headline": ["Noto Serif"],
                    "body": ["Work Sans"],
                    "label": ["Work Sans"]
            }
          },
        },
      };

module.exports = {
  content: ['./*.html', './en/*.html', './de/*.html', './assets/goal.js'],
  darkMode: 'class',
  theme: cfg.theme,
  plugins: [require('@tailwindcss/forms'), require('@tailwindcss/container-queries')],
};
