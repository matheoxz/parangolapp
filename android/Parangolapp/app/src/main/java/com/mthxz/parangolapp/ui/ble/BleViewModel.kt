package com.mthxz.parangolapp.ui.ble

import android.annotation.SuppressLint
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothDevice
import android.bluetooth.BluetoothGatt
import android.bluetooth.BluetoothGattCallback
import android.bluetooth.BluetoothGattCharacteristic
import android.bluetooth.BluetoothGattDescriptor
import android.bluetooth.BluetoothManager
import android.bluetooth.BluetoothProfile
import android.bluetooth.le.ScanCallback
import android.bluetooth.le.ScanResult
import android.content.Context
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.mthxz.parangolapp.data.BleDevice
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.withTimeoutOrNull
import java.util.UUID

@SuppressLint("MissingPermission")
class BleViewModel(context: Context) : ViewModel() {
    companion object {
        private val SERVICE_UUID = UUID.fromString("eab05e32-bbf8-444c-b2a7-4311ed21d61d")
        private val CRED_CHAR_UUID = UUID.fromString("0663eb35-8ef2-4412-8981-326b53272d63")
        private val IP_CHAR_UUID = UUID.fromString("12345678-1234-1234-1234-1234567890ad")
        private val CLIENT_CFG_UUID = UUID.fromString("00002902-0000-1000-8000-00805f9b34fb")
    }

    // Use the application context to avoid leaking an Activity context
    private val appContext: Context = context.applicationContext

    private val bluetoothManager = appContext.getSystemService(Context.BLUETOOTH_SERVICE) as BluetoothManager
    private val bluetoothAdapter: BluetoothAdapter? = bluetoothManager.adapter
    private val bleScanner = bluetoothAdapter?.bluetoothLeScanner

    private val _isScanning = MutableStateFlow(false)
    val isScanning = _isScanning.asStateFlow()

    private val _discoveredDevices = MutableStateFlow<List<BleDevice>>(emptyList())
    val discoveredDevices = _discoveredDevices.asStateFlow()

    private val _errorMessage = MutableStateFlow<String?>(null)
    val errorMessage = _errorMessage.asStateFlow()

    // Connection related state
    private val _isConnecting = MutableStateFlow(false)
    val isConnecting = _isConnecting.asStateFlow()

    private val _connectingDeviceAddress = MutableStateFlow<String?>(null)
    val connectingDeviceAddress = _connectingDeviceAddress.asStateFlow()

    private val _connectionMessage = MutableStateFlow<String?>(null)
    val connectionMessage = _connectionMessage.asStateFlow()

    private val _wifiConnected = MutableStateFlow(false)
    val wifiConnected = _wifiConnected.asStateFlow()

    private val _wifiFailed = MutableStateFlow(false)
    val wifiFailed = _wifiFailed.asStateFlow()

    private val _deviceConnected = MutableStateFlow(false)
    val deviceConnected = _deviceConnected.asStateFlow()

    private val _deviceIpAddress = MutableStateFlow<String?>(null)
    val deviceIpAddress = _deviceIpAddress.asStateFlow()

    private var bluetoothGatt: BluetoothGatt? = null
    private var receivedConnected = false

    private val scanCallback = object : ScanCallback() {
        override fun onScanResult(callbackType: Int, result: ScanResult) {
            super.onScanResult(callbackType, result)
            val deviceName = result.device.name
            val deviceAddress = result.device.address
            val bleDevice = BleDevice(deviceName ?: "", deviceAddress)
            if (_discoveredDevices.value.none { it.address == deviceAddress }) {
                _discoveredDevices.value = _discoveredDevices.value + bleDevice
            }
        }

        override fun onBatchScanResults(results: List<ScanResult>) {
            super.onBatchScanResults(results)
            results.forEach { result ->
                val deviceName = result.device.name
                val deviceAddress = result.device.address
                val bleDevice = BleDevice(deviceName ?: "", deviceAddress)
                if (_discoveredDevices.value.none { it.address == deviceAddress }) {
                    _discoveredDevices.value = _discoveredDevices.value + bleDevice
                }
            }
        }

        override fun onScanFailed(errorCode: Int) {
            super.onScanFailed(errorCode)
            _errorMessage.value = "BLE Scan Failed: $errorCode"
            _isScanning.value = false
        }
    }

    fun startScan() {
        if (bluetoothAdapter == null || !bluetoothAdapter.isEnabled) {
            _errorMessage.value = "Bluetooth is not enabled."
            return
        }
        if (_isScanning.value) return

        _discoveredDevices.value = emptyList()
        _errorMessage.value = null
        _isScanning.value = true
        bleScanner?.startScan(scanCallback)

        viewModelScope.launch {
            kotlinx.coroutines.delay(5000) // Stop scan after 10 seconds
            if (_isScanning.value) {
                stopScan()
            }
        }
    }

    fun stopScan() {
        if (!_isScanning.value) return
        _isScanning.value = false
        bleScanner?.stopScan(scanCallback)
    }

    private val gattCallback = object : BluetoothGattCallback() {
        override fun onConnectionStateChange(gatt: BluetoothGatt, status: Int, newState: Int) {
            super.onConnectionStateChange(gatt, status, newState)
            when {
                status != BluetoothGatt.GATT_SUCCESS -> {
                    viewModelScope.launch {
                        _errorMessage.value = "Error in connection: $status"
                        _connectionMessage.value = "FAILED"
                        _isConnecting.value = false
                        _connectingDeviceAddress.value = null
                    }
                    bluetoothGatt?.close()
                    bluetoothGatt = null
                    return
                }
                newState == BluetoothProfile.STATE_CONNECTED -> {
                    viewModelScope.launch {
                        _connectionMessage.value = "CONNECTED"
                        _isConnecting.value = false
                        _connectingDeviceAddress.value = null
                        receivedConnected = true
                    }
                    // Enable notifications for characteristics
                    gatt.discoverServices()
                }
                newState == BluetoothProfile.STATE_DISCONNECTED -> {
                    viewModelScope.launch {
                        _connectionMessage.value = "DISCONNECTED"
                        _isConnecting.value = false
                        _connectingDeviceAddress.value = null
                    }
                    bluetoothGatt?.close()
                    bluetoothGatt = null
                }
            }
        }

        override fun onServicesDiscovered(gatt: BluetoothGatt, status: Int) {
            if (status == BluetoothGatt.GATT_SUCCESS) {
                val service = gatt.getService(SERVICE_UUID)
                val characteristic = service?.getCharacteristic(CRED_CHAR_UUID)
                characteristic?.let { char ->
                    // Enable notifications and set the correct properties
                    gatt.setCharacteristicNotification(char, true)
                    // Write type should be WRITE_TYPE_DEFAULT for reliable writes
                    char.writeType = BluetoothGattCharacteristic.WRITE_TYPE_DEFAULT
                }

                // Subscribe to IP notification characteristic
                val ipChar = service?.getCharacteristic(IP_CHAR_UUID)
                if (ipChar != null) {
                    gatt.setCharacteristicNotification(ipChar, true)
                    // Enable descriptor for notifications
                    val descriptor = ipChar.getDescriptor(CLIENT_CFG_UUID)
                    descriptor?.let {
                        it.value = BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE
                        gatt.writeDescriptor(it)
                    }
                }
            }
        }

        override fun onCharacteristicChanged(
            gatt: BluetoothGatt,
            characteristic: BluetoothGattCharacteristic
        ) {
            if (characteristic.uuid == IP_CHAR_UUID) {
                handleCharacteristicValue(characteristic.value)
            }
        }

        override fun onCharacteristicWrite(
            gatt: BluetoothGatt,
            characteristic: BluetoothGattCharacteristic,
            status: Int
        ) {
            if (characteristic.uuid == CRED_CHAR_UUID) {
                if (status != BluetoothGatt.GATT_SUCCESS) {
                    viewModelScope.launch {
                        _errorMessage.value = "Failed to write Wi-Fi credentials"
                        _wifiFailed.value = true
                    }
                } else {
                    viewModelScope.launch {
                        _errorMessage.value = null
                    }
                }
            }
        }
    }

    private fun handleCharacteristicValue(value: ByteArray?) {
        if (value == null) return
        val s = try { String(value) } catch (_: Exception) { null }
        if (s != null) {
            when {
                s.contains("CONNECTED", ignoreCase = true) -> {
                    receivedConnected = true
                    viewModelScope.launch {
                        _connectionMessage.value = "CONNECTED"
                        _isConnecting.value = false
                        _connectingDeviceAddress.value = null
                    }
                }
                s.contains("FAIL", ignoreCase = true) -> {
                    viewModelScope.launch {
                        _wifiFailed.value = true
                        _wifiConnected.value = false
                        _deviceIpAddress.value = null
                    }
                }
                s.startsWith("IP:", ignoreCase = true).and(!s.contains("FAIL")) -> {
                    val ip = s.substringAfter("IP:").trim()
                    viewModelScope.launch {
                        _deviceConnected.value = true
                        _wifiConnected.value = true
                        _wifiFailed.value = false
                        _deviceIpAddress.value = ip
                    }
                }
            }
        }
    }

    fun connectToDevice(device: BleDevice) {
        if (_isConnecting.value) return
        val address = device.address
        val remote: BluetoothDevice? = try {
            bluetoothAdapter?.getRemoteDevice(address)
        } catch (_: IllegalArgumentException) {
            null
        }
        if (remote == null) {
            _errorMessage.value = "Cannot find device: $address"
            return
        }

        _isConnecting.value = true
        _connectingDeviceAddress.value = address
        _connectionMessage.value = null
        receivedConnected = false

        bluetoothGatt = remote.connectGatt(appContext, false, gattCallback)

        // Wait up to 10 seconds for the "CONNECTED" message
        viewModelScope.launch {
            val ok = withTimeoutOrNull(10_000) {
                while (!receivedConnected) {
                    kotlinx.coroutines.delay(100)
                }
                true
            }
            if (ok != true) {
                _isConnecting.value = false
                _connectingDeviceAddress.value = null
                try {
                    bluetoothGatt?.disconnect()
                    bluetoothGatt?.close()
                } catch (_: Exception) {
                }
                bluetoothGatt = null
            }
        }
    }

    fun sendWifiCredentials(ssid: String, password: String?) {
        _wifiConnected.value = false
        _wifiFailed.value = false
        _deviceIpAddress.value = null

        bluetoothGatt?.let { gatt ->
            val service = gatt.getService(SERVICE_UUID)
            val characteristic = service?.getCharacteristic(CRED_CHAR_UUID)

            characteristic?.let { char ->
                val message = if (password != null) {
                    "$ssid;$password"
                } else {
                    "$ssid;"
                }

                char.setValue(message.toByteArray(Charsets.UTF_8))

                if (!gatt.writeCharacteristic(char)) {
                    viewModelScope.launch {
                        _errorMessage.value = "Failed to write to characteristic"
                        _wifiFailed.value = true
                    }
                }
            } ?: run {
                viewModelScope.launch {
                    _errorMessage.value = "Wi-Fi characteristic not found"
                    _wifiFailed.value = true
                }
            }
        } ?: run {
            viewModelScope.launch {
                _errorMessage.value = "Not connected to device"
                _wifiFailed.value = true
            }
        }
    }

    fun resetWifiStatus() {
        _wifiFailed.value = false
        _wifiConnected.value = false
    }

    fun disconnect() {
        try {
            bluetoothGatt?.disconnect()
            bluetoothGatt?.close()
        } catch (_: Exception) {
            // Ignore exceptions during disconnect
        }
        bluetoothGatt = null
        _isConnecting.value = false
        _connectingDeviceAddress.value = null
        _connectionMessage.value = null
    }
}
