<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { auth } from '$lib/stores/auth.svelte';
  import { authService } from '$lib/services/auth';
  import { employeeProfileUpdateSchema, nonEmployeeProfileUpdateSchema, changePasswordSchema } from '$lib/schemas';
  import type { User } from '$lib/types';
  import { z } from 'zod';

  // Profile state
  let user = $state<User | null>(null);
  let loading = $state(true);
  let error = $state('');

  // Edit mode
  let isEditing = $state(false);
  let editForm = $state({
    full_name: '',
    phone_number: '',
    nfc_uid: ''
  });
  let editErrors = $state<Record<string, string>>({});
  let saving = $state(false);
  let saveSuccess = $state('');

  // Password change
  let showPasswordForm = $state(false);
  let passwordForm = $state({
    old_password: '',
    new_password: '',
    new_password_confirm: ''
  });
  let passwordErrors = $state<Record<string, string>>({});
  let changingPassword = $state(false);
  let passwordSuccess = $state('');

  onMount(async () => {
    if (!auth.isAuthenticated) {
      await goto('/auth/login');
      return;
    }

    try {
      user = await authService.getProfile();
      editForm = {
        full_name: user.full_name,
        phone_number: user.phone_number || '',
        nfc_uid: user.nfc_uid || ''
      };
    } catch (e: any) {
      error = e.message || 'Failed to load profile';
    } finally {
      loading = false;
    }
  });

  function startEditing() {
    if (user) {
      editForm = {
        full_name: user.full_name,
        phone_number: user.phone_number || '',
        nfc_uid: user.nfc_uid || ''
      };
      editErrors = {};
      isEditing = true;
    }
  }

  function cancelEditing() {
    isEditing = false;
    editErrors = {};
  }

  async function saveProfile() {
    editErrors = {};
    saveSuccess = '';

    try {
      // Use role-based schema validation
      const schema = user?.role === 'employee'
        ? employeeProfileUpdateSchema
        : nonEmployeeProfileUpdateSchema;

      const validatedData = schema.parse(editForm);
      saving = true;

      const updatedUser = await auth.updateProfile(validatedData);
      user = updatedUser;

      saveSuccess = 'Profile updated successfully';
      isEditing = false;

      setTimeout(() => {
        saveSuccess = '';
      }, 3000);
    } catch (e: any) {
      if (e instanceof z.ZodError) {
        e.issues.forEach((issue) => {
          if (issue.path[0]) {
            editErrors[issue.path[0] as string] = issue.message;
          }
        });
      } else {
        error = e.message || 'Failed to update profile';
      }
    } finally {
      saving = false;
    }
  }

  async function handleChangePassword() {
    passwordErrors = {};
    passwordSuccess = '';

    try {
      const validatedData = changePasswordSchema.parse(passwordForm);
      changingPassword = true;

      const response = await authService.changePassword(validatedData);
      passwordSuccess = response.message;

      // Reset form
      passwordForm = {
        old_password: '',
        new_password: '',
        new_password_confirm: ''
      };

      setTimeout(() => {
        showPasswordForm = false;
        passwordSuccess = '';
      }, 3000);
    } catch (e: any) {
      if (e instanceof z.ZodError) {
        e.issues.forEach((issue) => {
          if (issue.path[0]) {
            passwordErrors[issue.path[0] as string] = issue.message;
          }
        });
      } else {
        passwordErrors.old_password = e.message || 'Failed to change password';
      }
    } finally {
      changingPassword = false;
    }
  }

  function formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }

  function getRoleBadgeColor(role: string): string {
    switch (role) {
      case 'admin':
        return 'bg-purple-100 text-purple-700 border-purple-200';
      case 'driver':
        return 'bg-blue-100 text-blue-700 border-blue-200';
      case 'employee':
        return 'bg-green-100 text-green-700 border-green-200';
      default:
        return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  }
</script>

<div class="min-h-screen bg-gray-50 relative overflow-hidden">
  <!-- Background Elements -->
  <div class="hero-dots fixed inset-0 opacity-30 pointer-events-none"></div>
  <div class="fixed top-0 left-0 w-full h-96 bg-gradient-to-b from-brand-50/80 to-transparent pointer-events-none"></div>

  <div class="relative z-10 p-4 md:p-8 max-w-3xl mx-auto">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-black text-gray-900 tracking-tight">My Profile</h1>
      <p class="text-gray-500 mt-1">Manage your account information</p>
    </div>

    {#if loading}
      <div class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-500"></div>
      </div>
    {:else if error}
      <div class="glass-card p-6 bg-red-50 border-red-200">
        <div class="flex items-center gap-3 text-red-600">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span class="font-medium">{error}</span>
        </div>
      </div>
    {:else if user}
      <!-- Success Message -->
      {#if saveSuccess}
        <div class="mb-6 p-4 rounded-xl bg-green-50 border border-green-200 flex items-center gap-3 animate-fade-in">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          <span class="text-green-700 font-medium">{saveSuccess}</span>
        </div>
      {/if}

      <!-- Profile Card -->
      <div class="glass-card p-6 mb-6">
        <!-- Profile Header -->
        <div class="flex items-start justify-between mb-6">
          <div class="flex items-center gap-4">
            <div class="w-16 h-16 rounded-full bg-brand-100 flex items-center justify-center text-brand-700 font-bold text-2xl border-2 border-white shadow-lg">
              {user.full_name.charAt(0).toUpperCase()}
            </div>
            <div>
              <h2 class="text-xl font-bold text-gray-900">{user.full_name}</h2>
              <p class="text-gray-500">{user.email}</p>
              <span class="inline-block mt-1 px-2 py-0.5 rounded-full text-xs font-bold uppercase border {getRoleBadgeColor(user.role)}">
                {user.role}
              </span>
            </div>
          </div>

          {#if !isEditing}
            <button
              type="button"
              onclick={startEditing}
              class="px-4 py-2 rounded-lg bg-gray-100 text-gray-700 font-medium hover:bg-gray-200 transition-colors flex items-center gap-2"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
              </svg>
              Edit
            </button>
          {/if}
        </div>

        <!-- Profile Details -->
        {#if isEditing}
          <form onsubmit={(e) => { e.preventDefault(); saveProfile(); }} class="space-y-4">
            <div>
              <label for="full_name" class="block text-sm font-bold text-gray-700 mb-1">Full Name</label>
              <input
                type="text"
                id="full_name"
                bind:value={editForm.full_name}
                class="w-full px-4 py-2 rounded-lg border {editErrors.full_name ? 'border-red-300 bg-red-50' : 'border-gray-200'} focus:ring-2 focus:ring-brand-500 focus:border-transparent transition-all"
              />
              {#if editErrors.full_name}
                <p class="text-red-500 text-sm mt-1">{editErrors.full_name}</p>
              {/if}
            </div>

            <div>
              <label for="phone_number" class="block text-sm font-bold text-gray-700 mb-1">Phone Number</label>
              <input
                type="tel"
                id="phone_number"
                bind:value={editForm.phone_number}
                class="w-full px-4 py-2 rounded-lg border {editErrors.phone_number ? 'border-red-300 bg-red-50' : 'border-gray-200'} focus:ring-2 focus:ring-brand-500 focus:border-transparent transition-all"
              />
              {#if editErrors.phone_number}
                <p class="text-red-500 text-sm mt-1">{editErrors.phone_number}</p>
              {/if}
            </div>

            {#if user.role === 'employee'}
              <div>
                <label for="nfc_uid" class="block text-sm font-bold text-gray-700 mb-1">NFC Card UID</label>
                <input
                  type="text"
                  id="nfc_uid"
                  bind:value={editForm.nfc_uid}
                  placeholder="Scan your NFC card or enter UID"
                  class="w-full px-4 py-2 rounded-lg border {editErrors.nfc_uid ? 'border-red-300 bg-red-50' : 'border-gray-200'} focus:ring-2 focus:ring-brand-500 focus:border-transparent transition-all font-mono"
                />
                {#if editErrors.nfc_uid}
                  <p class="text-red-500 text-sm mt-1">{editErrors.nfc_uid}</p>
                {/if}
                <p class="text-xs text-gray-500 mt-1">You can register your NFC card for bus check-ins</p>
              </div>
            {/if}

            <div class="flex gap-3 pt-4">
              <button
                type="submit"
                disabled={saving}
                class="px-4 py-2 rounded-lg bg-brand-500 text-white font-medium hover:bg-brand-600 transition-colors disabled:opacity-50"
              >
                {saving ? 'Saving...' : 'Save Changes'}
              </button>
              <button
                type="button"
                onclick={cancelEditing}
                class="px-4 py-2 rounded-lg bg-gray-100 text-gray-700 font-medium hover:bg-gray-200 transition-colors"
              >
                Cancel
              </button>
            </div>
          </form>
        {:else}
          <dl class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="p-4 rounded-lg bg-gray-50">
              <dt class="text-xs font-bold text-gray-500 uppercase tracking-wider">Email</dt>
              <dd class="mt-1 text-gray-900">{user.email}</dd>
            </div>

            <div class="p-4 rounded-lg bg-gray-50">
              <dt class="text-xs font-bold text-gray-500 uppercase tracking-wider">Phone</dt>
              <dd class="mt-1 text-gray-900">{user.phone_number || 'Not set'}</dd>
            </div>

            <div class="p-4 rounded-lg bg-gray-50">
              <dt class="text-xs font-bold text-gray-500 uppercase tracking-wider">Member Since</dt>
              <dd class="mt-1 text-gray-900">{formatDate(user.created_at)}</dd>
            </div>

            <div class="p-4 rounded-lg bg-gray-50">
              <dt class="text-xs font-bold text-gray-500 uppercase tracking-wider">Status</dt>
              <dd class="mt-1">
                <span class="inline-flex items-center gap-1.5 {user.is_active ? 'text-green-700' : 'text-red-700'}">
                  <span class="w-2 h-2 rounded-full {user.is_active ? 'bg-green-500' : 'bg-red-500'}"></span>
                  {user.is_active ? 'Active' : 'Inactive'}
                </span>
              </dd>
            </div>

            {#if user.role === 'employee'}
              <div class="p-4 rounded-lg bg-gray-50 md:col-span-2">
                <dt class="text-xs font-bold text-gray-500 uppercase tracking-wider">NFC Card UID</dt>
                <dd class="mt-1 font-mono text-gray-900">{user.nfc_uid || 'Not registered'}</dd>
                {#if !user.nfc_uid}
                  <p class="text-xs text-gray-500 mt-1">Click "Edit" to register your NFC card</p>
                {/if}
              </div>
            {:else if user.nfc_uid}
              <div class="p-4 rounded-lg bg-gray-50 md:col-span-2">
                <dt class="text-xs font-bold text-gray-500 uppercase tracking-wider">NFC Card UID</dt>
                <dd class="mt-1 font-mono text-gray-900">{user.nfc_uid}</dd>
                <p class="text-xs text-gray-500 mt-1">Contact admin to change NFC card</p>
              </div>
            {/if}
          </dl>
        {/if}
      </div>

      <!-- Security Section -->
      <div class="glass-card p-6">
        <h3 class="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
          Security
        </h3>

        {#if passwordSuccess}
          <div class="mb-4 p-4 rounded-xl bg-green-50 border border-green-200 flex items-center gap-3">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            <span class="text-green-700 font-medium">{passwordSuccess}</span>
          </div>
        {/if}

        {#if showPasswordForm}
          <form onsubmit={(e) => { e.preventDefault(); handleChangePassword(); }} class="space-y-4">
            <div>
              <label for="old_password" class="block text-sm font-bold text-gray-700 mb-1">Current Password</label>
              <input
                type="password"
                id="old_password"
                bind:value={passwordForm.old_password}
                class="w-full px-4 py-2 rounded-lg border {passwordErrors.old_password ? 'border-red-300 bg-red-50' : 'border-gray-200'} focus:ring-2 focus:ring-brand-500 focus:border-transparent transition-all"
              />
              {#if passwordErrors.old_password}
                <p class="text-red-500 text-sm mt-1">{passwordErrors.old_password}</p>
              {/if}
            </div>

            <div>
              <label for="new_password" class="block text-sm font-bold text-gray-700 mb-1">New Password</label>
              <input
                type="password"
                id="new_password"
                bind:value={passwordForm.new_password}
                class="w-full px-4 py-2 rounded-lg border {passwordErrors.new_password ? 'border-red-300 bg-red-50' : 'border-gray-200'} focus:ring-2 focus:ring-brand-500 focus:border-transparent transition-all"
              />
              {#if passwordErrors.new_password}
                <p class="text-red-500 text-sm mt-1">{passwordErrors.new_password}</p>
              {/if}
            </div>

            <div>
              <label for="new_password_confirm" class="block text-sm font-bold text-gray-700 mb-1">Confirm New Password</label>
              <input
                type="password"
                id="new_password_confirm"
                bind:value={passwordForm.new_password_confirm}
                class="w-full px-4 py-2 rounded-lg border {passwordErrors.new_password_confirm ? 'border-red-300 bg-red-50' : 'border-gray-200'} focus:ring-2 focus:ring-brand-500 focus:border-transparent transition-all"
              />
              {#if passwordErrors.new_password_confirm}
                <p class="text-red-500 text-sm mt-1">{passwordErrors.new_password_confirm}</p>
              {/if}
            </div>

            <div class="flex gap-3 pt-2">
              <button
                type="submit"
                disabled={changingPassword}
                class="px-4 py-2 rounded-lg bg-brand-500 text-white font-medium hover:bg-brand-600 transition-colors disabled:opacity-50"
              >
                {changingPassword ? 'Changing...' : 'Change Password'}
              </button>
              <button
                type="button"
                onclick={() => { showPasswordForm = false; passwordErrors = {}; }}
                class="px-4 py-2 rounded-lg bg-gray-100 text-gray-700 font-medium hover:bg-gray-200 transition-colors"
              >
                Cancel
              </button>
            </div>
          </form>
        {:else}
          <button
            type="button"
            onclick={() => showPasswordForm = true}
            class="px-4 py-2 rounded-lg bg-gray-100 text-gray-700 font-medium hover:bg-gray-200 transition-colors"
          >
            Change Password
          </button>
        {/if}
      </div>
    {/if}
  </div>
</div>

<style>
  .glass-card {
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(229, 231, 235, 0.8);
    border-radius: 1rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  }

  .hero-dots {
    background-image: radial-gradient(#d1d5db 1px, transparent 1px);
    background-size: 20px 20px;
  }

  .animate-fade-in {
    animation: fadeIn 0.3s ease-out;
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
</style>
