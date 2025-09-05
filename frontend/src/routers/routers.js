import { createRouter, createWebHistory } from "vue-router"
import Login from "../views/Login.vue"
import Dashboard from "../views/Dashboard.vue"

const routes = [
  {
    path: "/",
    name: "Login",
    component: Login,
  },
  {
    path: "/dashboard",
    name: "Dashboard",
    component: Dashboard,
    props: route => ({ userInfo: route.state?.userInfo })
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router