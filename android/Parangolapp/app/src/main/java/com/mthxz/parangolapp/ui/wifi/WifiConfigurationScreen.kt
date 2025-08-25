package com.mthxz.parangolapp.ui.wifi

import android.Manifest
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.Divider
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import com.mthxz.parangolapp.data.BleDevice
import com.mthxz.parangolapp.data.WifiNetwork
import com.mthxz.parangolapp.service.WifiScannerService

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun WifiConfigurationScreen(
    navController: NavController,
    selectedBleDevice: BleDevice,
    onSendCredentials: (String, String?) -> Unit,
) {
    var selectedWifi by remember { mutableStateOf<WifiNetwork?>(null) }
    var password by remember { mutableStateOf("") }
    var showPasswordDialog by remember { mutableStateOf(false) }
    var statusMessage by remember { mutableStateOf<String?>(null) }

    val context = LocalContext.current
    val wifiScannerService = WifiScannerService(context)
    val wifiNetworks = remember { mutableStateListOf<WifiNetwork>() }

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

        LazyColumn(modifier = Modifier.weight(1f).fillMaxWidth()) {
            items(wifiNetworks) { network ->
                WifiNetworkRow(network = network, selected = network == selectedWifi) {
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
            Text(it, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.primary)
        }

        Button(
            onClick = {
                if (selectedWifi != null) {
                    onSendCredentials(selectedWifi!!.ssid, if (selectedWifi!!.requiresPassword) password else null)
                    navController.navigate("ipScreen")
                } else {
                    statusMessage = "Please select a Wi-Fi network first."
                }
            },
            enabled = selectedWifi != null,
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("Send Credentials to ESP32")
        }
    }

    if (showPasswordDialog && selectedWifi != null && selectedWifi!!.requiresPassword) {
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
                Button(onClick = {
                    showPasswordDialog = false
                    statusMessage = "Password entered for ${selectedWifi?.ssid}"
                }) {
                    Text("OK")
                }
            },
            dismissButton = {
                Button(onClick = { showPasswordDialog = false }) {
                    Text("Cancel")
                }
            }
        )
    }
}

@Composable
fun WifiNetworkRow(network: WifiNetwork, selected: Boolean, onClick: () -> Unit) {
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
        if (!network.requiresPassword) {
            Text("(Open)", style = MaterialTheme.typography.bodySmall)
        }
    }
}
