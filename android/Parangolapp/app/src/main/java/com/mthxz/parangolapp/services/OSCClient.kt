package com.mthxz.parangolapp.services

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.net.DatagramPacket
import java.net.DatagramSocket
import java.net.InetAddress
import java.nio.ByteBuffer
import java.nio.ByteOrder

object OSCClient {
    suspend fun sendMessage(host: String, port: Int, address: String, args: List<Any> = emptyList()) {
        withContext(Dispatchers.IO) {
            val data = buildOscMessage(address, args)
            DatagramSocket().use { socket ->
                val packet = DatagramPacket(data, data.size, InetAddress.getByName(host), port)
                socket.send(packet)
            }
        }
    }

    private fun pad4(len: Int): Int {
        val rem = len % 4
        return if (rem == 0) 0 else 4 - rem
    }

    private fun buildOscMessage(address: String, args: List<Any>): ByteArray {
        val addressBytes = address.toByteArray(Charsets.UTF_8)
        val addressPadding = pad4(addressBytes.size + 1)

        val typeTagsBuilder = StringBuilder()
        typeTagsBuilder.append(',')
        val argBytesList = mutableListOf<ByteArray>()

        for (arg in args) {
            when (arg) {
                is String -> {
                    typeTagsBuilder.append('s')
                    val b = arg.toByteArray(Charsets.UTF_8)
                    val pad = pad4(b.size + 1)
                    val arr = ByteArray(b.size + 1 + pad)
                    System.arraycopy(b, 0, arr, 0, b.size)
                    // null terminator is already zero
                    argBytesList.add(arr)
                }
                is Int -> {
                    typeTagsBuilder.append('i')
                    val bb = ByteBuffer.allocate(4).order(ByteOrder.BIG_ENDIAN).putInt(arg).array()
                    argBytesList.add(bb)
                }
                is Float -> {
                    typeTagsBuilder.append('f')
                    val bb = ByteBuffer.allocate(4).order(ByteOrder.BIG_ENDIAN).putFloat(arg).array()
                    argBytesList.add(bb)
                }
                else -> throw IllegalArgumentException("Unsupported OSC arg type: ${arg::class}")
            }
        }

        val typeTagBytes = typeTagsBuilder.toString().toByteArray(Charsets.UTF_8)
        val typeTagPadding = pad4(typeTagBytes.size + 1)

        // compute total size
        var total = (addressBytes.size + 1 + addressPadding) + (typeTagBytes.size + 1 + typeTagPadding)
        for (b in argBytesList) total += b.size

        val buffer = ByteBuffer.allocate(total)
        buffer.put(addressBytes)
        buffer.put(0)
        repeat(addressPadding) { buffer.put(0) }

        buffer.put(typeTagBytes)
        buffer.put(0)
        repeat(typeTagPadding) { buffer.put(0) }

        for (b in argBytesList) buffer.put(b)

        return buffer.array()
    }
}

