package com.mthxz.parangolapp

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.runtime.Composable
import androidx.compose.ui.platform.LocalContext
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.mthxz.parangolapp.data.BleDevice
import com.mthxz.parangolapp.service.BleScannerService
import com.mthxz.parangolapp.ui.ble.BleScanScreen
import com.mthxz.parangolapp.ui.wifi.WifiConfigurationScreen
import com.mthxz.parangolapp.ui.ip.IPScreen

@Composable
fun MainScreen() {
    val navController = rememberNavController()
    val bleScannerService = BleScannerService(LocalContext.current)

    NavHost(
        navController = navController,
        startDestination = "bleScan"
    ) {
        composable("bleScan") {
            BleScanScreen(
                navController = navController,
                onDeviceSelected = { device ->
                    bleScannerService.connectToDevice(device.address)
                    navController.navigate("wifiConfiguration")
                }
            )
        }
        composable("wifiConfiguration") {
            WifiConfigurationScreen(
                navController = navController,
                selectedBleDevice = BleDevice("ESP32_Device", "00:11:22:33:AA:BB"),
                onSendCredentials = { ssid, password ->
                    bleScannerService.sendCredentials(ssid, password)
                    navController.navigate("ipScreen")
                },
            )
        }
        composable("ipScreen") {
            IPScreen(
                bleScannerService = bleScannerService,
                onRetry = { /* Handle retry */ }
            )
        }
    }
}

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            // Apply theme with automatic dark/light mode
            com.mthxz.parangolapp.ui.theme.ParangolappTheme {
                MainScreen()
            }
        }
    }
}
