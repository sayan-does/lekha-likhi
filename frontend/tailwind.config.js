/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      "colors": {
        "tertiary-fixed": "#ffdad8",
        "surface-container-high": "#f1e8cd",
        "tertiary": "#270003",
        "outline-variant": "#c5c6cc",
        "primary-fixed": "#d9e3f7",
        "on-secondary-fixed-variant": "#534529",
        "background": "#fff9ed",
        "on-background": "#1f1c0b",
        "primary": "#050e1c",
        "on-error-container": "#93000a",
        "surface-variant": "#ebe2c8",
        "primary-container": "#1a2433",
        "on-tertiary": "#ffffff",
        "inverse-surface": "#35301e",
        "on-tertiary-fixed": "#3b080b",
        "on-primary": "#ffffff",
        "tertiary-container": "#461013",
        "on-secondary-container": "#706142",
        "surface": "#fff9ed",
        "surface-dim": "#e2dabf",
        "on-surface": "#1f1c0b",
        "on-tertiary-fixed-variant": "#733333",
        "secondary-container": "#f2ddb7",
        "surface-container-low": "#fcf3d8",
        "on-surface-variant": "#44474c",
        "surface-container-lowest": "#ffffff",
        "on-primary-fixed-variant": "#3d4758",
        "tertiary-fixed-dim": "#ffb3b1",
        "on-primary-container": "#818b9e",
        "inverse-on-surface": "#faf0d5",
        "on-secondary-fixed": "#241a03",
        "error": "#ba1a1a",
        "surface-container-highest": "#ebe2c8",
        "secondary-fixed-dim": "#d8c49f",
        "primary-fixed-dim": "#bdc7db",
        "surface-bright": "#fff9ed",
        "on-primary-fixed": "#121c2b",
        "on-error": "#ffffff",
        "on-tertiary-container": "#c57473",
        "secondary-fixed": "#f5e0ba",
        "secondary": "#6b5d3e",
        "surface-tint": "#555f70",
        "inverse-primary": "#bdc7db",
        "error-container": "#ffdad6",
        "outline": "#75777d",
        "on-secondary": "#ffffff",
        "surface-container": "#f7eed2"
      },
      "borderRadius": {
        "DEFAULT": "0.25rem",
        "lg": "0.5rem",
        "xl": "0.75rem",
        "full": "9999px"
      },
      "spacing": {
        "gutter": "16px",
        "page-margin": "24px",
        "line-height-unit": "32px",
        "edge-irregularity": "8px"
      },
      "fontFamily": {
        "label-sm": ["Literata", "serif"],
        "headline-md": ["Literata", "serif"],
        "body-lg": ["Literata", "serif"],
        "body-md": ["Literata", "serif"],
        "display-lg": ["Literata", "serif"],
        "handwriting": ["Caveat", "cursive"]
      },
      "fontSize": {
        "label-sm": ["13px", {"lineHeight": "16px", "letterSpacing": "0.05em", "fontWeight": "600"}],
        "headline-md": ["24px", {"lineHeight": "32px", "fontWeight": "500"}],
        "headline-md-mobile": ["20px", {"lineHeight": "28px", "fontWeight": "500"}],
        "body-lg": ["18px", {"lineHeight": "32px", "fontWeight": "400"}],
        "body-md": ["16px", {"lineHeight": "32px", "fontWeight": "400"}],
        "display-lg": ["32px", {"lineHeight": "40px", "letterSpacing": "-0.02em", "fontWeight": "600"}]
      }
    }
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/container-queries'),
  ],
}
