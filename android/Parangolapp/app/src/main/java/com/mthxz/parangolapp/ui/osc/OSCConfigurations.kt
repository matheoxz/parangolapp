package com.mthxz.parangolapp.ui.osc

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.mthxz.parangolapp.services.OSCClient
import kotlinx.coroutines.launch
import kotlin.math.roundToInt

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

    // Effects as a dynamic list (initially 2)
    val effects = remember { mutableStateListOf(0f, 0f) }

    var drumsOn by remember { mutableStateOf(false) }

    // Note length options (strings kept as sent value)
    val noteOptions = listOf("1/32", "1/16", "1/12", "1/8", "1/6", "1/4", "1/2", "1", "1.5", "2")
    var noteIndex by remember { mutableStateOf(6f) } // default index e.g. 1/2

    // BPM
    var bpm by remember { mutableStateOf(120f) }

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

            // Effects header with add button
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween,
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("Effects", style = MaterialTheme.typography.titleMedium)
                IconButton(onClick = {
                    effects.add(0f)
                }) {
                    Icon(Icons.Filled.Add, contentDescription = "Add Effect")
                }
            }

            // Dynamic effect sliders
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                effects.forEachIndexed { idx, value ->
                    val effectIndex = idx + 1 // 1-based
                    var sliderValue by remember { mutableStateOf(value) }
                    Column {
                        Text("Effect $effectIndex", style = MaterialTheme.typography.labelLarge)
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Slider(
                                value = sliderValue,
                                onValueChange = {
                                    sliderValue = it
                                    effects[idx] = it
                                    // send /slider with two params: {effect_idx}, {value}
                                    coroutineScope.launch {
                                        OSCClient.sendMessage(host, port, "/slider", listOf(effectIndex, it.toInt()))
                                    }
                                },
                                valueRange = 0f..127f,
                                modifier = Modifier.weight(1f)
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(sliderValue.toInt().toString(), modifier = Modifier.width(40.dp))
                        }
                    }
                }
            }

            // Note Length (discrete slider mapped to options)
            Column {
                Text("Note Length", style = MaterialTheme.typography.labelLarge)
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Slider(
                        value = noteIndex,
                        onValueChange = { v ->
                            // snap to nearest index
                            val idx = v.roundToInt().coerceIn(0, noteOptions.lastIndex)
                            noteIndex = idx.toFloat()
                            val selected = noteOptions[idx]
                            coroutineScope.launch {
                                OSCClient.sendMessage(host, port, "/note/length", listOf(selected))
                            }
                        },
                        valueRange = 0f..(noteOptions.size - 1).toFloat(),
                        steps = (noteOptions.size - 2).coerceAtLeast(0),
                        modifier = Modifier.weight(1f)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(noteOptions[noteIndex.roundToInt()])
                }
            }

            // BPM slider
            Column {
                Text("BPM", style = MaterialTheme.typography.labelLarge)
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Slider(
                        value = bpm,
                        onValueChange = {
                            bpm = it
                            coroutineScope.launch {
                                OSCClient.sendMessage(host, port, "/bpm", listOf(it.toInt()))
                            }
                        },
                        valueRange = 60f..180f,
                        modifier = Modifier.weight(1f)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(bpm.toInt().toString(), modifier = Modifier.width(48.dp))
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
