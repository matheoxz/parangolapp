package com.mthxz.parangolapp.service

import android.Manifest
import android.annotation.SuppressLint
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothManager
import android.bluetooth.le.ScanCallback
import android.bluetooth.le.ScanResult
import android.content.Context
import com.mthxz.parangolapp.data.BleDevice
import java.util.UUID
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import android.bluetooth.BluetoothGatt
import android.bluetooth.BluetoothGattCallback
import android.bluetooth.BluetoothGattCharacteristic
import android.bluetooth.BluetoothGattDescriptor
import android.bluetooth.BluetoothGattService
import androidx.annotation.RequiresPermission

class BleScannerService(context: Context) {

    private val bluetoothManager = context.getSystemService(Context.BLUETOOTH_SERVICE) as BluetoothManager
    private val bluetoothAdapter: BluetoothAdapter? = bluetoothManager.adapter
    private val bleScanner = bluetoothAdapter?.bluetoothLeScanner

    private val _isScanning = MutableStateFlow(false)
    val isScanning: StateFlow<Boolean> = _isScanning

    private val _discoveredDevices = MutableStateFlow<List<BleDevice>>(emptyList())
    val discoveredDevices: StateFlow<List<BleDevice>> = _discoveredDevices

    private val _errorMessage = MutableStateFlow<String?>(null)
    val errorMessage: StateFlow<String?> = _errorMessage

    private val _receivedMessage = MutableStateFlow<String?>(null)
    val receivedMessage: StateFlow<String?> = _receivedMessage

    private var bluetoothGatt: BluetoothGatt? = null

    companion object {
        private val SERVICE_UUID = UUID.fromString("eab05e32-bbf8-444c-b2a7-4311ed21d61d")
        private val CRED_CHAR_UUID = UUID.fromString("0663eb35-8ef2-4412-8981-326b53272d63")
        private val IP_CHAR_UUID   = UUID.fromString("12345678-1234-1234-1234-1234567890ad")
        private val CLIENT_CFG_UUID = UUID.fromString("00002902-0000-1000-8000-00805f9b34fb")
    }

    private val context: Context = context

    private val scanCallback = object : ScanCallback() {
        override fun onScanResult(callbackType: Int, result: ScanResult) {
            super.onScanResult(callbackType, result)
            val deviceName = result.device.name
            if (deviceName != null && deviceName.contains("PARANGOLE", ignoreCase = true)) {
                val deviceAddress = result.device.address
                val bleDevice = BleDevice(deviceName, deviceAddress)
                if (_discoveredDevices.value.none { it.address == deviceAddress }) {
                    _discoveredDevices.value = _discoveredDevices.value + bleDevice
                }
            }
        }

        override fun onBatchScanResults(results: List<ScanResult>) {
            super.onBatchScanResults(results)
            results.forEach { result ->
                val deviceName = result.device.name
                if (deviceName != null && deviceName.contains("PARANGOLE", ignoreCase = true)) {
                    val deviceAddress = result.device.address
                    val bleDevice = BleDevice(deviceName, deviceAddress)
                    if (_discoveredDevices.value.none { it.address == deviceAddress }) {
                        _discoveredDevices.value = _discoveredDevices.value + bleDevice
                    }
                }
            }
        }

        override fun onScanFailed(errorCode: Int) {
            super.onScanFailed(errorCode)
            _errorMessage.value = "BLE Scan Failed: $errorCode"
        }
    }

    @SuppressLint("MissingPermission")
    fun startScan() {
        if (bleScanner != null && !_isScanning.value) {
            _isScanning.value = true
            _discoveredDevices.value = emptyList()
            _errorMessage.value = null

            // scan all BLE devices
            bleScanner.startScan(scanCallback)
        }
    }

    @SuppressLint("MissingPermission")
    fun stopScan() {
        if (bleScanner != null && _isScanning.value) {
            _isScanning.value = false
            bleScanner.stopScan(scanCallback)
        }
    }

    @RequiresPermission(Manifest.permission.BLUETOOTH_CONNECT)
    fun connectToDevice(deviceAddress: String) {
        val device = bluetoothAdapter?.getRemoteDevice(deviceAddress)
        bluetoothGatt = device?.connectGatt(this.context, false, object : BluetoothGattCallback() {
            @RequiresPermission(Manifest.permission.BLUETOOTH_CONNECT)
            override fun onConnectionStateChange(gatt: BluetoothGatt?, status: Int, newState: Int) {
                if (newState == BluetoothGatt.STATE_CONNECTED) {
                    gatt?.discoverServices()
                }
            }

            @RequiresPermission(Manifest.permission.BLUETOOTH_CONNECT)
            override fun onServicesDiscovered(gatt: BluetoothGatt?, status: Int) {
                // Subscribe to IP notification characteristic
                val service = gatt?.getService(SERVICE_UUID)
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

            override fun onCharacteristicChanged(gatt: BluetoothGatt?, characteristic: BluetoothGattCharacteristic?) {
                val message = characteristic?.value?.toString(Charsets.UTF_8)
                _receivedMessage.value = message
            }
        })
    }

    @RequiresPermission(Manifest.permission.BLUETOOTH_CONNECT)
    fun disconnect() {
        bluetoothGatt?.close()
        bluetoothGatt = null
    }

    fun sendCredentials(ssid: String, password: String?) {
        // Write credentials as SSID;PASSWORD
        val credChar = bluetoothGatt?.getService(SERVICE_UUID)
            ?.getCharacteristic(CRED_CHAR_UUID)
        if (credChar != null) {
            val payload = if (password != null) "$ssid;$password" else "$ssid;"
            credChar.value = payload.toByteArray(Charsets.UTF_8)
            bluetoothGatt?.writeCharacteristic(credChar)
        } else {
            _errorMessage.value = "Failed to send credentials: Credential characteristic not found"
        }
    }
}
