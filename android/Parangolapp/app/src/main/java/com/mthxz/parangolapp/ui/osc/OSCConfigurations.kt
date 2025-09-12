package com.mthxz.parangolapp.ui.osc

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.mthxz.parangolapp.services.OSCClient
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun OSCConfigurationsScreen(
    oscViewModel: OSCViewModel = viewModel(),
    onBack: () -> Unit = {}
) {
    val selectedService by oscViewModel.selectedService.collectAsState()
    val coroutineScope = rememberCoroutineScope()

    if (selectedService == null) {
        Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Text("No OSC service selected")
                Spacer(modifier = Modifier.height(8.dp))
                Button(onClick = onBack) { Text("Back") }
            }
        }
        return
    }

    val host = selectedService!!.ip
    val port = selectedService!!.port

    val arpStyles = listOf("up", "down", "up down", "down up", "third octaved")
    var selectedStyle by remember { mutableStateOf(arpStyles.first()) }
    var styleExpanded by remember { mutableStateOf(false) }

    var effect1 by remember { mutableStateOf(0f) }
    var effect2 by remember { mutableStateOf(0f) }

    var drumsOn by remember { mutableStateOf(false) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("OSC: ${selectedService!!.name} (${host}:${port})") }
            )
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Arpeggio Style Dropdown
            Column {
                Text("Arpeggio Style", style = MaterialTheme.typography.labelLarge)
                Box {
                    OutlinedButton(onClick = { styleExpanded = true }) {
                        Text(selectedStyle)
                    }
                    DropdownMenu(
                        expanded = styleExpanded,
                        onDismissRequest = { styleExpanded = false }
                    ) {
                        arpStyles.forEach { style ->
                            DropdownMenuItem(text = { Text(style) }, onClick = {
                                selectedStyle = style
                                styleExpanded = false
                                // send OSC message
                                coroutineScope.launch {
                                    OSCClient.sendMessage(host, port, "/arp/style", listOf(style))
                                }
                            })
                        }
                    }
                }
            }

            // Effect 1
            Column {
                Text("Effect 1", style = MaterialTheme.typography.labelLarge)
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Slider(
                        value = effect1,
                        onValueChange = {
                            effect1 = it
                            coroutineScope.launch {
                                OSCClient.sendMessage(host, port, "/instrument/effect/1", listOf(it.toInt()))
                            }
                        },
                        valueRange = 0f..127f,
                        modifier = Modifier.weight(1f)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(effect1.toInt().toString(), modifier = Modifier.width(40.dp))
                }
            }

            // Effect 2
            Column {
                Text("Effect 2", style = MaterialTheme.typography.labelLarge)
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Slider(
                        value = effect2,
                        onValueChange = {
                            effect2 = it
                            coroutineScope.launch {
                                OSCClient.sendMessage(host, port, "/instrument/effect/2", listOf(it.toInt()))
                            }
                        },
                        valueRange = 0f..127f,
                        modifier = Modifier.weight(1f)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(effect2.toInt().toString(), modifier = Modifier.width(40.dp))
                }
            }

            // Drums toggle
            Column {
                Text("Drums", style = MaterialTheme.typography.labelLarge)
                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Button(onClick = {
                        drumsOn = !drumsOn
                        val msg = if (drumsOn) "on" else "off"
                        coroutineScope.launch {
                            OSCClient.sendMessage(host, port, "/drums", listOf(msg))
                        }
                    }) {
                        Text(if (drumsOn) "Turn Drums Off" else "Turn Drums On")
                    }
                    Text(if (drumsOn) "ON" else "OFF")
                }
            }
        }
    }
}

