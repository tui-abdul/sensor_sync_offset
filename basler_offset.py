from pypylon import pylon
import csv
import time
from datetime import datetime, timedelta
import requests

def open_cameras(user_ids):
    """Open all cameras once and return a dictionary {user_id: InstantCamera}."""
    tl_factory = pylon.TlFactory.GetInstance()
    devices = tl_factory.EnumerateDevices()
    cams = {}
    for dev in devices:
        cam = pylon.InstantCamera(tl_factory.CreateDevice(dev))
        cam.Open()
        uid = cam.GetNodeMap().GetNode("DeviceUserID").GetValue()
        if str(uid) in user_ids:
            cams[str(uid)] = cam
        else:
            cam.Close()
    return cams

def get_master_offset(ip_address):
    url = f"http://{ip_address}/api/v1/time/ptp"
    r = requests.get(url, timeout=5)
    r.raise_for_status()
    return r.json()["time_status_np"]["master_offset"]

def collect_ptp_offsets(user_ids, master_ips, interval_seconds=2, duration_minutes=2, csv_filename="ptp_offsets.csv"):
    # --- open all needed cameras once
    cameras = open_cameras(user_ids)

    end_time = datetime.now() + timedelta(minutes=duration_minutes)

    with open(csv_filename, mode='w', newline='') as f:
        writer = csv.writer(f)
        header = ['timestamp', 'camera_user_id', 'offset_from_master']
        for ip in master_ips:
            header.append(f"master_offset_{ip}")
        writer.writerow(header)

        while datetime.now() < end_time:
            # get master offsets (from both IPs)
            master_offsets = {}
            for ip in master_ips:
                try:
                    master_offsets[ip] = get_master_offset(ip)
                except Exception as e:
                    print(f"Error getting master offset from {ip}: {e}")
                    master_offsets[ip] = None

            # read offsets from each already opened camera
            for uid, cam in cameras.items():
                try:
                    cam.PtpDataSetLatch.Execute()
                    cam_offset = cam.PtpOffsetFromMaster.GetValue()

                    row = [datetime.now().isoformat(), uid, cam_offset]
                    for ip in master_ips:
                        row.append(master_offsets[ip])
                    writer.writerow(row)

                    print(f"[{datetime.now().isoformat()}] Cam {uid} Offset={cam_offset}, "
                          + ", ".join([f"{ip}={master_offsets[ip]}" for ip in master_ips]))

                except Exception as e:
                    print(f"Error reading camera {uid}: {e}")

            time.sleep(interval_seconds)

    # --- close the cameras when finished
    for cam in cameras.values():
        cam.Close()

if __name__ == "__main__":
    camera_ids = ["103", "104", "121", "122"]
    master_ips = ["192.168.1.102", "192.168.1.120"]
    collect_ptp_offsets(camera_ids, master_ips, interval_seconds=2, duration_minutes=4, csv_filename="ptp_offsets_1.csv")
