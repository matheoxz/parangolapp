package com.mthxz.parangolapp.ui.ble

import android.annotation.SuppressLint
import android.content.Context
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.mthxz.parangolapp.service.BleScannerService
import kotlinx.coroutines.launch

@SuppressLint("MissingPermission")
class BleViewModel(private val context: Context) : ViewModel() {

    private val bleScannerService = BleScannerService(context)

    val isScanning = bleScannerService.isScanning
    val discoveredDevices = bleScannerService.discoveredDevices
    val errorMessage = bleScannerService.errorMessage

    fun startScan() {
        viewModelScope.launch {
            bleScannerService.startScan()
        }
    }

    fun stopScan() {
        viewModelScope.launch {
            bleScannerService.stopScan()
        }
    }
}
