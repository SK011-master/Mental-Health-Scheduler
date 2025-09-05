<!-- The code below includes your Project ID (P32C7iJw4jI8URAAOMxtazQxScvQ) -->
<!-- login.vue -->
<template>
	<Descope
		:flowId="sign-up-or-in"
		@error="handleError"
		@success="handleSuccess"
	/>
</template>
<script setup>
	const handleError = (e) => {
		console.log("Error!", e);
	};

	const handleSuccess = (e) => {
		console.log(e.detail.user.name);
		console.log(e.detail.user.email);
	};

	import { createApp } from 'vue';

	const app = createApp(App);
	app.use(descope, {
		projectId: 'P32C7iJw4jI8URAAOMxtazQxScvQ',
		baseUrl: '',
		sessionTokenViaCookie: true
	});
</script>