import { createApp } from 'vue'
import App from './App.vue'
import router from './routers/routers'
import './style.css'

import descope from '@descope/vue-sdk'
import '@descope/web-component' 

const app = createApp(App)

app.use(router)
app.use(descope, {
  projectId: import.meta.env.VITE_DESCOPE_PROJECT_ID, // must exist in .env
})

app.mount('#app')
