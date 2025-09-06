package com.mthxz.parangolapp.ui.wifi

import android.Manifest
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import com.mthxz.parangolapp.data.BleDevice
import com.mthxz.parangolapp.data.WifiNetwork
import com.mthxz.parangolapp.service.WifiScannerService
import com.mthxz.parangolapp.ui.ble.BleViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun WifiConfigurationScreen(
    navController: NavController,
    selectedBleDevice: BleDevice,
    bleViewModel: BleViewModel
) {
    var selectedWifi by remember { mutableStateOf<WifiNetwork?>(null) }
    var password by remember { mutableStateOf("") }
    var showPasswordDialog by remember { mutableStateOf(false) }
    var statusMessage by remember { mutableStateOf<String?>(null) }
    var loadingNetwork by remember { mutableStateOf<WifiNetwork?>(null) }

    val context = LocalContext.current
    val wifiScannerService = WifiScannerService(context)
    val wifiNetworks = remember { mutableStateListOf<WifiNetwork>() }

    val wifiConnected by bleViewModel.wifiConnected.collectAsState()
    val wifiFailed by bleViewModel.wifiFailed.collectAsState()
    val deviceConnected by bleViewModel.deviceConnected.collectAsState()
    val deviceIpAddress by bleViewModel.deviceIpAddress.collectAsState()

    val permissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) @androidx.annotation.RequiresPermission(android.Manifest.permission.ACCESS_FINE_LOCATION) { isGranted ->
        if (isGranted) {
            wifiScannerService.startWifiScan()
            wifiNetworks.clear()
            wifiNetworks.addAll(wifiScannerService.getAvailableNetworks())
        } else {
            statusMessage = "Location permission is required to scan for Wi-Fi networks."
        }
    }

    LaunchedEffect(Unit) {
        permissionLauncher.launch(Manifest.permission.ACCESS_FINE_LOCATION)
    }

    LaunchedEffect(wifiFailed) {
        if (wifiFailed) {
            loadingNetwork = null
            statusMessage = "Failed to connect to network"
        }
    }

    LaunchedEffect(wifiConnected, wifiFailed) {
        if (wifiFailed) {
            loadingNetwork = null
            statusMessage = "The device couldn't connect to the network"
        } else if (wifiConnected && deviceIpAddress != null) {
            // Only navigate if we have an IP address
            loadingNetwork = null
            statusMessage = "Successfully connected to network"
            navController.navigate("connected")
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        Text("Configure Wi-Fi for ${selectedBleDevice.name}", style = MaterialTheme.typography.headlineSmall)
        Text("(${selectedBleDevice.address})", style = MaterialTheme.typography.bodySmall)

        Spacer(modifier = Modifier.height(10.dp))

        Text("Select a Wi-Fi Network:", style = MaterialTheme.typography.titleMedium)

        LazyColumn(
            modifier = Modifier
                .weight(1f)
                .fillMaxWidth()
        ) {
            items(wifiNetworks) { network ->
                WifiNetworkRow(
                    network = network,
                    selected = network == selectedWifi,
                    isLoading = network == loadingNetwork
                ) {
                    selectedWifi = network
                    if (network.requiresPassword) {
                        password = ""
                        showPasswordDialog = true
                    } else {
                        password = ""
                        statusMessage = "Selected open network: ${network.ssid}"
                    }
                }
                Divider()
            }
        }

        selectedWifi?.let {
            Text("Selected Wi-Fi: ${it.ssid}", style = MaterialTheme.typography.titleSmall)
        }

        statusMessage?.let {
            Text(
                it,
                style = MaterialTheme.typography.bodyMedium,
                color = if (wifiFailed) MaterialTheme.colorScheme.error else MaterialTheme.colorScheme.primary
            )
        }

        Button(
            onClick = {
                selectedWifi?.let { wifi ->
                    bleViewModel.resetWifiStatus()
                    loadingNetwork = wifi
                    bleViewModel.sendWifiCredentials(wifi.ssid, if (wifi.requiresPassword) password else null)
                    showPasswordDialog = false
                } ?: run {
                    statusMessage = "Please select a Wi-Fi network first."
                }
            },
            modifier = Modifier.fillMaxWidth(),
            enabled = selectedWifi != null && (!selectedWifi!!.requiresPassword || password.isNotEmpty()) && loadingNetwork == null
        ) {
            Text("Send Credentials to ESP32")
        }
    }

    if (showPasswordDialog) {
        AlertDialog(
            onDismissRequest = { showPasswordDialog = false },
            title = { Text("Enter Password for ${selectedWifi?.ssid}") },
            text = {
                OutlinedTextField(
                    value = password,
                    onValueChange = { password = it },
                    label = { Text("Password") },
                    singleLine = true
                )
            },
            confirmButton = {
                TextButton(onClick = {
                    showPasswordDialog = false
                    statusMessage = "Password entered for ${selectedWifi?.ssid}"
                }) {
                    Text("OK")
                }
            },
            dismissButton = {
                TextButton(onClick = { showPasswordDialog = false }) {
                    Text("Cancel")
                }
            }
        )
    }
}

@Composable
private fun WifiNetworkRow(
    network: WifiNetwork,
    selected: Boolean,
    isLoading: Boolean,
    onClick: () -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick)
            .padding(vertical = 12.dp, horizontal = 8.dp)
            .background(if (selected) MaterialTheme.colorScheme.primaryContainer else MaterialTheme.colorScheme.surface),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(network.ssid, style = MaterialTheme.typography.bodyLarge)
        Row(
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            if (isLoading) {
                CircularProgressIndicator(
                    modifier = Modifier.size(16.dp),
                    strokeWidth = 2.dp
                )
            }
            if (!network.requiresPassword) {
                Text("(Open)", style = MaterialTheme.typography.bodySmall)
            }
        }
    }
}
