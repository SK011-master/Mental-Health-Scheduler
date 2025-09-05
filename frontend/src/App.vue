<script setup>
import { ref } from "vue"
import { Descope } from "@descope/vue-sdk"
import Dashboard from "./components/Dashboard.vue"

// State to track authentication & user info
const isAuthenticated = ref(false)
const userInfo = ref(null)

const onSuccess = async (e) => {
  console.log("✅ User authenticated:", e)

  // Store user info from Descope
  userInfo.value = {
    id: e.detail.user.userId,
    name: e.detail.user.name || "Guest User",
    email: e.detail.user.email || "No email provided",
    phone: e.detail.user.phone,
    profilePicture: e.detail.user.picture || "https://via.placeholder.com/150",
    sessionJwt: e.detail.sessionJwt
  }

  // Send user_id + sessionJwt to Flask backend
  try {
    const res = await fetch("http://localhost:8000/schedule-breaks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: userInfo.value.id,
        session_jwt: userInfo.value.sessionJwt
      })
    })

    const data = await res.json()
    console.log("📅 Backend response:", data)
  } catch (err) {
    console.error("❌ Backend error:", err)
  }

  // After successful login, show the dashboard
  isAuthenticated.value = true
}

const onError = (err) => {
  console.error("❌ Authentication error:", err)
}
</script>

<template>
  <div>
    <!-- If authenticated, show Dashboard -->
    <Dashboard v-if="isAuthenticated" :user-info="userInfo" />

    <!-- Otherwise, show Descope login/signup flow -->
    <Descope
      v-else
      flow-id="sign-up-or-in"
      @success="onSuccess"
      @error="onError"
    />
  </div>
</template>
