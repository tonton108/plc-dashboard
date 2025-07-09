// https://nuxt.com/docs/api/configuration/nuxt-config
import { createVuetify } from 'vuetify'

export default defineNuxtConfig({
  compatibilityDate: '2025-05-15',
  devtools: { enabled: true },
  css: ['vuetify/styles'],
  build: {
    transpile: ['vuetify'],
  }
})
