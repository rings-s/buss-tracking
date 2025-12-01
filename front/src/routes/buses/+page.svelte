<script lang="ts">
  import { onMount } from 'svelte';
  import { apiClient } from '$lib/services/api-client';
  import { t } from '$lib/i18n';

  let buses = $state<any[]>([]);
  let drivers = $state<any[]>([]);
  let loading = $state(true);
  let error = $state('');

  // Form state
  let showForm = $state(false);
  let editingId = $state<number | null>(null);
  let formData = $state({ name: '', plate_number: '', capacity: 1, driver_id: '' as string | number, active: true });

  onMount(async () => {
    await Promise.all([loadBuses(), loadDrivers()]);
  });

  async function loadBuses() {
    loading = true;
    try {
      const response = await apiClient.get<any>('/api/buses/');
      buses = response.results || response;
    } catch (e: any) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  async function loadDrivers() {
    try {
      const response = await apiClient.get<any>('/api/auth/users/?role=driver');
      drivers = response.users || [];
    } catch (e: any) {
      console.error('Failed to load drivers:', e);
    }
  }

  async function handleSubmit() {
    try {
      // Convert empty string to null for driver_id
      const submitData = {
        ...formData,
        driver_id: formData.driver_id === '' ? null : Number(formData.driver_id)
      };
      
      if (editingId) {
        await apiClient.put(`/api/buses/${editingId}/`, submitData);
      } else {
        await apiClient.post('/api/buses/', submitData);
      }
      resetForm();
      await loadBuses();
    } catch (e: any) {
      error = e.message;
    }
  }

  async function handleDelete(id: number) {
    if (confirm($t('buses.deleteConfirm'))) {
      try {
        await apiClient.delete(`/api/buses/${id}/`);
        await loadBuses();
      } catch (e: any) {
        error = e.message;
      }
    }
  }

  function editBus(bus: any) {
    editingId = bus.id;
    formData = {
      name: bus.name,
      plate_number: bus.plate_number,
      capacity: bus.capacity,
      driver_id: bus.driver?.id || '',
      active: bus.active
    };
    showForm = true;
  }

  function resetForm() {
    showForm = false;
    editingId = null;
    formData = { name: '', plate_number: '', capacity: 1, driver_id: '', active: true };
  }
</script>

<div class="max-w-6xl mx-auto px-4 py-8">
  <div class="flex justify-between items-center mb-8">
    <h1 class="text-4xl font-black text-gray-900 tracking-tight">{$t('buses.title')}</h1>
    <button class="btn-primary w-auto flex items-center gap-2" onclick={() => showForm = !showForm}>
      {#if showForm}
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
        </svg>
        {$t('buses.cancel')}
      {:else}
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
        </svg>
        {$t('buses.addBus')}
      {/if}
    </button>
  </div>

  {#if showForm}
    <div class="glass-card p-8 mb-8 animate-slide-down">
      <h2 class="text-2xl font-bold mb-6 text-gray-800">{editingId ? $t('buses.editBus') : $t('buses.addNewBus')}</h2>
      <form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }} class="space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label for="bus-name" class="block text-sm font-bold text-gray-700 mb-2">{$t('buses.busName')}</label>
            <input id="bus-name" class="input-field" bind:value={formData.name} required placeholder={$t('buses.busNamePlaceholder')} />
          </div>
          <div>
            <label for="plate-number" class="block text-sm font-bold text-gray-700 mb-2">{$t('buses.plateNumber')}</label>
            <input id="plate-number" class="input-field" bind:value={formData.plate_number} required placeholder={$t('buses.plateNumberPlaceholder')} />
          </div>
          <div>
            <label for="capacity" class="block text-sm font-bold text-gray-700 mb-2">{$t('buses.capacity')}</label>
            <input id="capacity" type="number" class="input-field" bind:value={formData.capacity} min="1" required />
          </div>
          <div>
            <label for="driver" class="block text-sm font-bold text-gray-700 mb-2">{$t('buses.assignDriver')}</label>
            <select id="driver" class="input-field" bind:value={formData.driver_id}>
              <option value="">{$t('buses.noDriver')}</option>
              {#each drivers as driver}
                <option value={driver.id}>{driver.full_name} ({driver.email})</option>
              {/each}
            </select>
            <p class="text-xs text-gray-500 mt-1">{$t('buses.assignDriverOptional')}</p>
          </div>
          <div class="flex items-center h-full pt-8">
            <label class="flex items-center cursor-pointer">
              <input type="checkbox" bind:checked={formData.active} class="form-checkbox h-5 w-5 text-brand-500 rounded border-gray-300 focus:ring-brand-500" />
              <span class="ml-3 text-gray-700 font-medium">{$t('buses.activeStatus')}</span>
            </label>
          </div>
        </div>
        <div class="flex justify-end pt-4">
          <button type="submit" class="btn-primary w-auto px-8">
            {editingId ? $t('buses.updateBus') : $t('buses.createBus')}
          </button>
        </div>
      </form>
    </div>
  {/if}

  {#if error}
    <div class="p-4 mb-6 rounded-xl bg-red-50 text-red-600 border border-red-100 flex items-center gap-3">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <span class="font-medium">{error}</span>
    </div>
  {/if}

  {#if loading}
    <div class="flex justify-center py-20">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-500"></div>
    </div>
  {:else}
    <div class="glass-card overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-gray-50/80 border-b border-gray-200/50 text-xs uppercase tracking-wider text-gray-500">
              <th class="py-4 px-6 font-bold">{$t('buses.table.id')}</th>
              <th class="py-4 px-6 font-bold">{$t('buses.table.name')}</th>
              <th class="py-4 px-6 font-bold">{$t('buses.table.plate')}</th>
              <th class="py-4 px-6 font-bold">{$t('buses.table.capacity')}</th>
              <th class="py-4 px-6 font-bold">{$t('buses.table.driver')}</th>
              <th class="py-4 px-6 font-bold">{$t('buses.table.status')}</th>
              <th class="py-4 px-6 font-bold text-right">{$t('buses.table.actions')}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100/50">
            {#each buses as bus}
              <tr class="hover:bg-brand-50/30 transition-colors duration-200">
                <td class="py-4 px-6 text-gray-500 font-mono text-sm">#{bus.id}</td>
                <td class="py-4 px-6 font-bold text-gray-900">{bus.name}</td>
                <td class="py-4 px-6 text-gray-600 font-mono bg-gray-50 rounded px-2 py-1 text-xs w-fit">{bus.plate_number}</td>
                <td class="py-4 px-6 text-gray-600">{bus.capacity} {$t('buses.table.seats')}</td>
                <td class="py-4 px-6">
                  {#if bus.driver}
                    <div class="flex items-center gap-2">
                      <div class="w-6 h-6 rounded-full bg-brand-100 text-brand-600 flex items-center justify-center text-xs font-bold">
                        {bus.driver.full_name.charAt(0)}
                      </div>
                      <span class="text-sm font-medium text-gray-700">{bus.driver.full_name}</span>
                    </div>
                  {:else}
                    <span class="text-gray-400 text-sm italic">{$t('buses.table.unassigned')}</span>
                  {/if}
                </td>
                <td class="py-4 px-6">
                  <span class={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${bus.active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                    {bus.active ? $t('buses.table.active') : $t('buses.table.inactive')}
                  </span>
                </td>
                <td class="py-4 px-6 text-right space-x-2">
                  <button onclick={() => editBus(bus)} class="text-brand-600 hover:text-brand-800 font-medium text-sm transition-colors">{$t('buses.table.edit')}</button>
                  <button onclick={() => handleDelete(bus.id)} class="text-red-500 hover:text-red-700 font-medium text-sm transition-colors">{$t('buses.table.delete')}</button>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    </div>
  {/if}
</div>
