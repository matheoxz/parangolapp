package com.mthxz.parangolapp.ui.osc

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.mthxz.parangolapp.services.OSCService
import com.mthxz.parangolapp.ui.ble.BleViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun OSCServicesSearchScreen(
    oscViewModel: OSCViewModel = viewModel(),
    bleViewModel: BleViewModel,
    onNavigateToConnected: () -> Unit
) {
    val discoveredServices by oscViewModel.discoveredServices.collectAsState()
    val selectedService by oscViewModel.selectedService.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("OSC Services") },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer
                )
            )
        },
        bottomBar = {
            BottomAppBar {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    horizontalArrangement = Arrangement.Center
                ) {
                    Button(
                        onClick = {
                            selectedService?.let { service ->
                                // Send the IP to BLE device
                                bleViewModel.sendOscIpToBleDevice(service.ip, service.port)
                                onNavigateToConnected()
                            }
                        },
                        enabled = selectedService != null
                    ) {
                        Text("Connect to Selected Service")
                    }
                }
            }
        }
    ) { paddingValues ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            if (discoveredServices.isEmpty()) {
                CircularProgressIndicator(
                    modifier = Modifier.align(Alignment.Center)
                )
            } else {
                LazyColumn(
                    modifier = Modifier.fillMaxSize(),
                    contentPadding = PaddingValues(16.dp)
                ) {
                    items(discoveredServices) { service ->
                        OSCServiceItem(
                            service = service,
                            isSelected = service == selectedService,
                            onSelect = { oscViewModel.selectService(service) }
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun OSCServiceItem(
    service: OSCService,
    isSelected: Boolean,
    onSelect: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp)
            .clickable(onClick = onSelect),
        colors = CardDefaults.cardColors(
            containerColor = if (isSelected)
                MaterialTheme.colorScheme.primaryContainer
            else
                MaterialTheme.colorScheme.surface
        )
    ) {
        Column(
            modifier = Modifier
                .padding(16.dp)
                .fillMaxWidth()
        ) {
            Text(
                text = service.name,
                style = MaterialTheme.typography.titleMedium,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = "IP: ${service.ip}",
                style = MaterialTheme.typography.bodyMedium
            )
            Text(
                text = "Port: ${service.port}",
                style = MaterialTheme.typography.bodyMedium
            )
        }
    }
}
