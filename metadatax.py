#!/usr/bin/env python3
# ============================================
#   MetaDataX - Image Metadata Extractor
#   By: Almash Coder
#   For: Educational & OSINT Purposes Only
# ============================================

import os
import sys
import json
from datetime import datetime
from colorama import Fore, Style, init

try:
    from PIL import Image
    from PIL.ExifTags import TAGS, GPSTAGS
except ImportError:
    print("pip install pillow karein pehle!")
    sys.exit()

init(autoreset=True)

BANNER = f"""
{Fore.MAGENTA}
███╗   ███╗███████╗████████╗ █████╗ ██████╗  █████╗ ████████╗ █████╗ ██╗  ██╗
████╗ ████║██╔════╝╚══██╔══╝██╔══██╗██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗╚██╗██╔╝
██╔████╔██║█████╗     ██║   ███████║██║  ██║███████║   ██║   ███████║ ╚███╔╝ 
██║╚██╔╝██║██╔══╝     ██║   ██╔══██║██║  ██║██╔══██║   ██║   ██╔══██║ ██╔██╗ 
██║ ╚═╝ ██║███████╗   ██║   ██║  ██║██████╔╝██║  ██║   ██║   ██║  ██║██╔╝ ██╗
╚═╝     ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝
{Fore.YELLOW}              Image Metadata & EXIF Extractor Tool
{Fore.RED}              By Almash Coder | Educational Only
{Style.RESET_ALL}"""

def convert_gps(value):
    try:
        d = float(value[0])
        m = float(value[1])
        s = float(value[2])
        return d + (m / 60.0) + (s / 3600.0)
    except Exception:
        return None

def get_gps(gps_data):
    try:
        gps = {}
        for key, val in gps_data.items():
            name = GPSTAGS.get(key, key)
            gps[name] = val

        lat = gps.get("GPSLatitude")
        lat_ref = gps.get("GPSLatitudeRef")
        lon = gps.get("GPSLongitude")
        lon_ref = gps.get("GPSLongitudeRef")

        if lat and lon:
            lat_val = convert_gps(lat)
            lon_val = convert_gps(lon)
            if lat_val and lon_val:
                if lat_ref == "S": lat_val = -lat_val
                if lon_ref == "W": lon_val = -lon_val
                return lat_val, lon_val
    except Exception:
        pass
    return None, None

def basic_info(filepath):
    try:
        size = os.path.getsize(filepath)
        modified = datetime.fromtimestamp(os.path.getmtime(filepath))
        created = datetime.fromtimestamp(os.path.getctime(filepath))

        img = Image.open(filepath)

        print(f"\n{Fore.CYAN}{'═'*50}")
        print(f"  📁 Basic File Info")
        print(f"{'═'*50}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}  [✓] File Name   : {os.path.basename(filepath)}")
        print(f"  [✓] File Size   : {size/1024:.2f} KB")
        print(f"  [✓] Format      : {img.format}")
        print(f"  [✓] Mode        : {img.mode}")
        print(f"  [✓] Resolution  : {img.size[0]}x{img.size[1]} px")
        print(f"  [✓] Modified    : {modified.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  [✓] Created     : {created.strftime('%Y-%m-%d %H:%M:%S')}")
        print(Style.RESET_ALL)
        return img
    except Exception as e:
        print(f"{Fore.RED}[!] Error: {e}{Style.RESET_ALL}")
        return None

def exif_data(filepath):
    try:
        img = Image.open(filepath)
        exif = img._getexif()

        if not exif:
            print(f"{Fore.RED}  [!] Koi EXIF data nahi mila इस इमेज में।{Style.RESET_ALL}")
            return

        print(f"\n{Fore.CYAN}{'═'*50}")
        print(f"  📷 EXIF / Camera Info")
        print(f"{'═'*50}{Style.RESET_ALL}")

        gps_info = None
        for tag_id, value in exif.items():
            tag = TAGS.get(tag_id, tag_id)
            if tag == "GPSInfo":
                gps_info = value
                continue

            important = [
                "Make", "Model", "Software", "DateTime",
                "ExifImageWidth", "ExifImageHeight",
                "FocalLength", "Flash", "ISOSpeedRatings",
                "ExposureTime", "Orientation", "WhiteBalance",
                "LensModel"
            ]
            if tag in important:
                print(f"{Fore.GREEN}  [✓] {tag:<22}: {str(value)}{Style.RESET_ALL}")

        # Extract GPS Data safely using Pillows get_ifd context if nested
        if gps_info:
            print(f"\n{Fore.CYAN}{'═'*50}")
            print(f"  🗺️  GPS Location Info")
            print(f"{'═'*50}{Style.RESET_ALL}")
            
            # If gps_info is just an offset ID, pull dictionary via IFD
            if isinstance(gps_info, int):
                try:
                    gps_info = img.getexif().get_ifd(0x8825)
                except Exception:
                    pass
            
            if isinstance(gps_info, dict):
                lat, lon = get_gps(gps_info)
                if lat and lon:
                    print(f"{Fore.GREEN}  [✓] Latitude   : {lat:.6f}")
                    print(f"  [✓] Longitude  : {lon:.6f}")
                    print(f"\n  [🗺️] Live Maps Link:")
                    print(f"  https://www.google.com/maps?q={lat},{lon}")
                    print(Style.RESET_ALL)
                else:
                    print(f"{Fore.RED}  [!] GPS coordinates extract nahi ho sake{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}  [!] GPS data parsing block rejected.{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}  [!] GPS data nahi hai is image mein (No GPS Tags){Style.RESET_ALL}")

    except Exception as e:
        print(f"{Fore.RED}[!] EXIF Error: {e}{Style.RESET_ALL}")

def save_report(filepath):
    try:
        img = Image.open(filepath)
        exif = img._getexif()
        report = {
            "file": os.path.basename(filepath),
            "size_kb": round(os.path.getsize(filepath)/1024, 2),
            "format": img.format,
            "resolution": f"{img.size[0]}x{img.size[1]}",
            "exif": {}
        }

        if exif:
            for tag_id, value in exif.items():
                tag = TAGS.get(tag_id, tag_id)
                if tag != "GPSInfo":
                    report["exif"][tag] = str(value)

        out = "metadata_report.json"
        with open(out, "w") as f:
            json.dump(report, f, indent=4)

        print(f"{Fore.GREEN}[✓] JSON Report saved successfully as: {out}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[!] Save error: {e}{Style.RESET_ALL}")

def main():
    print(BANNER)
    while True:
        print(f"\n{Fore.CYAN}{'─'*45}")
        print(f"  1. 📁 Basic Image Info")
        print(f"  2. 📷 EXIF & Camera Data")
        print(f"  3. 🗺️  GPS Location Nikalo")
        print(f"  4. 💥 Full Scan (Sab ek saath)")
        print(f"  5. 💾 JSON Report Save Karo")
        print(f"  6. 🚪 Exit")
        print(f"{'─'*45}{Style.RESET_ALL}")

        choice = input(f"\n{Fore.YELLOW}[MetaDataX]> {Style.RESET_ALL}").strip()

        if choice in ["1","2","3","4","5"]:
            filepath = input(f"{Fore.YELLOW}Image path daalo: {Style.RESET_ALL}").strip()

            if not os.path.exists(filepath):
                print(f"{Fore.RED}[!] File nahi mili! Path check karein.{Style.RESET_ALL}")
                continue

            ext = filepath.lower().split('.')[-1]
            if ext not in ["jpg","jpeg","png","tiff","bmp","webp"]:
                print(f"{Fore.RED}[!] Sirf valid image formats support hote hain!{Style.RESET_ALL}")
                continue

            if choice == "1":   basic_info(filepath)
            elif choice == "2": exif_data(filepath)
            elif choice == "3":
                exif_data(filepath) # Exif wrapper performs safe parsing internally
            elif choice == "4":
                basic_info(filepath)
                exif_data(filepath)
            elif choice == "5": save_report(filepath)

        elif choice == "6":
            print(f"{Fore.RED}\n[!] Thanks for use Bro ! 👋{Style.RESET_ALL}")
            sys.exit()
        else:
            print(f"{Fore.RED}[!] Wrong choice!{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
