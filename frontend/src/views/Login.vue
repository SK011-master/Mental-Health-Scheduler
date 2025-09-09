<script setup>
import { ref, onMounted } from "vue"
import { useSession } from "@descope/vue-sdk"
import { useRouter } from "vue-router"

const router = useRouter()

const { isLoading } = useSession();

const projectId = import.meta.env.VITE_DESCOPE_PROJECT_ID

const onSuccess = async (e) => {

  const userInfo = {
    id: e.detail.user.userId,
    name: e.detail.user.name || "Guest User",
    email: e.detail.user.email || "No email provided",
    phone: e.detail.user.phone,
    profilePicture: e.detail.user.picture || "https://via.placeholder.com/150",
    sessionJwt: e.detail.sessionJwt,
  }

  try {

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
    <p>Some Time it take time to show up aprox 1min please do a reaload if not showing up</p>

    <!-- Loading state -->
    <p v-if="isLoading">Loading...</p>

    <!-- Descope authentication widget -->
    <descope-wc
      v-else
      :project-id="projectId"
      flow-id="sign-up-or-in"
      @success="onSuccess"
      @error="onError"
    ></descope-wc>
  </div>
</template>
