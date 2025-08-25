package com.mthxz.parangolapp.ui.ip

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.mthxz.parangolapp.service.BleScannerService

@Composable
fun IPScreen(
    bleScannerService: BleScannerService,
    onRetry: () -> Unit
) {
    val receivedMessage by bleScannerService.receivedMessage.collectAsState()

    LaunchedEffect(Unit) {
        // Assuming the BLE device is already connected
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        if (receivedMessage != null) {
            Text("Device IP Address:", style = MaterialTheme.typography.titleMedium)
            Spacer(modifier = Modifier.height(8.dp))
            Text(receivedMessage!!, style = MaterialTheme.typography.headlineSmall)
        } else {
            CircularProgressIndicator()
            Spacer(modifier = Modifier.height(16.dp))
            Text("Waiting for device response...", style = MaterialTheme.typography.bodyMedium)
        }
    }
}