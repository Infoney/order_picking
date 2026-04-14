<template>
  <div>
    <!-- B2B Workflow Steps Indicator -->
    <div class="flex items-center justify-center gap-2 mb-6 text-xs font-bold uppercase tracking-wider flex-wrap">
      <div :class="stepClass(1)" class="flex items-center gap-1.5 px-3 py-1.5 rounded-full transition-all">
        <span class="w-5 h-5 rounded-full flex items-center justify-center text-[10px] border" :class="stepNumClass(1)">1</span>
        Pick Items
      </div>
      <svg class="w-4 h-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
      <div :class="stepClass(2)" class="flex items-center gap-1.5 px-3 py-1.5 rounded-full transition-all">
        <span class="w-5 h-5 rounded-full flex items-center justify-center text-[10px] border" :class="stepNumClass(2)">2</span>
        Material Request
      </div>
      <svg class="w-4 h-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
      <div :class="stepClass(3)" class="flex items-center gap-1.5 px-3 py-1.5 rounded-full transition-all">
        <span class="w-5 h-5 rounded-full flex items-center justify-center text-[10px] border" :class="stepNumClass(3)">3</span>
        Stock Entry
      </div>
      <svg class="w-4 h-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
      <div :class="stepClass(4)" class="flex items-center gap-1.5 px-3 py-1.5 rounded-full transition-all">
        <span class="w-5 h-5 rounded-full flex items-center justify-center text-[10px] border" :class="stepNumClass(4)">4</span>
        Complete
      </div>
    </div>

    <!-- Progress Bar -->
    <div class="bg-white dark:bg-slate-800 p-6 rounded-xl shadow-sm border border-gray-100 dark:border-slate-700 mb-6 relative overflow-hidden">
      <div class="absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-purple-400 to-indigo-500"></div>
      <div class="flex justify-between items-end mb-3">
        <h4 class="text-sm font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider flex items-center gap-2">
          <svg class="w-4 h-4 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/></svg>
          B2B Picking Progress
        </h4>
        <div class="text-2xl font-black" :class="percentage >= 100 ? 'text-green-600' : 'text-purple-600'">{{ percentage }}%</div>
      </div>
      <div class="w-full bg-gray-100 rounded-full h-4 mb-2 overflow-hidden shadow-inner ring-1 ring-inset ring-gray-200/50">
        <div class="h-4 rounded-full transition-all duration-500 ease-out relative"
          :class="percentage >= 100 ? 'bg-gradient-to-r from-green-400 to-green-500' : 'bg-gradient-to-r from-purple-400 to-indigo-500'"
          :style="{ width: Math.min(percentage, 100) + '%' }">
          <div class="absolute inset-0 bg-white/20 w-full animate-[shimmer_2s_infinite] -skew-x-12 translate-x-[-100%]"></div>
        </div>
      </div>
      <!-- Active SO + Customer -->
      <div class="flex flex-wrap items-center gap-3 mt-4">
        <div v-if="currentSO" class="text-sm font-medium text-gray-500 bg-gray-50 dark:bg-slate-700 dark:text-slate-200 px-3 py-1.5 rounded-md border border-gray-100 dark:border-slate-600 shadow-sm">
          Active: <span class="font-bold text-gray-800 dark:text-white">{{ currentSO }}</span>
        </div>
        <div v-if="customerName" class="text-sm font-medium text-purple-700 bg-purple-50 dark:bg-purple-900/30 dark:text-purple-300 px-3 py-1.5 rounded-md border border-purple-200 dark:border-purple-800 shadow-sm flex items-center gap-1.5">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>
          {{ customerName }}
        </div>
        <div v-if="soStatus" class="text-xs font-bold px-2.5 py-1.5 rounded-md uppercase tracking-wider shadow-sm border"
          :class="soStatus === 'To Deliver and Bill' ? 'bg-blue-100 text-blue-700 border-blue-200' : soStatus === 'Completed' ? 'bg-green-100 text-green-700 border-green-200' : 'bg-gray-100 text-gray-700 border-gray-200'">
          {{ soStatus }}
        </div>
        <!-- MR Created badge -->
        <div v-if="mrName" class="text-xs font-bold px-2.5 py-1.5 rounded-md uppercase tracking-wider shadow-sm border bg-amber-100 text-amber-700 border-amber-200">
          MR: {{ mrName }}
        </div>
      </div>
    </div>

    <!-- STEP 1: Scan Inputs -->
    <div v-if="currentStep === 1" class="flex flex-col gap-4 mb-6">
      <!-- SO Scanner (always visible in step 1) -->
      <div class="flex flex-col md:flex-row gap-4">
        <div class="flex-1 relative group">
          <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
            <svg class="w-6 h-6 text-gray-400 group-focus-within:text-purple-500 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
          </div>
          <input v-model="soScan" @keyup.enter="handleSOScan" type="text" id="scan_so_input"
            class="w-full pl-12 pr-4 py-4 text-lg border-2 border-gray-200 dark:border-slate-600 rounded-xl focus:border-purple-500 focus:ring-4 focus:ring-purple-500/20 transition-all shadow-sm font-medium bg-white dark:bg-slate-800 dark:text-slate-100 placeholder-gray-400 dark:placeholder-slate-500"
            placeholder="Scan Sales Order Barcode..."
            :disabled="isLoading || warehouseConfirmed" ref="soInputRef">
        </div>
      </div>

      <!-- Warehouse Selection (after SO scanned, before picking) -->
      <div v-if="currentSO && !warehouseConfirmed" class="bg-white dark:bg-slate-800 p-6 rounded-xl shadow-sm border-2 border-purple-200 dark:border-purple-800 mb-2">
        <h4 class="text-sm font-bold text-purple-700 dark:text-purple-300 uppercase tracking-wider mb-4 flex items-center gap-2">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/></svg>
          Select Warehouses to Start Picking
        </h4>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div class="relative" ref="srcDropdownContainer">
            <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Source Warehouse *</label>
            <input type="text" v-model="sourceWarehouseQuery" @input="onSourceInput" @focus="showSourceDropdown = true" @keydown.down.prevent="navigateDropdown('source', 1)" @keydown.up.prevent="navigateDropdown('source', -1)" @keydown.enter.prevent="selectHighlighted('source')" @keydown.escape="showSourceDropdown = false"
              class="w-full border-2 border-gray-200 rounded-lg px-3 py-2.5 text-sm font-medium focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 bg-white dark:bg-slate-700 dark:border-slate-600 dark:text-slate-100"
              :class="{'border-green-400 bg-green-50 dark:bg-green-900/20': sourceWarehouse && sourceWarehouseQuery === sourceWarehouse}"
              placeholder="Type to search source warehouse...">
            <div v-if="showSourceDropdown && filteredSourceWarehouses.length > 0" class="absolute z-50 mt-1 w-full bg-white dark:bg-slate-700 border-2 border-purple-300 dark:border-purple-600 rounded-lg shadow-xl max-h-52 overflow-y-auto">
              <button v-for="(w, idx) in filteredSourceWarehouses" :key="w" type="button" @mousedown.prevent="selectWarehouse('source', w)"
                class="w-full text-left px-3 py-2 text-sm font-medium transition-colors truncate"
                :class="idx === sourceHighlight ? 'bg-purple-100 dark:bg-purple-800 text-purple-800 dark:text-purple-200' : 'hover:bg-gray-50 dark:hover:bg-slate-600 text-gray-700 dark:text-slate-200'">
                {{ w }}
              </button>
            </div>
          </div>
          <div class="relative" ref="destDropdownContainer">
            <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Destination Warehouse *</label>
            <input type="text" v-model="targetWarehouseQuery" @input="onTargetInput" @focus="showTargetDropdown = true" @keydown.down.prevent="navigateDropdown('target', 1)" @keydown.up.prevent="navigateDropdown('target', -1)" @keydown.enter.prevent="selectHighlighted('target')" @keydown.escape="showTargetDropdown = false"
              class="w-full border-2 border-gray-200 rounded-lg px-3 py-2.5 text-sm font-medium focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 bg-white dark:bg-slate-700 dark:border-slate-600 dark:text-slate-100"
              :class="{'border-green-400 bg-green-50 dark:bg-green-900/20': targetWarehouse && targetWarehouseQuery === targetWarehouse}"
              placeholder="Type to search destination warehouse...">
            <div v-if="showTargetDropdown && filteredTargetWarehouses.length > 0" class="absolute z-50 mt-1 w-full bg-white dark:bg-slate-700 border-2 border-purple-300 dark:border-purple-600 rounded-lg shadow-xl max-h-52 overflow-y-auto">
              <button v-for="(w, idx) in filteredTargetWarehouses" :key="w" type="button" @mousedown.prevent="selectWarehouse('target', w)"
                class="w-full text-left px-3 py-2 text-sm font-medium transition-colors truncate"
                :class="idx === targetHighlight ? 'bg-purple-100 dark:bg-purple-800 text-purple-800 dark:text-purple-200' : 'hover:bg-gray-50 dark:hover:bg-slate-600 text-gray-700 dark:text-slate-200'">
                {{ w }}
              </button>
            </div>
          </div>
        </div>
        <button @click="confirmWarehouses" :disabled="!sourceWarehouse || !targetWarehouse || isLoading"
          class="bg-purple-600 hover:bg-purple-700 text-white font-bold py-2.5 px-6 rounded-lg text-sm shadow-md transition-all hover:-translate-y-0.5 hover:shadow-lg flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed">
          <svg v-if="isLoading" class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/></svg>
          <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
          Confirm &amp; Start Picking
        </button>
      </div>

      <!-- Active warehouse badges + change warehouse (after confirmed) -->
      <div v-if="warehouseConfirmed" class="flex flex-wrap items-center gap-2 mb-2">
        <div class="text-xs font-bold px-3 py-1.5 rounded-md bg-blue-50 text-blue-700 border border-blue-200 flex items-center gap-1">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4"/></svg>
          From: {{ sourceWarehouse }}
        </div>
        <div class="text-xs font-bold px-3 py-1.5 rounded-md bg-green-50 text-green-700 border border-green-200 flex items-center gap-1">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"/></svg>
          To: {{ targetWarehouse }}
        </div>
        <button @click="openChangeWarehouse" class="text-xs font-bold px-3 py-1.5 rounded-md bg-purple-50 text-purple-700 border border-purple-200 hover:bg-purple-100 transition-colors flex items-center gap-1 cursor-pointer" title="Change active warehouses for next scans (F5)">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
          Change WH <span class="bg-purple-200/60 px-1 rounded text-[10px] ml-0.5">F5</span>
        </button>
      </div>

      <!-- Change Warehouse Inline Panel (mid-pick) -->
      <div v-if="showChangeWarehouse && warehouseConfirmed" class="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-xl border-2 border-purple-300 dark:border-purple-700 mb-3 transition-all">
        <div class="flex items-center justify-between mb-3">
          <h5 class="text-xs font-bold text-purple-700 dark:text-purple-300 uppercase tracking-wider flex items-center gap-1.5">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
            Switch Warehouses (next scans will use these)
          </h5>
          <button @click="showChangeWarehouse = false" class="text-purple-400 hover:text-purple-600 transition-colors">&times;</button>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
          <div class="relative" ref="chgSrcDropdownContainer">
            <label class="block text-[10px] font-bold text-purple-500 uppercase mb-0.5">New Source</label>
            <input type="text" v-model="chgSourceQuery" @input="onChgSourceInput" @focus="showChgSourceDropdown = true" @keydown.down.prevent="navigateDropdown('chgSource', 1)" @keydown.up.prevent="navigateDropdown('chgSource', -1)" @keydown.enter.prevent="selectHighlighted('chgSource')" @keydown.escape="showChgSourceDropdown = false"
              class="w-full border-2 border-purple-200 rounded-lg px-3 py-2 text-sm font-medium focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 bg-white dark:bg-slate-700 dark:border-purple-600 dark:text-slate-100"
              :class="{'border-green-400 bg-green-50 dark:bg-green-900/20': chgSourceWarehouse}"
              :placeholder="sourceWarehouse">
            <div v-if="showChgSourceDropdown && filteredChgSourceWarehouses.length > 0" class="absolute z-50 mt-1 w-full bg-white dark:bg-slate-700 border-2 border-purple-300 dark:border-purple-600 rounded-lg shadow-xl max-h-44 overflow-y-auto">
              <button v-for="(w, idx) in filteredChgSourceWarehouses" :key="w" type="button" @mousedown.prevent="selectWarehouse('chgSource', w)"
                class="w-full text-left px-3 py-2 text-sm font-medium transition-colors truncate"
                :class="idx === chgSourceHighlight ? 'bg-purple-100 dark:bg-purple-800 text-purple-800 dark:text-purple-200' : 'hover:bg-gray-50 dark:hover:bg-slate-600 text-gray-700 dark:text-slate-200'">
                {{ w }}
              </button>
            </div>
          </div>
          <div class="relative" ref="chgDestDropdownContainer">
            <label class="block text-[10px] font-bold text-purple-500 uppercase mb-0.5">New Destination</label>
            <input type="text" v-model="chgTargetQuery" @input="onChgTargetInput" @focus="showChgTargetDropdown = true" @keydown.down.prevent="navigateDropdown('chgTarget', 1)" @keydown.up.prevent="navigateDropdown('chgTarget', -1)" @keydown.enter.prevent="selectHighlighted('chgTarget')" @keydown.escape="showChgTargetDropdown = false"
              class="w-full border-2 border-purple-200 rounded-lg px-3 py-2 text-sm font-medium focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 bg-white dark:bg-slate-700 dark:border-purple-600 dark:text-slate-100"
              :class="{'border-green-400 bg-green-50 dark:bg-green-900/20': chgTargetWarehouse}"
              :placeholder="targetWarehouse">
            <div v-if="showChgTargetDropdown && filteredChgTargetWarehouses.length > 0" class="absolute z-50 mt-1 w-full bg-white dark:bg-slate-700 border-2 border-purple-300 dark:border-purple-600 rounded-lg shadow-xl max-h-44 overflow-y-auto">
              <button v-for="(w, idx) in filteredChgTargetWarehouses" :key="w" type="button" @mousedown.prevent="selectWarehouse('chgTarget', w)"
                class="w-full text-left px-3 py-2 text-sm font-medium transition-colors truncate"
                :class="idx === chgTargetHighlight ? 'bg-purple-100 dark:bg-purple-800 text-purple-800 dark:text-purple-200' : 'hover:bg-gray-50 dark:hover:bg-slate-600 text-gray-700 dark:text-slate-200'">
                {{ w }}
              </button>
            </div>
          </div>
        </div>
        <button @click="applyWarehouseChange" :disabled="(!chgSourceWarehouse && !chgTargetWarehouse)"
          class="bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-5 rounded-lg text-xs shadow-md transition-all flex items-center gap-1.5 disabled:opacity-50 disabled:cursor-not-allowed">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
          Apply &amp; Continue Picking
        </button>
      </div>

      <!-- Item Scanner (only after warehouses confirmed) -->
      <div v-if="warehouseConfirmed" class="flex flex-col gap-2">
        <div class="flex flex-row gap-2">
          <div class="flex-1 relative group">
            <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <svg class="w-6 h-6 text-gray-400 group-focus-within:text-indigo-500 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z"/></svg>
            </div>
            <input v-model="itemScan" @keyup.enter="handleItemScan" type="text" id="scan_b2b_item_input"
              :class="{'ring-4 ring-green-400/50 border-green-400': flashSuccess, 'border-red-400 ring-4 ring-red-400/30 bg-red-50 dark:bg-red-900/20': scanError, 'border-gray-200 focus:border-indigo-500 focus:ring-indigo-500/20': !flashSuccess && !scanError}"
              class="w-full pl-12 pr-4 py-4 text-lg border-2 rounded-xl focus:ring-4 transition-all shadow-sm font-medium bg-white dark:bg-slate-800 dark:text-slate-100 placeholder-gray-400 dark:placeholder-slate-500 disabled:bg-gray-100 dark:disabled:bg-slate-900 disabled:cursor-not-allowed"
              placeholder="Scan Item Barcode (supports UOM/Box)..."
              :disabled="isLoading" ref="itemInputRef">
          </div>
          <!-- Manual Qty Multiplier -->
          <div class="w-24 flex-shrink-0">
            <div class="relative">
              <label class="absolute -top-2 left-2 bg-white dark:bg-slate-800 px-1 text-[10px] font-bold text-purple-600 dark:text-purple-400 uppercase tracking-wider z-10">× Qty</label>
              <input v-model.number="manualQtyMultiplier" type="number" min="1" step="1"
                @keydown.enter.prevent="handleItemScan"
                class="w-full py-4 px-3 text-lg text-center border-2 border-purple-300 dark:border-purple-700 rounded-xl focus:border-purple-500 focus:ring-4 focus:ring-purple-500/20 transition-all shadow-sm font-black bg-purple-50 dark:bg-purple-900/30 dark:text-purple-200"
                :disabled="isLoading">
            </div>
          </div>
        </div>
        <!-- Inline Over-pick Error Banner -->
        <Transition name="fade">
          <div v-if="scanError" class="flex items-center gap-3 bg-red-600 text-white px-4 py-3 rounded-xl shadow-lg font-bold text-sm">
            <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636"/></svg>
            <span>{{ scanError }}</span>
            <button @click="scanError = ''" class="ml-auto text-white/80 hover:text-white text-lg leading-none">&times;</button>
          </div>
        </Transition>
      </div>
    </div>

    <!-- Last scanned info -->
    <Transition name="fade">
      <div v-if="lastScanInfo && currentStep === 1" class="mb-4 p-3 rounded-lg bg-indigo-50 dark:bg-indigo-900/30 border border-indigo-200 dark:border-indigo-800 text-sm font-medium text-indigo-700 dark:text-indigo-300 flex items-center gap-2">
        <svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
        {{ lastScanInfo }}
      </div>
    </Transition>

    <!-- Items Lists (Step 1) -->
    <div v-if="currentStep === 1" class="flex flex-col md:flex-row gap-6 mb-6">
      <!-- Items to Pick -->
      <div class="flex-1 bg-white dark:bg-slate-800 p-6 rounded-xl shadow-sm border border-gray-100 dark:border-slate-700 flex flex-col min-h-[350px]">
        <h4 class="text-sm font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-4 border-b pb-3 flex justify-between items-center">
          <span class="flex items-center gap-2"><div class="w-2 h-2 rounded-full bg-purple-500"></div> Items to Pick</span>
          <span class="bg-gray-100 text-gray-600 px-2 py-0.5 rounded text-xs">{{ itemsToPick.filter(i => i.qty > 0).length }} pending</span>
        </h4>
        <div class="flex-1 overflow-y-auto pr-2 -mr-2 space-y-2" v-if="itemsToPick.length > 0">
          <div v-for="item in itemsToPick.filter(i => i.qty > 0)" :key="item.item_code"
            class="flex justify-between items-center bg-gray-50 dark:bg-slate-700 border border-gray-100 dark:border-slate-600 p-3 rounded-lg hover:border-purple-200 hover:shadow-sm transition-all group gap-3">
            <div class="flex items-center gap-3 overflow-hidden">
              <div v-if="item.image" class="w-12 h-12 flex-shrink-0 bg-white rounded-md p-1 border border-gray-200 overflow-hidden flex items-center justify-center">
                <img :src="item.image" class="max-w-full max-h-full object-contain" :alt="item.item_code">
              </div>
              <div v-else class="w-12 h-12 flex-shrink-0 bg-gray-100 rounded-md border border-gray-200 flex items-center justify-center text-gray-400">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
              </div>
              <div class="flex flex-col overflow-hidden">
                <div class="font-bold text-gray-800 dark:text-slate-100 tracking-wide truncate">{{ item.item_code }}</div>
                <div class="text-xs text-gray-500 truncate" :title="item.item_name">{{ item.item_name || 'No Name' }}</div>
              </div>
            </div>
            <div class="text-lg font-black bg-white dark:bg-slate-800 px-3 py-1 rounded shadow-sm border border-gray-200 group-hover:border-purple-300 group-hover:text-purple-700 transition-colors flex-shrink-0">
              {{ item.qty }} <span class="text-xs text-gray-400 font-medium">{{ item.uom }}</span>
              <div v-if="stockLevels[item.item_code] !== undefined" class="text-[10px] font-medium mt-0.5" :class="stockLevels[item.item_code] >= item.qty ? 'text-green-500' : 'text-red-500'">
                Stock: {{ stockLevels[item.item_code] }}
              </div>
            </div>
          </div>
        </div>
        <div v-else class="flex-1 flex flex-col items-center justify-center text-gray-400 opacity-60">
          <svg class="w-16 h-16 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/></svg>
          <p class="font-medium text-lg">Scan a Sales Order to begin.</p>
        </div>
      </div>
      <!-- Picked Items -->
      <div class="flex-1 bg-white dark:bg-slate-800 p-6 rounded-xl shadow-sm border border-gray-100 dark:border-slate-700 flex flex-col min-h-[350px]">
        <h4 class="text-sm font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-4 border-b pb-3 flex justify-between items-center">
          <span class="flex items-center gap-2"><div class="w-2 h-2 rounded-full bg-green-500"></div> Picked Items</span>
          <span class="bg-green-50 text-green-700 px-2 py-0.5 rounded text-xs border border-green-100">{{ pickedItems.reduce((a, o) => a + o.qty, 0) }} total</span>
        </h4>
        <div class="flex-1 overflow-y-auto pr-2 -mr-2 space-y-2" v-if="pickedItems.length > 0">
          <div v-for="item in pickedItems" :key="item.item_code + item.source_warehouse"
            @click="askRemoveItem(item)"
            class="flex justify-between items-center bg-green-50 border border-green-100 p-3 rounded-lg shadow-sm gap-3 cursor-pointer hover:bg-red-50 hover:border-red-200 group transition-colors"
            title="Click to remove">
            <div class="flex items-center gap-3 overflow-hidden">
              <div v-if="item.image" class="w-10 h-10 flex-shrink-0 bg-white rounded-md border border-green-200 overflow-hidden p-0.5 flex items-center justify-center">
                <img :src="item.image" class="max-w-full max-h-full object-contain" :alt="item.item_code">
              </div>
              <div class="flex flex-col overflow-hidden">
                <div class="font-bold text-green-800 group-hover:text-red-700 tracking-wide flex items-center gap-1.5 truncate transition-colors">
                  <svg class="w-4 h-4 text-green-600 group-hover:hidden flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                  <svg class="w-4 h-4 text-red-500 hidden group-hover:block flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                  <span class="truncate">{{ item.item_code }}</span>
                </div>
                <div class="text-xs text-green-700/80 group-hover:text-red-500/80 truncate transition-colors" :title="item.item_name">{{ item.item_name || 'No Name' }}</div>
              </div>
            </div>
            <div class="flex flex-col items-end gap-0.5 flex-shrink-0">
              <div class="text-lg font-black bg-white text-green-700 group-hover:text-red-600 group-hover:border-red-200 px-3 py-1 rounded shadow-sm border border-green-200 transition-colors">{{ item.qty }}</div>
              <div v-if="item.source_warehouse || item.target_warehouse" class="text-[9px] text-gray-400 font-medium leading-tight text-right max-w-[140px] truncate" :title="(item.source_warehouse || '') + ' → ' + (item.target_warehouse || '')">
                {{ shortenWH(item.source_warehouse) }} → {{ shortenWH(item.target_warehouse) }}
              </div>
            </div>
          </div>
        </div>
        <div v-else class="flex-1 flex flex-col items-center justify-center text-gray-400 opacity-60">
          <svg class="w-16 h-16 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"/></svg>
          <p class="font-medium">No items picked yet.</p>
        </div>
      </div>
    </div>

    <!-- Print Button (visible whenever picked items exist, across all steps) -->
    <div v-if="pickedItems.length > 0" class="flex justify-end mb-4">
      <button @click="printPickList" class="text-sm font-semibold text-gray-600 bg-gray-100 hover:bg-gray-200 dark:bg-slate-700 dark:text-slate-200 dark:hover:bg-slate-600 px-4 py-2 rounded-lg transition-colors shadow-sm ring-1 ring-inset ring-gray-200 dark:ring-slate-600 flex items-center gap-2">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"/></svg>
        Print Pick List
      </button>
    </div>

    <!-- Action: Create Material Request (after picking - full or partial) -->
    <div v-if="currentStep === 1 && pickedItems.length > 0 && currentSO && warehouseConfirmed" class="bg-white dark:bg-slate-800 p-6 rounded-xl shadow-sm border border-gray-100 dark:border-slate-700 mb-6">
      <!-- Partial Delivery Info (B2B allows any %) -->
      <div v-if="percentage < 100" class="mb-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3 flex items-center gap-3">
        <svg class="w-5 h-5 text-blue-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
        <p class="text-sm text-blue-700 dark:text-blue-300">
          <span class="font-bold">{{ percentage }}% picked</span> — You can proceed at any quantity. Order will be marked <strong>"Consignment Partially Delivered"</strong>.
        </p>
      </div>
      <div v-if="percentage >= 100" class="mb-4 bg-green-50 border border-green-200 rounded-lg p-3 flex items-center gap-2">
        <svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
        <p class="text-sm font-bold text-green-800">
          {{ percentage > 100 ? `Over-picked at ${percentage}% — ` : 'All items fully picked! — ' }}This will be marked as "Consignment Delivered".
        </p>
      </div>
      <h4 class="text-sm font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-4 flex items-center gap-2">
        <svg class="w-4 h-4 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/></svg>
        Create Material Request
      </h4>
      <div class="grid grid-cols-1 gap-4 mb-4">
        <div>
          <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Required By Date *</label>
          <input v-model="requiredByDate" type="date" class="w-full md:w-1/3 border-2 border-gray-200 rounded-lg px-3 py-2.5 text-sm font-medium focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 bg-white dark:bg-slate-700 dark:border-slate-600 dark:text-slate-100">
        </div>
      </div>
      <button @click="createMR" :disabled="!requiredByDate || isLoading"
        :class="percentage < 100 ? 'bg-orange-600 hover:bg-orange-700' : 'bg-amber-600 hover:bg-amber-700'"
        class="text-white font-bold py-2.5 px-6 rounded-lg text-sm shadow-md transition-all hover:-translate-y-0.5 hover:shadow-lg flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:translate-y-0">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
        {{ percentage < 100 ? 'Create Material Request (Partial Delivery)' : 'Create Material Request' }}
      </button>
    </div>

    <!-- STEP 2: Submit Material Request -->
    <div v-if="currentStep === 2" class="bg-white dark:bg-slate-800 p-8 rounded-xl shadow-sm border border-gray-100 dark:border-slate-700 mb-6 text-center">
      <div class="flex items-center justify-center w-16 h-16 mx-auto bg-amber-100 text-amber-600 rounded-full mb-4">
        <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
      </div>
      <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-2">Material Request Created</h3>
      <p class="text-gray-500 dark:text-slate-400 mb-1 font-medium">
        <a :href="'/app/material-request/' + mrName" target="_blank" class="text-amber-600 font-bold hover:underline">{{ mrName }}</a>
        has been saved as Draft.
      </p>
      <p class="text-gray-400 dark:text-slate-500 mb-6 text-sm">Please review and submit to proceed with the Material Transfer.</p>
      <button @click="submitMR" :disabled="isLoading"
        class="bg-amber-600 hover:bg-amber-700 text-white font-bold py-3 px-8 rounded-lg text-sm shadow-md transition-all hover:-translate-y-0.5 hover:shadow-lg inline-flex items-center gap-2 disabled:opacity-50">
        <svg v-if="isLoading" class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/></svg>
        <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
        Submit Material Request
      </button>
    </div>

    <!-- STEP 3: Create Stock Entry -->
    <div v-if="currentStep === 3" class="bg-white dark:bg-slate-800 p-8 rounded-xl shadow-sm border border-gray-100 dark:border-slate-700 mb-6">
      <div class="flex items-center justify-center w-16 h-16 mx-auto bg-green-100 text-green-600 rounded-full mb-4">
        <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"/></svg>
      </div>
      <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-2 text-center">Create Material Transfer</h3>
      <p class="text-gray-500 dark:text-slate-400 mb-6 text-center font-medium text-sm">Material Request <span class="font-bold text-amber-600">{{ mrName }}</span> has been submitted. Now create the Stock Entry.</p>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div class="relative" ref="ccDropdownContainer">
          <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Cost Center *</label>
          <input type="text" v-model="costCenterQuery" @input="onCostCenterInput" @focus="showCCDropdown = true" @keydown.down.prevent="navigateDropdown('cc', 1)" @keydown.up.prevent="navigateDropdown('cc', -1)" @keydown.enter.prevent="selectHighlighted('cc')" @keydown.escape="showCCDropdown = false"
            class="w-full border-2 border-gray-200 rounded-lg px-3 py-2.5 text-sm font-medium focus:border-green-500 focus:ring-2 focus:ring-green-500/20 bg-white dark:bg-slate-700 dark:border-slate-600 dark:text-slate-100"
            :class="{'border-green-400 bg-green-50 dark:bg-green-900/20': costCenter && costCenterQuery === costCenter}"
            placeholder="Type to search cost center...">
          <div v-if="showCCDropdown && filteredCostCenters.length > 0" class="absolute z-50 mt-1 w-full bg-white dark:bg-slate-700 border-2 border-green-300 dark:border-green-600 rounded-lg shadow-xl max-h-52 overflow-y-auto">
            <button v-for="(cc, idx) in filteredCostCenters" :key="cc" type="button" @mousedown.prevent="selectWarehouse('cc', cc)"
              class="w-full text-left px-3 py-2 text-sm font-medium transition-colors truncate"
              :class="idx === ccHighlight ? 'bg-green-100 dark:bg-green-800 text-green-800 dark:text-green-200' : 'hover:bg-gray-50 dark:hover:bg-slate-600 text-gray-700 dark:text-slate-200'">
              {{ cc }}
            </button>
          </div>
        </div>
        <div>
          <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Purpose of Transfer</label>
          <input v-model="purposeOfTransfer" type="text" class="w-full border-2 border-gray-200 rounded-lg px-3 py-2.5 text-sm font-medium focus:border-green-500 focus:ring-2 focus:ring-green-500/20 bg-white dark:bg-slate-700 dark:border-slate-600 dark:text-slate-100"
            :placeholder="'Transfer by B2B Order Pick for ' + customerName">
        </div>
      </div>
      <div class="text-center">
        <button @click="createSE" :disabled="!costCenter || isLoading"
          class="bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-8 rounded-lg text-sm shadow-md transition-all hover:-translate-y-0.5 hover:shadow-lg inline-flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed">
          <svg v-if="isLoading" class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/></svg>
          <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"/></svg>
          Create &amp; Submit Material Transfer
        </button>
      </div>
    </div>

    <!-- STEP 4: Completed Summary -->
    <div v-if="currentStep === 4" class="bg-white dark:bg-slate-800 p-8 rounded-xl shadow-sm border border-gray-100 dark:border-slate-700 mb-6">
      <div class="flex items-center justify-center w-16 h-16 mx-auto rounded-full mb-4" :class="isPartialPick ? 'bg-orange-100 text-orange-600' : 'bg-green-100 text-green-600'">
        <svg v-if="!isPartialPick" class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
        <svg v-else class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"/></svg>
      </div>
      <h3 class="text-xl font-bold mb-1 text-center" :class="isPartialPick ? 'text-orange-700 dark:text-orange-400' : 'text-green-700 dark:text-green-400'">{{ isPartialPick ? 'Consignment Partially Delivered' : 'B2B Order Completed!' }}</h3>
      <p class="text-gray-500 dark:text-slate-400 mb-6 text-center text-sm">
        Sales Order <span class="font-bold">{{ completedSE.so_name }}</span> &mdash; {{ completedSE.customer_name }}
      </p>

      <!-- Reference Links -->
      <div class="flex flex-wrap justify-center gap-3 mb-6">
        <a :href="'/app/material-request/' + completedSE.mr_name" target="_blank" class="text-sm font-bold text-amber-700 bg-amber-50 border border-amber-200 px-4 py-2 rounded-lg hover:bg-amber-100 transition-colors flex items-center gap-2">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
          MR: {{ completedSE.mr_name }}
        </a>
        <a :href="'/app/stock-entry/' + completedSE.se_name" target="_blank" class="text-sm font-bold text-green-700 bg-green-50 border border-green-200 px-4 py-2 rounded-lg hover:bg-green-100 transition-colors flex items-center gap-2">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"/></svg>
          SE: {{ completedSE.se_name }}
        </a>
      </div>

      <!-- Items Summary Table -->
      <div class="overflow-x-auto mb-6 border border-gray-200 dark:border-slate-600 rounded-lg">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 dark:bg-slate-700">
            <tr>
              <th class="text-left px-4 py-2.5 text-xs font-bold text-gray-500 uppercase">#</th>
              <th class="text-left px-4 py-2.5 text-xs font-bold text-gray-500 uppercase">Item Code</th>
              <th class="text-left px-4 py-2.5 text-xs font-bold text-gray-500 uppercase">Item Name</th>
              <th class="text-right px-4 py-2.5 text-xs font-bold text-gray-500 uppercase">Qty</th>
              <th class="text-left px-4 py-2.5 text-xs font-bold text-gray-500 uppercase">UOM</th>
              <th class="text-left px-4 py-2.5 text-xs font-bold text-gray-500 uppercase">From</th>
              <th class="text-left px-4 py-2.5 text-xs font-bold text-gray-500 uppercase">To</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, idx) in completedSE.items" :key="idx" class="border-t border-gray-100 dark:border-slate-600">
              <td class="px-4 py-2 text-gray-400">{{ idx + 1 }}</td>
              <td class="px-4 py-2 font-bold text-gray-700 dark:text-slate-200">{{ item.item_code }}</td>
              <td class="px-4 py-2 text-gray-600 dark:text-slate-300">{{ item.item_name }}</td>
              <td class="px-4 py-2 text-right font-black text-green-700">{{ item.qty }}</td>
              <td class="px-4 py-2 text-gray-500">{{ item.uom }}</td>
              <td class="px-4 py-2 text-gray-500 text-xs">{{ item.from_warehouse }}</td>
              <td class="px-4 py-2 text-gray-500 text-xs">{{ item.to_warehouse }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Action Buttons -->
      <div class="flex flex-wrap justify-center gap-3">
        <button @click="printCompletedSummary" class="text-sm font-semibold text-gray-600 bg-gray-100 hover:bg-gray-200 dark:bg-slate-700 dark:text-slate-200 dark:hover:bg-slate-600 px-5 py-2.5 rounded-lg transition-colors shadow-sm ring-1 ring-inset ring-gray-200 dark:ring-slate-600 flex items-center gap-2">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"/></svg>
          Print Summary
        </button>
        <button @click="resetForNextOrder" class="text-sm font-bold text-white bg-purple-600 hover:bg-purple-700 px-5 py-2.5 rounded-lg transition-all shadow-md hover:-translate-y-0.5 hover:shadow-lg flex items-center gap-2">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 5l7 7-7 7"/></svg>
          Scan Next Order
        </button>
      </div>
    </div>

    <!-- Session Summary -->
    <div class="flex flex-col md:flex-row gap-6 mb-6 mt-4">
      <div class="flex-1 bg-white dark:bg-slate-800 p-6 rounded-xl shadow-sm border-2 border-dashed border-gray-200 dark:border-slate-700 flex items-center justify-between">
        <div>
          <p class="text-sm font-bold text-gray-500 uppercase tracking-wider mb-1">Completed Orders</p>
          <h3 class="text-3xl font-black text-gray-800 dark:text-white">{{ completedCount }}</h3>
        </div>
        <div class="w-12 h-12 rounded-full bg-purple-50 dark:bg-slate-700 flex items-center justify-center text-purple-500">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
        </div>
      </div>
      <div class="flex-1 bg-white dark:bg-slate-800 p-6 rounded-xl shadow-sm border-2 border-dashed border-gray-200 dark:border-slate-700 flex items-center justify-between">
        <div>
          <p class="text-sm font-bold text-gray-500 uppercase tracking-wider mb-1">Total Items Picked</p>
          <h3 class="text-3xl font-black text-gray-800 dark:text-white">{{ totalPickedCount }}</h3>
        </div>
        <div class="w-12 h-12 rounded-full bg-green-50 dark:bg-slate-700 flex items-center justify-center text-green-500">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4"/></svg>
        </div>
      </div>
    </div>

    <!-- Remove Item Confirmation Modal -->
    <Transition name="fade">
      <div v-if="removeTarget" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" @click.self="removeTarget = null">
        <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl border-2 border-red-300 dark:border-red-700 p-7 w-full max-w-sm mx-4">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-10 h-10 bg-red-100 dark:bg-red-900/40 rounded-xl flex items-center justify-center flex-shrink-0">
              <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
            </div>
            <h3 class="text-lg font-black text-gray-800 dark:text-white">Remove Picked Item?</h3>
          </div>
          <p class="text-sm text-gray-600 dark:text-slate-300 mb-1">
            <span class="font-bold text-gray-800 dark:text-white">{{ removeTarget?.item_code }}</span>
          </p>
          <p class="text-xs text-gray-400 dark:text-slate-500 mb-5">{{ removeTarget?.item_name }}</p>
          <div class="bg-gray-50 dark:bg-slate-700 rounded-lg px-4 py-2 mb-5 flex items-center justify-between text-sm">
            <span class="text-gray-500 dark:text-slate-400">Qty to return:</span>
            <span class="font-black text-red-600">−{{ removeTarget?.qty }} {{ removeTarget?.uom }}</span>
          </div>
          <div class="flex gap-3">
            <button @click="removeTarget = null" class="flex-1 py-3 bg-gray-100 dark:bg-slate-700 text-gray-700 dark:text-slate-200 rounded-xl font-bold text-sm hover:bg-gray-200 transition-colors">
              No, Keep It
            </button>
            <button @click="confirmRemoveItem" class="flex-1 py-3 bg-red-600 text-white rounded-xl font-bold text-sm hover:bg-red-700 transition-colors shadow-md">
              Yes, Remove
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Close B2B Pick Confirmation Modal -->
    <Transition name="fade">
      <div v-if="showCloseConfirm" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
        <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl border-2 border-orange-300 dark:border-orange-700 p-7 w-full max-w-sm mx-4">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-10 h-10 bg-orange-100 dark:bg-orange-900/40 rounded-xl flex items-center justify-center flex-shrink-0">
              <svg class="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/></svg>
            </div>
            <h3 class="text-lg font-black text-gray-800 dark:text-white">Close B2B Pick?</h3>
          </div>
          <p class="text-sm text-gray-600 dark:text-slate-300 mb-5">
            You have <span class="font-black text-orange-600">{{ pickedItems.length }} item(s)</span> already picked. Closing will discard all progress for this order.
          </p>
          <div class="flex gap-3">
            <button @click="showCloseConfirm = false" class="flex-1 py-3 bg-gray-100 dark:bg-slate-700 text-gray-700 dark:text-slate-200 rounded-xl font-bold text-sm hover:bg-gray-200 transition-colors">
              Keep Picking
            </button>
            <button @click="$emit('close'); showCloseConfirm = false" class="flex-1 py-3 bg-orange-600 text-white rounded-xl font-bold text-sm hover:bg-orange-700 transition-colors shadow-md">
              Yes, Close
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Qty Override Modal (F9) — Scanner-friendly, large layout -->
    <Transition name="fade">
      <div v-if="showQtyOverride" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" @click.self="closeQtyOverride">
        <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl border-2 border-purple-300 dark:border-purple-600 p-8 w-full max-w-lg mx-4">
          <!-- Header -->
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-2xl font-black text-gray-800 dark:text-white flex items-center gap-3">
              <div class="w-10 h-10 bg-purple-100 dark:bg-purple-900/50 rounded-xl flex items-center justify-center">
                <svg class="w-6 h-6 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14"/></svg>
              </div>
              Override Quantity
            </h3>
            <button @click="closeQtyOverride" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 text-2xl font-bold px-2 transition-colors">&times;</button>
          </div>

          <!-- Step 1: Barcode / SKU Scanner -->
          <div class="mb-5">
            <label class="block text-sm font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">Scan Item Barcode or Enter SKU</label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <svg class="w-7 h-7 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z"/></svg>
              </div>
              <input type="text" v-model="qtyOverrideScanInput" ref="qtyOverrideScanRef"
                @keyup.enter="resolveQtyOverrideItem"
                class="w-full pl-14 pr-4 py-5 text-xl border-2 border-gray-300 dark:border-slate-600 rounded-xl focus:border-purple-500 focus:ring-4 focus:ring-purple-500/20 transition-all shadow-sm font-bold bg-white dark:bg-slate-700 dark:text-slate-100 placeholder-gray-400 dark:placeholder-slate-500"
                placeholder="Scan barcode or type item code...">
            </div>
          </div>

          <!-- Resolved Item Info -->
          <Transition name="fade">
            <div v-if="qtyOverrideItem" class="mb-5 p-4 rounded-xl border-2 transition-all"
              :class="qtyOverrideItem ? 'border-purple-200 bg-purple-50 dark:bg-purple-900/20 dark:border-purple-700' : 'border-gray-200 bg-gray-50'">
              <div class="flex items-center gap-4 mb-3">
                <div v-if="qtyOverrideItem.image" class="w-16 h-16 flex-shrink-0 bg-white rounded-lg p-1 border border-purple-200 overflow-hidden flex items-center justify-center shadow-sm">
                  <img :src="qtyOverrideItem.image" class="max-w-full max-h-full object-contain" :alt="qtyOverrideItem.item_code">
                </div>
                <div class="flex-1 min-w-0">
                  <div class="text-lg font-black text-gray-800 dark:text-white truncate">{{ qtyOverrideItem.item_code }}</div>
                  <div class="text-sm text-gray-500 dark:text-slate-400 truncate">{{ qtyOverrideItem.item_name || 'No Name' }}</div>
                </div>
              </div>
              <div class="flex gap-4 text-sm">
                <div class="bg-white dark:bg-slate-700 px-3 py-1.5 rounded-lg border border-gray-200 dark:border-slate-600">
                  <span class="text-gray-400 font-medium">Picked: </span>
                  <span class="font-black text-purple-600 dark:text-purple-400">{{ qtyOverrideItem.qty || 0 }}</span>
                </div>
                <div class="bg-white dark:bg-slate-700 px-3 py-1.5 rounded-lg border border-gray-200 dark:border-slate-600">
                  <span class="text-gray-400 font-medium">Remaining: </span>
                  <span class="font-black text-orange-600 dark:text-orange-400">{{ getItemRemainingQty(qtyOverrideItem.item_code) }}</span>
                </div>
                <div class="bg-white dark:bg-slate-700 px-3 py-1.5 rounded-lg border border-gray-200 dark:border-slate-600">
                  <span class="text-gray-400 font-medium">UOM: </span>
                  <span class="font-bold text-gray-600 dark:text-slate-300">{{ qtyOverrideItem.uom || 'Nos' }}</span>
                </div>
              </div>
            </div>
          </Transition>

          <!-- Step 2: Qty Input (only after item resolved) -->
          <div v-if="qtyOverrideItem" class="mb-6">
            <label class="block text-sm font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">New Quantity</label>
            <input type="number" v-model.number="qtyOverrideValue" min="0" step="1" ref="qtyOverrideInputRef"
              @keydown.enter.prevent="applyQtyOverride" @keydown.escape.prevent="closeQtyOverride"
              class="w-full border-3 border-purple-400 dark:border-purple-500 rounded-xl px-6 py-5 text-3xl text-center font-black focus:border-purple-600 focus:ring-4 focus:ring-purple-500/30 bg-purple-50 dark:bg-purple-900/30 dark:text-purple-200 shadow-inner transition-all"
              placeholder="0">
          </div>

          <!-- Stock error inside popup -->
          <Transition name="fade">
            <div v-if="qtyOverrideError" class="flex items-center gap-2 bg-red-600 text-white px-4 py-3 rounded-xl font-bold text-sm mb-4">
              <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/></svg>
              <span>{{ qtyOverrideError }}</span>
              <button @click="qtyOverrideError = ''" class="ml-auto text-white/80 hover:text-white text-lg">&times;</button>
            </div>
          </Transition>

          <!-- Action buttons -->
          <div v-if="qtyOverrideItem" class="flex gap-3">
            <button @click="closeQtyOverride" class="flex-1 py-4 px-4 bg-gray-100 dark:bg-slate-700 text-gray-700 dark:text-slate-200 rounded-xl font-bold text-base hover:bg-gray-200 dark:hover:bg-slate-600 transition-colors">
              Cancel <span class="text-xs text-gray-400 ml-1 border border-gray-300 rounded px-1">Esc</span>
            </button>
            <button @click="applyQtyOverride" class="flex-1 py-4 px-4 bg-purple-600 text-white rounded-xl font-bold text-base hover:bg-purple-700 transition-colors shadow-lg">
              Apply Override <span class="text-xs bg-black/20 px-1.5 rounded ml-1">Enter</span>
            </button>
          </div>

          <!-- Hint when no item resolved yet -->
          <div v-if="!qtyOverrideItem" class="text-center text-sm text-gray-400 dark:text-slate-500 mt-2">
            <p>Scan a barcode or type an item code above, then press <span class="font-bold bg-gray-100 dark:bg-slate-700 px-1.5 py-0.5 rounded text-xs">Enter</span></p>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Picking History (collapsible) -->
    <div v-if="pickingLog.length > 0" class="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-gray-100 dark:border-slate-700 mb-6 overflow-hidden">
      <button @click="showLog = !showLog" class="w-full p-4 flex justify-between items-center text-sm font-bold text-gray-600 dark:text-gray-300 uppercase tracking-wider hover:bg-gray-50 dark:hover:bg-slate-700 transition-colors">
        <span class="flex items-center gap-2">
          <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
          Picking History ({{ pickingLog.length }} scans)
        </span>
        <svg class="w-4 h-4 transition-transform" :class="showLog ? 'rotate-180' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
      </button>
      <div v-if="showLog" class="border-t border-gray-100 dark:border-slate-700 max-h-[300px] overflow-y-auto">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 dark:bg-slate-700 sticky top-0">
            <tr>
              <th class="text-left px-4 py-2 text-xs font-bold text-gray-500 uppercase">#</th>
              <th class="text-left px-4 py-2 text-xs font-bold text-gray-500 uppercase">Time</th>
              <th class="text-left px-4 py-2 text-xs font-bold text-gray-500 uppercase">Item</th>
              <th class="text-left px-4 py-2 text-xs font-bold text-gray-500 uppercase">Barcode</th>
              <th class="text-right px-4 py-2 text-xs font-bold text-gray-500 uppercase">Qty</th>
              <th class="text-left px-4 py-2 text-xs font-bold text-gray-500 uppercase">UOM Factor</th>
              <th class="text-right px-4 py-2 text-xs font-bold text-gray-500 uppercase">Multiplier</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(log, idx) in pickingLog" :key="idx" class="border-t border-gray-50 dark:border-slate-600 hover:bg-gray-50 dark:hover:bg-slate-700/50">
              <td class="px-4 py-2 text-gray-400">{{ idx + 1 }}</td>
              <td class="px-4 py-2 text-gray-500 font-mono text-xs">{{ log.time }}</td>
              <td class="px-4 py-2 font-bold text-gray-700 dark:text-slate-200">{{ log.item_code }}</td>
              <td class="px-4 py-2 text-gray-500 font-mono text-xs">{{ log.barcode }}</td>
              <td class="px-4 py-2 text-right font-black text-green-700">{{ log.qty }}</td>
              <td class="px-4 py-2 text-gray-500">{{ log.uom_factor }}</td>
              <td class="px-4 py-2 text-right text-purple-600 font-bold">×{{ log.multiplier }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue';

const emit = defineEmits(['alert']);
const props = defineProps({ isLoading: Boolean });

// State
const currentSO = ref(null);
const customerName = ref('');
const soStatus = ref(null);
const itemsToPick = ref([]);
const pickedItems = ref([]);
const barcodeMap = ref({});
const soScan = ref('');
const itemScan = ref('');
const flashSuccess = ref(false);
const lastScanInfo = ref('');
const manualQtyMultiplier = ref(1);
const pickingLog = ref([]);
const showLog = ref(false);

// Workflow state
const currentStep = ref(1); // 1=pick, 2=MR draft, 3=SE, 4=complete
const isPartialPick = ref(false);
const mrName = ref(null);
const sourceWarehouse = ref('');
const targetWarehouse = ref('');
const requiredByDate = ref('');
const costCenter = ref('');
const purposeOfTransfer = ref('');
const warehouses = ref([]);
const costCenters = ref([]);
const completedSE = ref({ so_name: '', customer_name: '', mr_name: '', se_name: '', items: [] });
const warehouseConfirmed = ref(false);
const stockLevels = ref({});

const completedCount = ref(0);
const totalPickedCount = ref(0);
const isLoading = ref(false);

const soInputRef = ref(null);
const itemInputRef = ref(null);
const scanError = ref('');
let scanErrorTimer = null;
const originalTotalQty = ref(0); // sum of all order item qtys — denominator for % (allows >100)
const originalItems = ref([]);   // [{item_code, qty}] — for Order Qty column in print

// --- AJAX Warehouse Autocomplete State ---
const sourceWarehouseQuery = ref('');
const targetWarehouseQuery = ref('');
const showSourceDropdown = ref(false);
const showTargetDropdown = ref(false);
const sourceHighlight = ref(0);
const targetHighlight = ref(0);
const srcDropdownContainer = ref(null);
const destDropdownContainer = ref(null);

// Change warehouse mid-pick state
const showChangeWarehouse = ref(false);
const chgSourceQuery = ref('');
const chgTargetQuery = ref('');
const chgSourceWarehouse = ref('');
const chgTargetWarehouse = ref('');
const showChgSourceDropdown = ref(false);
const showChgTargetDropdown = ref(false);
const chgSourceHighlight = ref(0);
const chgTargetHighlight = ref(0);
const chgSrcDropdownContainer = ref(null);
const chgDestDropdownContainer = ref(null);

// Cost Center autocomplete
const costCenterQuery = ref('');
const showCCDropdown = ref(false);
const ccHighlight = ref(0);
const ccDropdownContainer = ref(null);

// Remove item confirmation
const removeTarget = ref(null);

const askRemoveItem = (item) => {
  removeTarget.value = { ...item };
};

const confirmRemoveItem = () => {
  if (!removeTarget.value) return;
  const item = removeTarget.value;
  const pickedIdx = pickedItems.value.findIndex(i => i.item_code === item.item_code && i.source_warehouse === item.source_warehouse && i.target_warehouse === item.target_warehouse);
  if (pickedIdx !== -1) {
    pickedItems.value.splice(pickedIdx, 1);
    // Return qty to itemsToPick
    const toPickIdx = itemsToPick.value.findIndex(i => i.item_code === item.item_code);
    if (toPickIdx !== -1) {
      itemsToPick.value[toPickIdx].qty += item.qty;
    }
    pickingLog.value.push({
      time: new Date().toLocaleTimeString(),
      item_code: item.item_code,
      barcode: '(removed)',
      qty: 0,
      uom_factor: `removed ${item.qty}`,
      multiplier: '×0'
    });
    emit('alert', `Removed ${item.item_code} (${item.qty} ${item.uom || 'Nos'}) from picked items.`, 'success');
  }
  removeTarget.value = null;
  nextTick(() => itemInputRef.value?.focus());
};

// Qty Override (F9) state
const showQtyOverride = ref(false);
const qtyOverrideItem = ref(null);
const qtyOverrideValue = ref(0);
const qtyOverrideInputRef = ref(null);
const qtyOverrideScanInput = ref('');
const qtyOverrideScanRef = ref(null);
const qtyOverrideError = ref('');

// Close B2B pick confirmation
const showCloseConfirm = ref(false);

// --- AJAX Warehouse Computed ---
const filteredSourceWarehouses = computed(() => {
  const q = sourceWarehouseQuery.value.toLowerCase();
  if (!q) return warehouses.value.slice(0, 30);
  return warehouses.value.filter(w => w.toLowerCase().includes(q)).slice(0, 30);
});
const filteredTargetWarehouses = computed(() => {
  const q = targetWarehouseQuery.value.toLowerCase();
  if (!q) return warehouses.value.slice(0, 30);
  return warehouses.value.filter(w => w.toLowerCase().includes(q)).slice(0, 30);
});
const filteredChgSourceWarehouses = computed(() => {
  const q = chgSourceQuery.value.toLowerCase();
  if (!q) return warehouses.value.slice(0, 30);
  return warehouses.value.filter(w => w.toLowerCase().includes(q)).slice(0, 30);
});
const filteredChgTargetWarehouses = computed(() => {
  const q = chgTargetQuery.value.toLowerCase();
  if (!q) return warehouses.value.slice(0, 30);
  return warehouses.value.filter(w => w.toLowerCase().includes(q)).slice(0, 30);
});

const filteredCostCenters = computed(() => {
  const q = costCenterQuery.value.toLowerCase();
  if (!q) return costCenters.value.slice(0, 30);
  return costCenters.value.filter(cc => cc.toLowerCase().includes(q)).slice(0, 30);
});

const onCostCenterInput = () => { showCCDropdown.value = true; ccHighlight.value = 0; costCenter.value = ''; };
const onSourceInput = () => { showSourceDropdown.value = true; sourceHighlight.value = 0; sourceWarehouse.value = ''; };
const onTargetInput = () => { showTargetDropdown.value = true; targetHighlight.value = 0; targetWarehouse.value = ''; };
const onChgSourceInput = () => { showChgSourceDropdown.value = true; chgSourceHighlight.value = 0; chgSourceWarehouse.value = ''; };
const onChgTargetInput = () => { showChgTargetDropdown.value = true; chgTargetHighlight.value = 0; chgTargetWarehouse.value = ''; };

const navigateDropdown = (type, dir) => {
  const map = {
    source: { highlight: sourceHighlight, list: filteredSourceWarehouses },
    target: { highlight: targetHighlight, list: filteredTargetWarehouses },
    chgSource: { highlight: chgSourceHighlight, list: filteredChgSourceWarehouses },
    chgTarget: { highlight: chgTargetHighlight, list: filteredChgTargetWarehouses },
    cc: { highlight: ccHighlight, list: filteredCostCenters },
  };
  const { highlight, list } = map[type];
  const len = list.value.length;
  if (len === 0) return;
  highlight.value = (highlight.value + dir + len) % len;
};

const selectWarehouse = (type, value) => {
  if (type === 'source') { sourceWarehouse.value = value; sourceWarehouseQuery.value = value; showSourceDropdown.value = false; }
  else if (type === 'target') { targetWarehouse.value = value; targetWarehouseQuery.value = value; showTargetDropdown.value = false; }
  else if (type === 'chgSource') { chgSourceWarehouse.value = value; chgSourceQuery.value = value; showChgSourceDropdown.value = false; }
  else if (type === 'chgTarget') { chgTargetWarehouse.value = value; chgTargetQuery.value = value; showChgTargetDropdown.value = false; }
  else if (type === 'cc') { costCenter.value = value; costCenterQuery.value = value; showCCDropdown.value = false; }
};

const selectHighlighted = (type) => {
  const map = {
    source: { highlight: sourceHighlight, list: filteredSourceWarehouses, show: showSourceDropdown },
    target: { highlight: targetHighlight, list: filteredTargetWarehouses, show: showTargetDropdown },
    chgSource: { highlight: chgSourceHighlight, list: filteredChgSourceWarehouses, show: showChgSourceDropdown },
    chgTarget: { highlight: chgTargetHighlight, list: filteredChgTargetWarehouses, show: showChgTargetDropdown },
    cc: { highlight: ccHighlight, list: filteredCostCenters, show: showCCDropdown },
  };
  const { highlight, list, show } = map[type];
  if (list.value.length > 0 && show.value) {
    selectWarehouse(type, list.value[highlight.value]);
  }
};

// Close dropdowns on outside click
const handleClickOutside = (e) => {
  if (srcDropdownContainer.value && !srcDropdownContainer.value.contains(e.target)) showSourceDropdown.value = false;
  if (destDropdownContainer.value && !destDropdownContainer.value.contains(e.target)) showTargetDropdown.value = false;
  if (chgSrcDropdownContainer.value && !chgSrcDropdownContainer.value.contains(e.target)) showChgSourceDropdown.value = false;
  if (chgDestDropdownContainer.value && !chgDestDropdownContainer.value.contains(e.target)) showChgTargetDropdown.value = false;
  if (ccDropdownContainer.value && !ccDropdownContainer.value.contains(e.target)) showCCDropdown.value = false;
};

// Change warehouse mid-pick
const openChangeWarehouse = () => {
  showChangeWarehouse.value = true;
  chgSourceQuery.value = '';
  chgTargetQuery.value = '';
  chgSourceWarehouse.value = '';
  chgTargetWarehouse.value = '';
};

const applyWarehouseChange = async () => {
  const newSrc = chgSourceWarehouse.value || sourceWarehouse.value;
  const newTgt = chgTargetWarehouse.value || targetWarehouse.value;
  if (newSrc === newTgt) {
    emit('alert', 'Source and Destination warehouse cannot be the same!', 'error');
    return;
  }
  sourceWarehouse.value = newSrc;
  sourceWarehouseQuery.value = newSrc;
  targetWarehouse.value = newTgt;
  targetWarehouseQuery.value = newTgt;
  showChangeWarehouse.value = false;
  // Reload stock for new source
  try {
    const itemCodes = itemsToPick.value.map(i => i.item_code);
    if (itemCodes.length > 0) {
      const stock = await apiCall('order_picking.api.api.get_stock_for_items', {
        item_codes: JSON.stringify(itemCodes),
        warehouse: newSrc
      });
      stockLevels.value = stock || {};
    }
  } catch(e) {}
  emit('alert', `Warehouses updated → From: ${newSrc}, To: ${newTgt}. Next scans use these.`, 'success');
  await nextTick();
  itemInputRef.value?.focus();
};

// Shorten warehouse name for display in badges
const shortenWH = (wh) => {
  if (!wh) return '?';
  // Show last part after " - " if exists, otherwise truncate
  const parts = wh.split(' - ');
  return parts.length > 1 ? parts[parts.length - 1] : (wh.length > 20 ? wh.substring(0, 18) + '…' : wh);
};

// --- Qty Override (F3) ---
const getItemRemainingQty = (itemCode) => {
  if (!itemCode) return 0;
  const found = itemsToPick.value.find(i => i.item_code === itemCode);
  return found ? found.qty : 0;
};

const openQtyOverride = () => {
  // Open with scanner field focused — worker scans barcode first, then types qty
  qtyOverrideItem.value = null;
  qtyOverrideScanInput.value = '';
  qtyOverrideValue.value = 0;
  showQtyOverride.value = true;
  nextTick(() => {
    qtyOverrideScanRef.value?.focus();
  });
};

const resolveQtyOverrideItem = () => {
  const val = qtyOverrideScanInput.value.trim();
  if (!val) return;

  // Try to find in picked items by barcode map or item_code
  let matchItemCode = null;
  const bcEntry = barcodeMap.value[val];
  if (bcEntry) {
    matchItemCode = bcEntry.item_code;
  } else {
    // Direct item_code match in picked list
    const found = pickedItems.value.find(i => i.item_code === val);
    if (found) matchItemCode = found.item_code;
    // Also check itemsToPick (item might not be picked yet but exists in order)
    if (!matchItemCode) {
      const foundInOrder = itemsToPick.value.find(i => i.item_code === val);
      if (foundInOrder) matchItemCode = foundInOrder.item_code;
    }
  }

  if (!matchItemCode) {
    emit('alert', `Item not found for barcode/SKU: ${val}`, 'error');
    qtyOverrideScanInput.value = '';
    return;
  }

  // Find in picked items
  const pickedItem = pickedItems.value.find(i => i.item_code === matchItemCode);
  if (pickedItem) {
    qtyOverrideItem.value = { ...pickedItem };
    qtyOverrideValue.value = pickedItem.qty;
  } else {
    // Item exists in order but not yet picked — show with qty 0
    const orderItem = itemsToPick.value.find(i => i.item_code === matchItemCode);
    qtyOverrideItem.value = {
      item_code: matchItemCode,
      item_name: orderItem?.item_name || '',
      image: orderItem?.image || '',
      uom: orderItem?.uom || 'Nos',
      qty: 0,
      source_warehouse: sourceWarehouse.value,
      target_warehouse: targetWarehouse.value,
    };
    qtyOverrideValue.value = 0;
  }

  qtyOverrideScanInput.value = '';
  nextTick(() => {
    qtyOverrideInputRef.value?.focus();
    qtyOverrideInputRef.value?.select();
  });
};

const closeQtyOverride = () => {
  showQtyOverride.value = false;
  qtyOverrideItem.value = null;
  qtyOverrideValue.value = 0;
  qtyOverrideScanInput.value = '';
  qtyOverrideError.value = '';
  nextTick(() => itemInputRef.value?.focus());
};

const applyQtyOverride = () => {
  if (!qtyOverrideItem.value) return;
  const itemCode = qtyOverrideItem.value.item_code;
  const newQty = Math.max(0, Math.floor(qtyOverrideValue.value || 0));
  const pickedIdx = pickedItems.value.findIndex(i => i.item_code === itemCode);
  const oldQty = pickedIdx !== -1 ? pickedItems.value[pickedIdx].qty : 0;
  const diff = newQty - oldQty;

  // Stock availability check — F9 override cannot exceed physical stock
  if (stockLevels.value[itemCode] !== undefined) {
    const alreadyPickedFromWH = pickedItems.value
      .filter(i => i.item_code === itemCode && i.source_warehouse === (qtyOverrideItem.value?.source_warehouse || sourceWarehouse.value))
      .reduce((a, i) => a + i.qty, 0);
    const availableStock = stockLevels.value[itemCode] - (alreadyPickedFromWH - oldQty);
    if (newQty > availableStock) {
      qtyOverrideError.value = `Insufficient stock! Only ${availableStock} available in ${qtyOverrideItem.value?.source_warehouse || sourceWarehouse.value}.`;
      return;
    }
  }
  qtyOverrideError.value = '';

  // Clamp remaining at 0, never go negative
  const toPickIdx = itemsToPick.value.findIndex(i => i.item_code === itemCode);
  if (toPickIdx !== -1) {
    itemsToPick.value[toPickIdx].qty = Math.max(0, itemsToPick.value[toPickIdx].qty - diff);
  }

  if (newQty <= 0 && pickedIdx !== -1) {
    // Remove from picked
    pickedItems.value.splice(pickedIdx, 1);
  } else if (newQty > 0 && pickedIdx !== -1) {
    pickedItems.value[pickedIdx].qty = newQty;
  } else if (newQty > 0 && pickedIdx === -1) {
    // Item not yet in picked list — add it
    pickedItems.value.push({
      item_code: itemCode,
      item_name: qtyOverrideItem.value.item_name,
      image: qtyOverrideItem.value.image,
      uom: qtyOverrideItem.value.uom,
      qty: newQty,
      source_warehouse: qtyOverrideItem.value.source_warehouse || sourceWarehouse.value,
      target_warehouse: qtyOverrideItem.value.target_warehouse || targetWarehouse.value,
    });
  }

  // Log the override
  pickingLog.value.push({
    time: new Date().toLocaleTimeString(),
    item_code: itemCode,
    barcode: '(F9 override)',
    qty: newQty,
    uom_factor: `was ${oldQty}`,
    multiplier: '→' + newQty
  });

  emit('alert', `Qty for ${itemCode} changed: ${oldQty} → ${newQty}`, 'success');
  closeQtyOverride();
};

// B2B keyboard handler
const handleB2BKeydown = (e) => {
  // Escape key handling — priority order: override popup > remove modal > close confirmation > warn if picking
  if (e.key === 'Escape') {
    if (showQtyOverride.value) {
      e.preventDefault();
      closeQtyOverride();
      return;
    }
    if (removeTarget.value) {
      e.preventDefault();
      removeTarget.value = null;
      nextTick(() => itemInputRef.value?.focus());
      return;
    }
    if (showCloseConfirm.value) {
      // Swallow Esc entirely — modal must be dismissed via buttons only
      e.preventDefault();
      e.stopImmediatePropagation();
      return;
    }
    // If picking is in progress, show confirmation before closing
    if (currentStep.value === 1 && pickedItems.value.length > 0) {
      e.preventDefault();
      showCloseConfirm.value = true;
      return;
    }
    // Otherwise let the default Esc propagate (close B2B pick normally)
    return;
  }

  // Ctrl+Z: Remove last picked item (undo)
  if ((e.ctrlKey || e.metaKey) && e.key === 'z') {
    if (currentStep.value === 1 && pickedItems.value.length > 0 && !showQtyOverride.value && !removeTarget.value) {
      e.preventDefault();
      askRemoveItem(pickedItems.value[pickedItems.value.length - 1]);
    }
    return;
  }
  // F9: Qty Override (scanner-friendly popup)
  if (e.key === 'F9') {
    e.preventDefault();
    if (currentStep.value === 1 && warehouseConfirmed.value) {
      openQtyOverride();
    }
  }
  // F5: Change Warehouse
  if (e.key === 'F5') {
    e.preventDefault();
    if (currentStep.value === 1 && warehouseConfirmed.value) {
      if (showChangeWarehouse.value) {
        showChangeWarehouse.value = false;
        nextTick(() => itemInputRef.value?.focus());
      } else {
        openChangeWarehouse();
      }
    }
  }
};

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
  window.addEventListener('keydown', handleB2BKeydown);
});
onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
  window.removeEventListener('keydown', handleB2BKeydown);
  if (scanErrorTimer) clearTimeout(scanErrorTimer);
});

// CSRF
const csrf_token = window?.frappe?.csrf_token || '';

const apiCall = async (method, args = {}) => {
  isLoading.value = true;
  try {
    const response = await fetch(`/api/method/${method}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Frappe-CSRF-Token": csrf_token },
      body: JSON.stringify(args)
    });
    if (!response.ok) {
      let errMessage = `HTTP Error ${response.status}`;
      try {
        const data = await response.json();
        if (data.exc_type) errMessage = data.exc_type;
        if (data._server_messages) {
          const msgs = JSON.parse(data._server_messages);
          errMessage = JSON.parse(msgs[0]).message || errMessage;
        }
      } catch(e) {}
      throw new Error(errMessage);
    }
    const data = await response.json();
    if (data.message && data.message.error) throw new Error(data.message.error);
    return data.message;
  } catch (error) {
    emit('alert', error.message, 'error');
    throw error;
  } finally {
    isLoading.value = false;
  }
};

const percentage = computed(() => {
  if (originalTotalQty.value === 0) return 0;
  const totalPicked = pickedItems.value.reduce((a, o) => a + o.qty, 0);
  // Can exceed 100% when over-picked via F9 override
  return Math.round((totalPicked / originalTotalQty.value) * 100);
});

const stepClass = (step) => {
  if (step < currentStep.value) return 'text-green-600 bg-green-50';
  if (step === currentStep.value) return 'text-purple-700 bg-purple-50 ring-1 ring-purple-200';
  return 'text-gray-400 bg-gray-50';
};
const stepNumClass = (step) => {
  if (step < currentStep.value) return 'bg-green-500 text-white border-green-500';
  if (step === currentStep.value) return 'bg-purple-500 text-white border-purple-500';
  return 'bg-gray-200 text-gray-500 border-gray-300';
};

// Load warehouses/cost centers
onMounted(async () => {
  try {
    const data = await apiCall('order_picking.api.api.get_warehouses_and_cost_centers');
    warehouses.value = data.warehouses || [];
    costCenters.value = data.cost_centers || [];
  } catch(e) {}
  const today = new Date();
  // Use local date to avoid timezone mismatch with server transaction date
  const yyyy = today.getFullYear();
  const mm = String(today.getMonth() + 1).padStart(2, '0');
  const dd = String(today.getDate()).padStart(2, '0');
  requiredByDate.value = `${yyyy}-${mm}-${dd}`;
  await nextTick();
  soInputRef.value?.focus();
});

const handleSOScan = async () => {
  const val = soScan.value.trim();
  if (!val) return;
  try {
    const data = await apiCall('order_picking.api.api.get_sales_order_items', { scan_input: val });
    if (data) {
      currentSO.value = data.so_name;
      customerName.value = data.customer_name || '';
      soStatus.value = data.status || null;
      itemsToPick.value = JSON.parse(JSON.stringify(data.items));
      originalItems.value = data.items.map(i => ({ item_code: i.item_code, qty: i.qty, item_name: i.item_name, uom: i.uom }));
      originalTotalQty.value = data.items.reduce((a, i) => a + i.qty, 0);
      pickedItems.value = [];
      barcodeMap.value = data.barcode_map || {};
      currentStep.value = 1;
      mrName.value = null;
      lastScanInfo.value = '';
      soScan.value = '';
      warehouseConfirmed.value = false;
      stockLevels.value = {};
      showChangeWarehouse.value = false;
      sourceWarehouseQuery.value = sourceWarehouse.value;
      targetWarehouseQuery.value = targetWarehouse.value;
      emit('alert', `Loaded Sales Order ${currentSO.value} — Customer: ${customerName.value}. Select warehouses to start picking.`, 'success');
    }
  } catch(e) {
    soScan.value = '';
    soInputRef.value?.focus();
  }
};

const confirmWarehouses = async () => {
  if (!sourceWarehouse.value || !targetWarehouse.value) return;
  if (sourceWarehouse.value === targetWarehouse.value) {
    emit('alert', 'Source and Destination warehouse cannot be the same!', 'error');
    return;
  }
  try {
    const itemCodes = itemsToPick.value.map(i => i.item_code);
    const stock = await apiCall('order_picking.api.api.get_stock_for_items', {
      item_codes: JSON.stringify(itemCodes),
      warehouse: sourceWarehouse.value
    });
    stockLevels.value = stock || {};
    warehouseConfirmed.value = true;
    emit('alert', `Warehouses confirmed. Stock levels loaded from ${sourceWarehouse.value}. Start scanning items!`, 'success');
    await nextTick();
    itemInputRef.value?.focus();
  } catch(e) {
    emit('alert', 'Failed to load stock levels. Please try again.', 'error');
  }
};

const handleItemScan = () => {
  const val = itemScan.value.trim();
  if (!val) return;

  const multiplier = Math.max(1, Math.floor(manualQtyMultiplier.value || 1));

  // Check barcode map first
  const bcEntry = barcodeMap.value[val];
  let matchItemCode = null;
  let uomFactor = 1;

  if (bcEntry) {
    matchItemCode = bcEntry.item_code;
    uomFactor = bcEntry.qty || 1;
  } else {
    // Fallback: match by item_code directly
    const found = itemsToPick.value.find(i => i.item_code === val);
    if (found) matchItemCode = found.item_code;
  }

  if (!matchItemCode) {
    scanError.value = `Barcode not found in this Sales Order: ${val}`;
    if (scanErrorTimer) clearTimeout(scanErrorTimer);
    scanErrorTimer = setTimeout(() => { scanError.value = ''; }, 5000);
    itemScan.value = '';
    return;
  }

  const foundIndex = itemsToPick.value.findIndex(i => i.item_code === matchItemCode);
  if (foundIndex === -1 || itemsToPick.value[foundIndex].qty <= 0) {
    scanError.value = `${matchItemCode} is already fully picked! Use F9 to override.`;
    if (scanErrorTimer) clearTimeout(scanErrorTimer);
    scanErrorTimer = setTimeout(() => { scanError.value = ''; }, 5000);
    itemScan.value = '';
    return;
  }
  scanError.value = '';

  // Total qty = UOM factor × manual multiplier — reject if over remaining
  const scanQty = uomFactor * multiplier;
  const remaining = itemsToPick.value[foundIndex].qty;

  if (scanQty > remaining) {
    scanError.value = `Over-pick! Adding ${scanQty} but only ${remaining} left for ${matchItemCode}. Reduce × Qty, or press F9 to override.`;
    if (scanErrorTimer) clearTimeout(scanErrorTimer);
    scanErrorTimer = setTimeout(() => { scanError.value = ''; }, 5000);
    itemScan.value = '';
    return;
  }

  // Stock availability check — cannot pick more than physical stock in source WH
  if (stockLevels.value[matchItemCode] !== undefined) {
    const alreadyPickedFromWH = pickedItems.value
      .filter(i => i.item_code === matchItemCode && i.source_warehouse === sourceWarehouse.value)
      .reduce((a, i) => a + i.qty, 0);
    const availableStock = stockLevels.value[matchItemCode] - alreadyPickedFromWH;
    if (scanQty > availableStock) {
      scanError.value = `Insufficient stock! Only ${availableStock} available in ${sourceWarehouse.value} for ${matchItemCode}.`;
      if (scanErrorTimer) clearTimeout(scanErrorTimer);
      scanErrorTimer = setTimeout(() => { scanError.value = ''; }, 5000);
      itemScan.value = '';
      return;
    }
  }
  scanError.value = '';

  const actualQty = scanQty;
  itemsToPick.value[foundIndex].qty -= actualQty;

  // Use a composite key: item_code + source + target warehouse for multi-WH support
  const activeSrc = sourceWarehouse.value;
  const activeTgt = targetWarehouse.value;
  const pickedIndex = pickedItems.value.findIndex(i => i.item_code === matchItemCode && i.source_warehouse === activeSrc && i.target_warehouse === activeTgt);
  if (pickedIndex !== -1) {
    pickedItems.value[pickedIndex].qty += actualQty;
  } else {
    pickedItems.value.push({
      item_code: matchItemCode,
      item_name: itemsToPick.value[foundIndex].item_name,
      image: itemsToPick.value[foundIndex].image,
      uom: itemsToPick.value[foundIndex].uom,
      qty: actualQty,
      source_warehouse: activeSrc,
      target_warehouse: activeTgt,
    });
  }

  // Log this scan
  const now = new Date();
  pickingLog.value.push({
    time: now.toLocaleTimeString(),
    item_code: matchItemCode,
    barcode: val,
    qty: actualQty,
    uom_factor: uomFactor > 1 ? `${uomFactor}/scan` : '1 (unit)',
    multiplier: multiplier
  });

  lastScanInfo.value = `Scanned ${matchItemCode} × ${actualQty}`
    + (uomFactor > 1 ? ` (UOM: ${uomFactor} × ${multiplier})` : (multiplier > 1 ? ` (× ${multiplier})` : ''));

  flashSuccess.value = true;
  setTimeout(() => flashSuccess.value = false, 200);

  // Reset multiplier back to 1 after scan
  manualQtyMultiplier.value = 1;

  if (percentage.value === 100) {
    emit('alert', 'All items picked! Fill warehouse details and create Material Request.', 'success');
  }

  itemScan.value = '';
};

const printPickList = () => {
  const orderQtyMap = {};
  originalItems.value.forEach(i => { orderQtyMap[i.item_code] = i.qty; });
  // Build item_code → scanned barcode map from picking log (only barcodes actually scanned)
  const scannedBarcodes = {};
  pickingLog.value.forEach(log => {
    if (log.item_code && log.barcode && log.barcode !== '(F9 override)') {
      scannedBarcodes[log.item_code] = log.barcode;
    }
  });
  const rows = pickedItems.value.map((item, idx) => {
    const orderQty = orderQtyMap[item.item_code] || 0;
    const overPick = item.qty > orderQty;
    const barcodes = scannedBarcodes[item.item_code] || '';
    return `<tr>
      <td style="padding:6px 12px;border:1px solid #ddd">${idx+1}</td>
      <td style="padding:6px 12px;border:1px solid #ddd;font-weight:bold">${item.item_code}${barcodes ? `<br><span style="font-weight:normal;font-size:10px;color:#888;font-family:monospace">${barcodes}</span>` : ''}</td>
      <td style="padding:6px 12px;border:1px solid #ddd">${item.item_name||''}</td>
      <td style="padding:6px 12px;border:1px solid #ddd;text-align:right;color:#666">${orderQty}</td>
      <td style="padding:6px 12px;border:1px solid #ddd;text-align:right;font-weight:bold;color:${overPick?'#dc2626':'#16a34a'}">${item.qty}${overPick?' ⚠':''}</td>
      <td style="padding:6px 12px;border:1px solid #ddd">${item.uom||'Nos'}</td>
      <td style="padding:6px 12px;border:1px solid #ddd;font-size:11px">${item.source_warehouse||''} → ${item.target_warehouse||''}</td>
    </tr>`;
  }).join('');
  const logRows = pickingLog.value.map((log, idx) =>
    `<tr><td style="padding:4px 8px;border:1px solid #eee;font-size:11px">${idx+1}</td><td style="padding:4px 8px;border:1px solid #eee;font-size:11px">${log.time}</td><td style="padding:4px 8px;border:1px solid #eee;font-size:11px;font-weight:bold">${log.item_code}</td><td style="padding:4px 8px;border:1px solid #eee;font-size:11px;font-family:monospace">${log.barcode}</td><td style="padding:4px 8px;border:1px solid #eee;font-size:11px;text-align:right;font-weight:bold">${log.qty}</td><td style="padding:4px 8px;border:1px solid #eee;font-size:11px">×${log.multiplier} (${log.uom_factor})</td></tr>`
  ).join('');
  const html = `<html><head><title>B2B Pick List — ${currentSO.value}</title><style>body{font-family:system-ui,sans-serif;padding:30px;color:#333}table{border-collapse:collapse;width:100%}th{background:#f3f4f6;text-align:left;padding:8px 12px;border:1px solid #ddd;font-size:12px;text-transform:uppercase}</style></head><body>` +
    `<h1 style="margin:0 0 4px">B2B Pick List</h1>` +
    `<p style="color:#666;margin:0 0 4px"><strong>Sales Order:</strong> ${currentSO.value} &nbsp; <strong>Customer:</strong> ${customerName.value} &nbsp; <strong>Status:</strong> ${soStatus.value||'N/A'} &nbsp; <strong>Picked:</strong> ${percentage.value}%</p>` +
    `<p style="color:#999;margin:0 0 20px;font-size:12px">Printed: ${new Date().toLocaleString()}</p>` +
    `<h3 style="margin:0 0 8px">Picked Items Summary</h3>` +
    `<table><thead><tr><th>#</th><th>Item Code</th><th>Item Name</th><th style="text-align:right">Order Qty</th><th style="text-align:right">Picked Qty</th><th>UOM</th><th>Warehouse</th></tr></thead><tbody>${rows}</tbody></table>` +
    (logRows ? `<h3 style="margin:24px 0 8px">Scan Log</h3><table><thead><tr><th>#</th><th>Time</th><th>Item</th><th>Barcode</th><th style="text-align:right">Qty</th><th>Details</th></tr></thead><tbody>${logRows}</tbody></table>` : '') +
    `</body></html>`;
  const w = window.open('', '_blank');
  w.document.write(html);
  w.document.close();
  w.focus();
  w.print();
};

const createMR = async () => {
  try {
    // Determine if this is a partial pick
    isPartialPick.value = percentage.value < 100;
    // Include per-item warehouse info for multi source/dest support
    const items = pickedItems.value.map(i => ({
      item_code: i.item_code,
      qty: i.qty,
      uom: i.uom || 'Nos',
      source_warehouse: i.source_warehouse || sourceWarehouse.value,
      target_warehouse: i.target_warehouse || targetWarehouse.value,
    }));
    const data = await apiCall('order_picking.api.api.create_b2b_material_request', {
      so_name: currentSO.value,
      items: JSON.stringify(items),
      source_warehouse: sourceWarehouse.value,
      target_warehouse: targetWarehouse.value,
      required_by_date: requiredByDate.value
    });
    mrName.value = data.mr_name;
    currentStep.value = 2;
    emit('alert', `Material Request ${data.mr_name} created successfully!`, 'success');
  } catch(e) {}
};

const submitMR = async () => {
  try {
    await apiCall('order_picking.api.api.submit_b2b_material_request', { mr_name: mrName.value });
    currentStep.value = 3;
    purposeOfTransfer.value = `Transfer by B2B Order Pick for ${customerName.value}`;
    emit('alert', `Material Request ${mrName.value} submitted!`, 'success');
  } catch(e) {}
};

const createSE = async () => {
  try {
    const data = await apiCall('order_picking.api.api.create_b2b_stock_entry', {
      mr_name: mrName.value,
      cost_center: costCenter.value,
      purpose_of_transfer: purposeOfTransfer.value,
      is_partial: isPartialPick.value ? 1 : 0,
      original_items: JSON.stringify(originalItems.value),
      picking_log: JSON.stringify(pickingLog.value)
    });
    const statusLabel = isPartialPick.value ? 'Consignment Partially Delivered' : 'Consignment Delivered';
    emit('alert', `Stock Entry ${data.se_name} created & submitted! Status: ${statusLabel}`, 'success');
    completedCount.value++;
    totalPickedCount.value += pickedItems.value.reduce((a, o) => a + o.qty, 0);

    // Store completion data for summary / print
    completedSE.value = {
      so_name: data.so_name || currentSO.value || '',
      customer_name: data.customer_name || customerName.value || '',
      mr_name: data.mr_name || mrName.value || '',
      se_name: data.se_name || '',
      items: data.items || pickedItems.value.map(i => ({
        item_code: i.item_code,
        item_name: i.item_name,
        qty: i.qty,
        uom: i.uom || 'Nos',
        from_warehouse: sourceWarehouse.value,
        to_warehouse: targetWarehouse.value
      }))
    };

    // Go to step 4 (completed) instead of immediately resetting
    currentStep.value = 4;
  } catch(e) {}
};

const printCompletedSummary = () => {
  const c = completedSE.value;
  const orderQtyMap = {};
  originalItems.value.forEach(i => { orderQtyMap[i.item_code] = (orderQtyMap[i.item_code] || 0) + i.qty; });
  // Build item_code → scanned barcode map from picking log (only barcodes actually scanned)
  const scannedBarcodes = {};
  pickingLog.value.forEach(log => {
    if (log.item_code && log.barcode && log.barcode !== '(F9 override)') {
      scannedBarcodes[log.item_code] = log.barcode;
    }
  });
  const rows = c.items.map((item, idx) => {
    const orderQty = orderQtyMap[item.item_code] || 0;
    const overPick = item.qty > orderQty;
    const barcodes = scannedBarcodes[item.item_code] || '';
    return `<tr><td style="padding:6px 12px;border:1px solid #ddd">${idx+1}</td><td style="padding:6px 12px;border:1px solid #ddd;font-weight:bold">${item.item_code}${barcodes ? `<br><span style="font-weight:normal;font-size:10px;color:#888;font-family:monospace">${barcodes}</span>` : ''}</td><td style="padding:6px 12px;border:1px solid #ddd">${item.item_name||''}</td><td style="padding:6px 12px;border:1px solid #ddd;text-align:right">${orderQty}</td><td style="padding:6px 12px;border:1px solid #ddd;text-align:right;font-weight:bold;color:${overPick?'#dc2626':'#16a34a'}">${item.qty}${overPick?' ⚠':''}</td><td style="padding:6px 12px;border:1px solid #ddd">${item.uom||'Nos'}</td><td style="padding:6px 12px;border:1px solid #ddd;font-size:11px">${item.from_warehouse||''}</td><td style="padding:6px 12px;border:1px solid #ddd;font-size:11px">${item.to_warehouse||''}</td></tr>`;
  }).join('');
  const logRows = pickingLog.value.map((log, idx) =>
    `<tr><td style="padding:4px 8px;border:1px solid #eee;font-size:11px">${idx+1}</td><td style="padding:4px 8px;border:1px solid #eee;font-size:11px">${log.time}</td><td style="padding:4px 8px;border:1px solid #eee;font-size:11px;font-weight:bold">${log.item_code}</td><td style="padding:4px 8px;border:1px solid #eee;font-size:11px;font-family:monospace">${log.barcode}</td><td style="padding:4px 8px;border:1px solid #eee;font-size:11px;text-align:right;font-weight:bold">${log.qty}</td><td style="padding:4px 8px;border:1px solid #eee;font-size:11px">&times;${log.multiplier} (${log.uom_factor})</td></tr>`
  ).join('');
  const html = `<html><head><title>B2B Pick Summary &mdash; ${c.so_name}</title><style>body{font-family:system-ui,sans-serif;padding:30px;color:#333}table{border-collapse:collapse;width:100%}th{background:#f3f4f6;text-align:left;padding:8px 12px;border:1px solid #ddd;font-size:12px;text-transform:uppercase}.badge{display:inline-block;padding:4px 10px;border-radius:6px;font-size:12px;font-weight:bold;margin-right:8px}</style></head><body>` +
    `<h1 style="margin:0 0 4px">B2B Order Pick &mdash; Completion Summary</h1>` +
    `<p style="color:#666;margin:0 0 4px"><strong>Sales Order:</strong> ${c.so_name} &nbsp; <strong>Customer:</strong> ${c.customer_name}</p>` +
    `<p style="color:#666;margin:0 0 4px"><span class="badge" style="background:#fef3c7;color:#92400e">MR: ${c.mr_name}</span><span class="badge" style="background:#d1fae5;color:#065f46">SE: ${c.se_name}</span></p>` +
    `<p style="color:#999;margin:0 0 20px;font-size:12px">Printed: ${new Date().toLocaleString()}</p>` +
    `<h3 style="margin:0 0 8px">Transfer Items</h3>` +
    `<table><thead><tr><th>#</th><th>Item Code</th><th>Item Name</th><th style="text-align:right">Order Qty</th><th style="text-align:right">Picked Qty</th><th>UOM</th><th>Source WH</th><th>Dest WH</th></tr></thead><tbody>${rows}</tbody></table>` +
    (logRows ? `<h3 style="margin:24px 0 8px">Scan Log (${pickingLog.value.length} scans)</h3><table><thead><tr><th>#</th><th>Time</th><th>Item</th><th>Barcode</th><th style="text-align:right">Qty</th><th>Details</th></tr></thead><tbody>${logRows}</tbody></table>` : '') +
    `</body></html>`;
  const w = window.open('', '_blank');
  w.document.write(html);
  w.document.close();
  w.focus();
  w.print();
};

const resetForNextOrder = async () => {
  currentSO.value = null;
  customerName.value = '';
  soStatus.value = null;
  itemsToPick.value = [];
  pickedItems.value = [];
  barcodeMap.value = {};
  originalItems.value = [];
  originalTotalQty.value = 0;
  mrName.value = null;
  currentStep.value = 1;
  sourceWarehouse.value = '';
  targetWarehouse.value = '';
  sourceWarehouseQuery.value = '';
  targetWarehouseQuery.value = '';
  costCenter.value = '';
  costCenterQuery.value = '';
  purposeOfTransfer.value = '';
  lastScanInfo.value = '';
  manualQtyMultiplier.value = 1;
  pickingLog.value = [];
  showLog.value = false;
  completedSE.value = { so_name: '', customer_name: '', mr_name: '', se_name: '', items: [] };
  warehouseConfirmed.value = false;
  stockLevels.value = {};
  isPartialPick.value = false;
  showChangeWarehouse.value = false;
  showQtyOverride.value = false;
  removeTarget.value = null;
  scanError.value = '';
  if (scanErrorTimer) clearTimeout(scanErrorTimer);
  const today = new Date();
  const yyyy = today.getFullYear();
  const mm = String(today.getMonth() + 1).padStart(2, '0');
  const dd = String(today.getDate()).padStart(2, '0');
  requiredByDate.value = `${yyyy}-${mm}-${dd}`;
  await nextTick();
  soInputRef.value?.focus();
};

// Expose refs for parent focus management
defineExpose({ soInputRef, itemInputRef, openQtyOverride, openChangeWarehouse });
</script>
