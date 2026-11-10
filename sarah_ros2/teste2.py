negative_number = -1000
# Must include signed=True
byte_data = negative_number.to_bytes(2, byteorder='little', signed=True)

print(byte_data[0])  # Output: b'\x18\xfc'