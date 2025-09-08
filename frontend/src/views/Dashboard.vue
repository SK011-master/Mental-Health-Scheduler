<template>
  <div class="min-h-screen bg-gray-50" v-if="user">
    <!-- Header Section -->
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <!-- Logo/Brand -->
          <div class="flex items-center">
            <h1 class="text-xl font-bold text-gray-900">Mental Health Scheduler</h1>
          </div>
          
          <!-- User Profile Section -->
          <div class="flex items-center space-x-4">
            <div class="flex items-center space-x-3">
              <img 
                :src="user?.profilePicture" 
                :alt="user?.name"
                class="h-8 w-8 rounded-full object-cover"
              >
              <div class="hidden sm:block">
                <div class="text-sm font-medium text-gray-900">{{ user?.name }}</div>
                <div class="text-sm text-gray-500">{{ user?.email }}</div>
              </div>
            </div>
            <button 
              @click="handleLogout"
              class="btn-secondary text-sm"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <!-- Main Content -->
    <main class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
      <!-- Welcome Section -->
      <div class="mb-8">
        <h2 class="text-2xl font-bold text-gray-900">
          Welcome back, {{ user?.name?.split(' ')[0] || 'Guest' }}! 👋
        </h2>
        <p class="mt-2 text-gray-600">
          Take care of your mental well-being by scheduling regular wellness breaks.
        </p>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Left Section -->
        <div class="lg:col-span-2 flex flex-col gap-6">
          <!-- Wellness Break Scheduler -->
          <div class="card">
            <div class="flex items-center mb-6">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center">
                  <span class="text-primary-600 text-lg">🧘</span>
                </div>
              </div>
              <div class="ml-3">
                <h3 class="text-lg font-medium text-gray-900">Schedule Wellness Break</h3>
                <p class="text-sm text-gray-500">Take a moment to recharge and reset</p>
              </div>
            </div>

            <form @submit.prevent="scheduleBreak" class="space-y-6">
              <div>
                <label for="breakTitle" class="form-label">Break Title</label>
                <input
                  id="breakTitle"
                  v-model="breakForm.title"
                  type="text"
                  class="form-input"
                  placeholder="Enter break title"
                />
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
                <div>
                  <label for="startTime" class="form-label">Start Time</label>
                  <input
                    id="startTime"
                    v-model="breakForm.startTime"
                    type="datetime-local"
                    class="form-input"
                    required
                  />
                </div>

                <div>
                  <label for="duration" class="form-label">Duration (minutes)</label>
                  <select
                    id="duration"
                    v-model="breakForm.duration"
                    class="form-input"
                  >
                    <option value="5">5 minutes</option>
                    <option value="10">10 minutes</option>
                    <option value="15">15 minutes</option>
                    <option value="20">20 minutes</option>
                    <option value="30">30 minutes</option>
                    <option value="60">1 hour</option>
                  </select>
                </div>
              </div>

              <button
                type="submit"
                :disabled="isScheduling"
                class="btn-primary w-full sm:w-auto"
              >
                <span v-if="isScheduling" class="flex items-center">
                  <svg
                    class="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      class="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      stroke-width="4"
                    ></circle>
                    <path
                      class="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    ></path>
                  </svg>
                  Scheduling...
                </span>
                <span v-else>Schedule Break</span>
              </button>
            </form>
          </div>

          <!-- Wellness Activities List (Added Below) -->
          <div class="card">
            <h3 class="text-lg font-medium text-gray-900 mb-6">Wellness Activities Scheduled Automatically</h3>

            <!-- Horizontal Scroll for Wellness Cards -->
            <div class="flex space-x-4 overflow-x-auto pb-2 scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100 hover:scrollbar-thumb-gray-400 transition-all duration-300">
              <div
                v-for="wellness in wellness"
                :key="wellness.id"
                class="min-w-[250px] p-4 border border-gray-200 rounded-lg hover:border-primary-300 transition-colors"
              >
                <div class="flex flex-col justify-between h-full">
                  <div>
                    <h4 class="text-sm font-medium text-gray-900">{{ wellness.title }}</h4>
                    <p class="text-sm text-gray-500 mt-1">{{ formatDateTime(wellness.startTime) }}</p>
                    <p class="text-xs text-gray-400 mt-1">{{ wellness.duration }} min</p>
                  </div>
                  <a
                    :href="wellness.calendarLink"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="bg-blue-600 text-white px-3 py-1 rounded-lg shadow hover:bg-blue-700 transition-colors text-sm font-medium mt-3 text-center"
                  >
                    View
                  </a>
                </div>
              </div>

              <!-- Fallback when no activities are available -->
              <div v-if="wellness && wellness.length === 0" class="text-center w-full py-4">
                <div class="text-gray-400 text-4xl mb-3">🧘</div>
                <p class="text-gray-500 text-sm">No wellness activities added yet</p>
                <p class="text-gray-400 text-xs mt-1">Schedule your first activity above</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Section (Upcoming Events List) -->
        <div class="lg:col-span-1">
          <div class="card">
            <h3 class="text-lg font-medium text-gray-900 mb-6">Upcoming Events & Breaks</h3>

            <!-- Vertical Scroll for Events -->
            <div class="space-y-4 max-h-80 overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100 hover:scrollbar-thumb-gray-400 transition-all duration-300">
              <div
                v-for="breakItem in upcomingEvents"
                :key="breakItem.id"
                class="p-4 border border-gray-200 rounded-lg hover:border-primary-300 transition-colors"
              >
                <div class="flex items-start justify-between">
                  <div class="flex-1">
                    <h4 class="text-sm font-medium text-gray-900">{{ breakItem.title }}</h4>
                    <p class="text-sm text-gray-500 mt-1">{{ formatDateTime(breakItem.startTime) }}</p>
                    <p class="text-xs text-gray-400 mt-1">{{ breakItem.duration }} min</p>
                  </div>
                  <a
                    :href="breakItem.calendarLink"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="text-primary-600 hover:text-primary-800 text-sm font-medium"
                  >
                    View →
                  </a>
                </div>
              </div>

              <div v-if="upcomingEvents && upcomingEvents.length === 0" class="text-center py-8">
                <div class="text-gray-400 text-4xl mb-3">🗓️</div>
                <p class="text-gray-500 text-sm">No upcoming events scheduled</p>
                <p class="text-gray-400 text-xs mt-1">Schedule your first wellness break above</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Toast Notification -->
    <div
      v-if="toast.show"
      class="fixed bottom-4 right-4 z-50 max-w-sm w-full"
    >
      <div
        :class="[
          'p-4 rounded-lg shadow-lg border',
          toast.type === 'success' 
            ? 'bg-success-50 border-success-200 text-success-800' 
            : 'bg-error-50 border-error-200 text-error-800'
        ]"
      >
        <div class="flex items-center">
          <span class="text-lg mr-2">
            {{ toast.type === 'success' ? '✅' : '❌' }}
          </span>
          <p class="font-medium">{{ toast.message }}</p>
        </div>
      </div>
    </div>
    
    <!-- Loading state -->
    <!-- <div v-else class="flex justify-center items-center h-screen">
      <p class="text-gray-500">Loading user info...</p>
    </div> -->
  </div>

  

</template>

<script setup>
import { ref, reactive, onMounted, watch, onUnmounted } from "vue";
import { useRouter } from "vue-router";


const API_URL = import.meta.env.VITE_API_URL;

const router = useRouter();

// Props (received from parent component)
const props = defineProps({
  userInfo: {
    type: Object,
    required: false,
  },
});

const user = ref(props.userInfo || null);

// Reactive states
const isScheduling = ref(false);

const breakForm = reactive({
  title: "Wellness Break 🧘",
  startTime: "",
  duration: 15,
});

const toast = reactive({
  show: false,
  type: "success", // success | error
  message: "",
});

const all_events = ref([]);
const upcomingEvents = ref([]);
const wellness = ref([]); // ✅ Stores only wellness-related events

/**
 * Convert Google Calendar API events into UpcomingBreak[] format
 */
function convertGoogleEventsToUpcomingBreaks() {
  if (!Array.isArray(all_events.value)) return; // Safety check

  //  Convert all Google events into upcomingEvents
  upcomingEvents.value = all_events.value
    .filter(event => event?.start?.dateTime) // Only valid events
    .map(event => {
      const start = new Date(event.start.dateTime);
      const end = new Date(event.end.dateTime);
      const duration = Math.round((end - start) / (1000 * 60));

      return {
        id: event.id || crypto.randomUUID(),
        title: event.summary || "Wellness Break 🧘",
        startTime: start.toISOString(),
        duration,
        calendarLink: event.htmlLink || "#",
      };
    })
    .filter(event => new Date(event.startTime) >= new Date()) // Only future events
    .sort((a, b) => new Date(a.startTime) - new Date(b.startTime));

  // ✅ Filter wellness events separately
  wellness.value = upcomingEvents.value.filter(event =>
    event.title.toLowerCase().includes("wellness break")
  );
}

/**
 * Fetch Google Calendar events
 */
async function getCalendarEvents(id, sessionJwt) {
  try {
    const res = await fetch(`${API_URL}/api/calendar/events`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: id,
        session_jwt: sessionJwt,
      }),
    });

    const data = await res.json();
    all_events.value = data.events || [];

    convertGoogleEventsToUpcomingBreaks();

    console.log("📅 All Google Events:", all_events.value);
  } catch (err) {
    console.error("Error fetching events:", err);
  }
}

/**
 * Auto-schedule breaks based on free time
 */
async function autoscheduleCalendarEvents() {
  try {
    const res = await fetch(`${API_URL}/auto-schedule/events`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: user.value.id,
        events: all_events.value,
        session_jwt: user.value.sessionJwt
      }),
    });

    const data = await res.json();
    console.log("📅 Free Time:", data);
  } catch (err) {
    console.error("Error fetching events:", err);
  }
}

/**
 * Schedule a manual wellness break
 */
const scheduleBreak = async () => {
  if (!breakForm.startTime) {
    showToast("error", "Please select a start time");
    return;
  }

  if (!user.value) {
    showToast("error", "User not found");
    return;
  }

  isScheduling.value = true;

  try {
    const response = await fetch(`${API_URL}/schedule-breaks`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: props.userInfo.id,
        session_jwt: props.userInfo.sessionJwt,
        title: breakForm.title,
        start_time: breakForm.startTime,
        duration: breakForm.duration,
      }),
    });

    if (response.ok) {
      showToast("success", "Wellness break scheduled successfully!");

      // Reset form
      breakForm.title = "Wellness Break 🧘";
      breakForm.startTime = "";
      breakForm.duration = 15;

      // Refresh upcoming breaks
      getCalendarEvents(user.value.id, user.value.sessionJwt);
    } else {
      const error = await response.text();
      showToast("error", `Failed to schedule break: ${error}`);
    }
  } catch (error) {
    console.error("Error scheduling break:", error);
    showToast("error", "Network error. Please check your connection.");
  } finally {
    isScheduling.value = false;
  }
};

/**
 * Show toast notification
 */
const showToast = (type, message) => {
  toast.show = true;
  toast.type = type;
  toast.message = message;

  setTimeout(() => {
    toast.show = false;
  }, 4000);
};

/**
 * Handle user logout
 */
const handleLogout = () => {
  localStorage.removeItem("userInfo");
  user.value = null;
  router.push("/");
  showToast("success", "Logged out successfully");
};

/**
 * Format datetime for display
 */
const formatDateTime = (dateTime) => {
  const date = new Date(dateTime);
  return date.toLocaleString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  });
};


// this is the watch to update Upcoming events as backend adds them to calender

watch(
  all_events,
  () => {
    convertGoogleEventsToUpcomingBreaks();
  },
  { deep: true, immediate: true }
);

/**
 * On page load → set default start time + fetch events + auto-schedule
 */
onMounted(() => {
  const now = new Date();
  now.setHours(now.getHours() + 1);
  now.setMinutes(0);
  breakForm.startTime = now.toISOString().slice(0, 16);

  if (!user.value) {
    const saved = localStorage.getItem("userInfo");
    if (saved) {
      user.value = JSON.parse(saved);
    }
  }

  // Fetch Google Calendar events + Auto-schedule free slots
  getCalendarEvents(user.value.id, user.value.sessionJwt).then(() => {
    autoscheduleCalendarEvents();
  });

  // 🔄 Poll every 60 seconds (or whatever interval you want)
  const interval = setInterval(() => {
    if (user.value) {
      getCalendarEvents(user.value.id, user.value.sessionJwt);
    }
  }, 60000);

  // Cleanup interval on unmount
  onUnmounted(() => clearInterval(interval));
});
</script>
