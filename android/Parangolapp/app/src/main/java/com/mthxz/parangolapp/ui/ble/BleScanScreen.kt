package com.mthxz.parangolapp.ui.ble

import android.Manifest
import android.content.pm.PackageManager
import android.os.Build
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import com.mthxz.parangolapp.data.BleDevice

@Composable
fun BleScanScreen(
    navController: NavController,
    onDeviceSelected: (BleDevice) -> Unit,
    viewModel: BleViewModel = viewModel(factory = BleViewModelFactory(LocalContext.current))
) {
    val context = LocalContext.current
    val isScanning by viewModel.isScanning.collectAsState()
    val discoveredDevices by viewModel.discoveredDevices.collectAsState()
    val errorMessage by viewModel.errorMessage.collectAsState()

    val isConnecting by viewModel.isConnecting.collectAsState()
    val connectingAddress by viewModel.connectingDeviceAddress.collectAsState()
    val connectionMessage by viewModel.connectionMessage.collectAsState()

    var hasPermissions by remember {
        mutableStateOf(
            (if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                listOf(Manifest.permission.BLUETOOTH_SCAN, Manifest.permission.BLUETOOTH_CONNECT, Manifest.permission.ACCESS_WIFI_STATE)
            } else {
                listOf(Manifest.permission.BLUETOOTH, Manifest.permission.BLUETOOTH_ADMIN, Manifest.permission.ACCESS_WIFI_STATE)
            }).all {
                ContextCompat.checkSelfPermission(context, it) == PackageManager.PERMISSION_GRANTED
            }
        )
    }

    val permissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        hasPermissions = permissions.values.all { it }
    }

    val requiredPermissions = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
        arrayOf(
            Manifest.permission.BLUETOOTH_SCAN,
            Manifest.permission.BLUETOOTH_CONNECT,
            Manifest.permission.ACCESS_WIFI_STATE
        )
    } else {
        arrayOf(
            Manifest.permission.BLUETOOTH,
            Manifest.permission.BLUETOOTH_ADMIN,
            Manifest.permission.ACCESS_WIFI_STATE
        )
    }

    LaunchedEffect(Unit) {
        permissionLauncher.launch(requiredPermissions)
    }

    // remember which device the user selected and is awaiting connection
    var pendingSelectedDevice by remember { mutableStateOf<BleDevice?>(null) }

    // react to successful connection
    LaunchedEffect(connectionMessage) {
        if (connectionMessage?.contains("CONNECTED", ignoreCase = true) == true && pendingSelectedDevice != null) {
            // proceed to next screen
            onDeviceSelected(pendingSelectedDevice!!)
            navController.navigate("wifiConfiguration")
            pendingSelectedDevice = null
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(10.dp)
    ) {
        Text(text = "Vamos conectar o Parangolé ao aplicativo", style = MaterialTheme.typography.headlineSmall)

        if (!hasPermissions) {
            Text("Habilite o Bluetooth para se conectar com o Parangolé", color = MaterialTheme.colorScheme.error, modifier = Modifier.padding(8.dp))
        } else {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceAround
            ) {
                Button(onClick = { viewModel.startScan() }, enabled = !isScanning) {
                    Text("Procurar Parangolés")
                }
                Button(onClick = { viewModel.stopScan() }, enabled = isScanning) {
                    Text("Parar procura")
                }
            }

            if (isScanning) {
                CircularProgressIndicator(modifier = Modifier.padding(vertical = 16.dp))
                Text("Procurando Parangolés...")
            }

            errorMessage?.let {
                Text(it, color = MaterialTheme.colorScheme.error, modifier = Modifier.padding(top = 8.dp))
            }

            when {
                discoveredDevices.isEmpty() && !isScanning && errorMessage == null -> {
                    Text("Nenhum parangolé encontrado ainda, inicie a procura!", modifier = Modifier.padding(top = 8.dp))
                }
                discoveredDevices.isNotEmpty() -> {
                    val visibleDevices = discoveredDevices.filter { it.name?.contains("PARANGOLE", ignoreCase = true) ?: false }
                    if (visibleDevices.isEmpty()) {
                        Text("Nenhum Parangolé encontrado", modifier = Modifier.padding(top = 8.dp))
                    } else {
                        LazyColumn(modifier = Modifier.weight(1f).fillMaxWidth()) {
                            items(visibleDevices) { device ->
                                val loadingForThis = isConnecting && connectingAddress == device.address
                                DeviceRow(device = device, isLoading = loadingForThis, onDeviceSelected = {
                                    // start connecting and remember pending device
                                    pendingSelectedDevice = device
                                    viewModel.stopScan()
                                    viewModel.connectToDevice(device)
                                })
                                HorizontalDivider()
                            }
                        }
                    }
                }
            }

            // show connection status messages
            connectionMessage?.let {
                Text(it, color = MaterialTheme.colorScheme.primary, modifier = Modifier.padding(top = 8.dp))
            }
        }
    }
}

@Composable
fun DeviceRow(device: BleDevice, isLoading: Boolean = false, onDeviceSelected: (BleDevice) -> Unit) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { if (!isLoading) onDeviceSelected(device) }
            .padding(vertical = 12.dp, horizontal = 8.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Column(modifier = Modifier.weight(1f)) {
            Text(text = device.name ?: "Unknown Device", style = MaterialTheme.typography.bodyLarge)
            Text(text = device.address, style = MaterialTheme.typography.bodySmall, modifier = Modifier.padding(top = 2.dp))
        }
        if (isLoading) {
            CircularProgressIndicator(modifier = Modifier.padding(start = 12.dp).size(20.dp))
        }
    }
}
