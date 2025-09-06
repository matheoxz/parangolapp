package com.mthxz.parangolapp.services

import android.content.Context
import android.net.nsd.NsdManager
import android.net.nsd.NsdServiceInfo
import android.util.Log
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

data class OSCService(
    val name: String,
    val ip: String,
    val port: Int
)

class OSCmDNSScanner(context: Context) {
    private val nsdManager = context.getSystemService(Context.NSD_SERVICE) as NsdManager
    private val SERVICE_TYPE = "_osc._udp."

    private val _oscServices = MutableStateFlow<List<OSCService>>(emptyList())
    val oscServices: StateFlow<List<OSCService>> = _oscServices.asStateFlow()

    private val discoveryListener = object : NsdManager.DiscoveryListener {
        override fun onStartDiscoveryFailed(serviceType: String, errorCode: Int) {
            Log.e("OSCmDNSScanner", "Discovery failed to start with error code: $errorCode")
        }

        override fun onStopDiscoveryFailed(serviceType: String, errorCode: Int) {
            Log.e("OSCmDNSScanner", "Discovery failed to stop with error code: $errorCode")
        }

        override fun onDiscoveryStarted(serviceType: String) {
            Log.d("OSCmDNSScanner", "Discovery started")
        }

        override fun onDiscoveryStopped(serviceType: String) {
            Log.d("OSCmDNSScanner", "Discovery stopped")
        }

        override fun onServiceFound(serviceInfo: NsdServiceInfo) {
            Log.d("OSCmDNSScanner", "Service found: ${serviceInfo.serviceName}")
            nsdManager.resolveService(serviceInfo, resolveListener)
        }

        override fun onServiceLost(serviceInfo: NsdServiceInfo) {
            Log.d("OSCmDNSScanner", "Service lost: ${serviceInfo.serviceName}")
            val currentList = _oscServices.value.toMutableList()
            currentList.removeAll { it.name == serviceInfo.serviceName }
            _oscServices.value = currentList
        }
    }

    private val resolveListener = object : NsdManager.ResolveListener {
        override fun onResolveFailed(serviceInfo: NsdServiceInfo, errorCode: Int) {
            Log.e("OSCmDNSScanner", "Resolve failed for ${serviceInfo.serviceName}: $errorCode")
        }

        override fun onServiceResolved(serviceInfo: NsdServiceInfo) {
            Log.d("OSCmDNSScanner", "Resolved service: ${serviceInfo.serviceName}")
            val oscService = OSCService(
                name = serviceInfo.serviceName,
                ip = serviceInfo.host.hostAddress ?: return,
                port = serviceInfo.port
            )

            val currentList = _oscServices.value.toMutableList()
            if (!currentList.any { it.ip == oscService.ip }) {
                currentList.add(oscService)
                _oscServices.value = currentList
            }
        }
    }

    fun startDiscovery() {
        try {
            nsdManager.discoverServices(
                SERVICE_TYPE,
                NsdManager.PROTOCOL_DNS_SD,
                discoveryListener
            )
        } catch (e: Exception) {
            Log.e("OSCmDNSScanner", "Failed to start discovery", e)
        }
    }

    fun stopDiscovery() {
        try {
            nsdManager.stopServiceDiscovery(discoveryListener)
        } catch (e: Exception) {
            Log.e("OSCmDNSScanner", "Failed to stop discovery", e)
        }
    }
}
