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
        <!-- Wellness Break Scheduler -->
        <div class="lg:col-span-2">
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
                >
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
                  >
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
                  <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Scheduling...
                </span>
                <span v-else>Schedule Break</span>
              </button>
            </form>
          </div>
        </div>

        <!-- Upcoming Breaks List -->
        <div class="lg:col-span-1">
          <div class="card">
            <h3 class="text-lg font-medium text-gray-900 mb-6">Upcoming Breaks</h3>
            
            <div class="space-y-4">
              <div
                v-for="breakItem in upcomingBreaks"
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

              <div v-if="upcomingBreaks.length === 0" class="text-center py-8">
                <div class="text-gray-400 text-4xl mb-3">🗓️</div>
                <p class="text-gray-500 text-sm">No upcoming breaks scheduled</p>
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
    <div v-else class="flex justify-center items-center h-screen">
      <p class="text-gray-500">Loading user info...</p>
    </div>
  </div>

  

</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from "vue-router"


const router = useRouter()
// Props (will receive from parent component)
const props = defineProps({
  userInfo: {
    type: Object,
    required: false,
  },
})

const user = ref(props.userInfo || null)

// Types
interface UserInfo {
  id: string
  name: string
  email: string
  profilePicture: string
  sessionJwt: string
}

interface BreakForm {
  title: string
  startTime: string
  duration: number
}

interface UpcomingBreak {
  id: string
  title: string
  startTime: string
  duration: number
  calendarLink: string
}

interface Toast {
  show: boolean
  type: 'success' | 'error'
  message: string
}


// Reactive data
const isScheduling = ref(false)

const breakForm = reactive<BreakForm>({
  title: 'Wellness Break 🧘',
  startTime: '',
  duration: 15
})

const toast = reactive<Toast>({
  show: false,
  type: 'success',
  message: ''
})

// Dummy data for upcoming breaks
const upcomingBreaks = ref<UpcomingBreak[]>([
  {
    id: '1',
    title: 'Morning Meditation 🧘',
    startTime: '2025-01-15T09:00:00',
    duration: 15,
    calendarLink: 'https://calendar.google.com/calendar/event?eid=dummy1'
  },
  {
    id: '2',
    title: 'Lunch Break Walk 🚶‍♀️',
    startTime: '2025-01-15T12:30:00',
    duration: 30,
    calendarLink: 'https://calendar.google.com/calendar/event?eid=dummy2'
  },
  {
    id: '3',
    title: 'Afternoon Breathing Exercise 🌬️',
    startTime: '2025-01-15T15:15:00',
    duration: 10,
    calendarLink: 'https://calendar.google.com/calendar/event?eid=dummy3'
  }
])

// Methods
const scheduleBreak = async () => {
  if (!breakForm.startTime) {
    showToast('error', 'Please select a start time')
    return
  }

  if (!user.value) {
    showToast('error', 'User not found')
    return
  }

  isScheduling.value = true

  try {
    const response = await fetch('http://localhost:8000/schedule-breaks', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: props.userInfo.id,
        session_jwt: props.userInfo.sessionJwt,
        title: breakForm.title,
        start_time: breakForm.startTime,
        duration: breakForm.duration
      })
    })

    if (response.ok) {
      showToast('success', 'Wellness break scheduled successfully!')
      
      // Reset form
      breakForm.title = 'Wellness Break 🧘'
      breakForm.startTime = ''
      breakForm.duration = 15
      
      // TODO: Refresh upcoming breaks list from backend
    } else {
      const error = await response.text()
      showToast('error', `Failed to schedule break: ${error}`)
    }
  } catch (error) {
    console.error('Error scheduling break:', error)
    showToast('error', 'Network error. Please check your connection.')
  } finally {
    isScheduling.value = false
  }
}

const showToast = (type: 'success' | 'error', message: string) => {
  toast.show = true
  toast.type = type
  toast.message = message
  
  setTimeout(() => {
    toast.show = false
  }, 4000)
}

const handleLogout = () => {
  localStorage.removeItem("userInfo")
  user.value = null
  router.push("/")
  showToast('success', 'Logged out successfully')
}

const formatDateTime = (dateTime: string): string => {
  const date = new Date(dateTime)
  return date.toLocaleString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  })
}

// Set default start time to current time + 1 hour
onMounted(() => {
  const now = new Date()
  now.setHours(now.getHours() + 1)
  now.setMinutes(0)
  breakForm.startTime = now.toISOString().slice(0, 16)

  if (!user.value) {
    const saved = localStorage.getItem("userInfo")
    if (saved) {
      user.value = JSON.parse(saved)
    }
  }
})
</script>