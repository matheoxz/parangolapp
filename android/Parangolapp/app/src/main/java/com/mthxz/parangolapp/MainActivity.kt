package com.mthxz.parangolapp

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.platform.LocalContext
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.mthxz.parangolapp.data.BleDevice
import com.mthxz.parangolapp.ui.ble.BleScanScreen
import com.mthxz.parangolapp.ui.ble.BleViewModel
import com.mthxz.parangolapp.ui.connected.ConnectedScreen
import com.mthxz.parangolapp.ui.wifi.WifiConfigurationScreen

@Composable
fun MainScreen() {
    val navController = rememberNavController()
    val context = LocalContext.current
    val bleViewModel = remember { BleViewModel(context) }
    var selectedBleDevice by remember { mutableStateOf<BleDevice?>(null) }

    NavHost(
        navController = navController,
        startDestination = "bleScan"
    ) {
        composable("bleScan") {
            BleScanScreen(
                navController = navController,
                onDeviceSelected = { device ->
                    selectedBleDevice = device
                    bleViewModel.connectToDevice(device)
                    navController.navigate("wifiConfiguration")
                }
            )
        }
        composable("wifiConfiguration") {
            selectedBleDevice?.let { device ->
                WifiConfigurationScreen(
                    navController = navController,
                    selectedBleDevice = device,
                    bleViewModel = bleViewModel
                )
            }
        }
        composable("connected") {
            ConnectedScreen(
                bleViewModel = bleViewModel
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
