{
  "presets": [
    "@tailwindcss/preset Typography",
    "@tailwindcss/preset-Forms"
  ],
  "content": [
    "./templates/**/*.html",
    "./src/research/templates/**/*.html",
    "./static/**/*.js"
  ],
  "theme": {
    "extend": {
      "colors": {
        "brand": {
          "500": "#3b82f6",
          "600": "#2563eb"
        },
        "surface": {
          "900": "#0f172a",
          "950": "#020617"
        }
      },
      "boxShadow": {
        "panel": "0 10px 30px rgba(2, 6, 23, 0.25)"
      }
    }
  },
  "plugins": []
}