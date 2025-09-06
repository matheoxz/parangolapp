package com.mthxz.parangolapp.ui.osc

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.mthxz.parangolapp.services.OSCService
import com.mthxz.parangolapp.services.OSCmDNSScanner
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class OSCViewModel(application: Application) : AndroidViewModel(application) {
    private val scanner = OSCmDNSScanner(application)

    private val _selectedService = MutableStateFlow<OSCService?>(null)
    val selectedService: StateFlow<OSCService?> = _selectedService.asStateFlow()

    private val _discoveredServices = MutableStateFlow<List<OSCService>>(emptyList())
    val discoveredServices: StateFlow<List<OSCService>> = _discoveredServices.asStateFlow()

    init {
        startScanning()
        viewModelScope.launch {
            scanner.oscServices.collect { services ->
                _discoveredServices.value = services
            }
        }
    }

    private fun startScanning() {
        viewModelScope.launch {
            scanner.startDiscovery()
        }
    }

    fun selectService(service: OSCService) {
        _selectedService.value = service
    }

    override fun onCleared() {
        super.onCleared()
        scanner.stopDiscovery()
    }
}
