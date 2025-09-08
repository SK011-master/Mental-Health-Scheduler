<script setup>
import { ref, onMounted } from "vue"
import { Descope, useSession } from "@descope/vue-sdk"
import { useRouter } from "vue-router"

const router = useRouter()

const { isLoading } = useSession();

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
    
    // Call backend
    // const res = await fetch("http://localhost:8000/api/schedule-breaks", {
    //   method: "POST",
    //   headers: { "Content-Type": "application/json" },
    //   body: JSON.stringify({
    //     user_id: userInfo.id,
    //     session_jwt: userInfo.sessionJwt,
    //   }),
    // })

    // const data = await res.json()
    // console.log("📅 Backend response:", data)

    //  Save userInfo in localStorage for persistence
    localStorage.setItem("userInfo", JSON.stringify(userInfo))

    // Redirect to dashboard (no need to pass state anymore)
    router.push({ name: "Dashboard" })
  } catch (err) {
    console.error("Backend error:", err)
  }
}

const onError = (err) => {
  console.error("Authentication error:", err)
}

const errorTransformer = (error) => {
  const translationMap = {
    SAMLStartFailed: "Failed to start SAML flow",
  };
  return translationMap[error.type] || error.text;
};
</script>

<template>
  <div class="p-6 max-w-md mx-auto">
    <h3 class="text-xl font-bold mb-4">Mental Health Scheduler</h3>

    <!-- Loading state -->
    <p v-if="isLoading">Loading...</p>

    <!-- Descope authentication widget -->
    <Descope
      v-else
      flow-id="sign-up-or-in"
      @error="onError"
      @success="onSuccess"
      :error-transformer="errorTransformer"
    />
  </div>
</template>
