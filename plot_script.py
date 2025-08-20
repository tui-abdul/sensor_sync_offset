import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV
df = pd.read_csv("ptp_offsets_1.csv")

# Convert the "timestamp" column to datetime
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Sort by timestamp
df = df.sort_values("timestamp")

plt.figure()

# Loop through each camera_id
for cam_id in df['camera_user_id'].unique():
    cam_data = df[df['camera_user_id'] == cam_id]
    # Use .values to make sure we pass 1-D arrays to matplotlib
    plt.plot(
        cam_data['timestamp'].values, 
        cam_data['offset_from_master'].values,
        label=f"Camera {cam_id}"
    )

plt.xlabel("Time")
plt.ylabel("Offset From Master")
plt.title("Camera Offset vs Time")

plt.legend()
plt.show()
