<script setup>
import { ref, onMounted } from "vue"
import { Descope } from "@descope/vue-sdk"
import { useRouter } from "vue-router"

const router = useRouter()
const loading = ref(false)

onMounted(() => {
  setTimeout(() => {
    loading.value = false
  }, 300) // 300ms delay
})

const onSuccess = async (e) => {
  console.log("✅ User authenticated:", e)

  const userInfo = {
    id: e.detail.user.userId,
    name: e.detail.user.name || "Guest User",
    email: e.detail.user.email || "No email provided",
    phone: e.detail.user.phone,
    profilePicture: e.detail.user.picture || "https://via.placeholder.com/150",
    sessionJwt: e.detail.sessionJwt,
  }

  try {

    // ✅ Save userInfo in localStorage for persistence
    localStorage.setItem("userInfo", JSON.stringify(userInfo))

    // ✅ Redirect to dashboard (no need to pass state anymore)
    router.push({ name: "Dashboard" })
  } catch (err) {
    console.error("❌ Backend error:", err)
  }
}

const onError = (err) => {
  console.error("❌ Authentication error:", err)
}
</script>

<template>
  <div class="p-6 max-w-md mx-auto">
    <h3 class="text-xl font-bold mb-4">Mental Health Scheduler</h3>

    <div v-if="loading" class="text-gray-600">Loading...</div>

    <!-- Fallback wrapper for Descope -->
    <div v-else>
      <Descope
        flow-id="sign-up-or-in"
        @success="onSuccess"
        @error="onError"
      />
    </div>
  </div>
</template>
