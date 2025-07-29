
message_history = [{'timestamp': '2025-07-29 16:39:42', 'topic': 'test/web', 'payload': '{"lat":35.78584,"lon":51.49607}', 'lat': 35.78584, 'lon': 51.49607}, {'timestamp': '2025-07-29 16:39:32', 'topic': 'test/web', 'payload': '{"lat":35.77621,"lon":51.47687}', 'lat': 35.77621, 'lon': 51.47687}]

gps_data = []
# for msg in message_history:
#     if 'lat' in msg and 'lon' in msg:
#         gps_data.append((msg['lat'], msg['lon']))

current_msg = message_history[0]
if 'lat' in current_msg and 'lon' in current_msg:
    gps_data.append((current_msg['lat'], current_msg['lon']))

print(current_msg)
print(gps_data)

# print(gps_data)
