import { createApp } from 'vue'
import App from './App.vue'
import './style.css'

import descope from '@descope/vue-sdk'

const app = createApp(App)

app.use(descope, {
  projectId: import.meta.env.VITE_DESCOPE_PROJECT_ID, // replace with your actual project ID
  // optional:
  // baseUrl: 'https://auth.yourdomain.com', 
  // sessionTokenViaCookie: true
})

app.mount('#app')
