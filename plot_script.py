import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV file
df = pd.read_csv("ptp_offsets_1.csv")

# Convert timestamp column to datetime and sort
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values("timestamp")

plt.figure()

# Plot each camera offset
for cam_id in df["camera_user_id"].unique():
    cam_data = df[df["camera_user_id"] == cam_id]
    plt.plot(
        cam_data["timestamp"].values,
        cam_data["offset_from_master"].values,
        label=f"Camera {cam_id}"
    )

# Plot the two master offsets (these values are the same for all rows at a given timestamp)
plt.plot(
    df["timestamp"].values,
    df["master_offset_192.168.1.102"].values,
    label="Master offset 192.168.1.102"
)

plt.plot(
    df["timestamp"].values,
    df["master_offset_192.168.1.120"].values,
    label="Master offset 192.168.1.120"
)

plt.xlabel("Time")
plt.ylabel("Offset")
plt.title("Camera Offset and Master Offset vs Time")
plt.legend()
plt.show()
