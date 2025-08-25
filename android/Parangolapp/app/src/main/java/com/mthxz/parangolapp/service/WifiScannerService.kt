package com.mthxz.parangolapp.service

import android.Manifest
import android.content.Context
import android.net.wifi.ScanResult
import android.net.wifi.WifiManager
import androidx.annotation.RequiresPermission
import com.mthxz.parangolapp.data.WifiNetwork

class WifiScannerService(context: Context) {

    private val wifiManager = context.applicationContext.getSystemService(Context.WIFI_SERVICE) as WifiManager

    fun startWifiScan() {
        wifiManager.startScan()
    }

    @RequiresPermission(Manifest.permission.ACCESS_FINE_LOCATION)
    fun getAvailableNetworks(): List<WifiNetwork> {
        val scanResults: List<ScanResult> = wifiManager.scanResults

        // only 2.4 GHz PSK networks (WPA personal), no enterprise/EAP or WEP
        val filtered = scanResults.filter { result ->
            result.frequency in 2400..2500 &&
            result.capabilities.contains("PSK") &&
            !result.capabilities.contains("EAP") &&
            !result.capabilities.contains("WEP")
        }

        return filtered.map { result ->
            // all are secure at this point
            WifiNetwork(result.SSID, true)
        }
    }
}
