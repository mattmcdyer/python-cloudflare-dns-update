import requests
import json

with open("configFile.json", "r") as configFile:
    config = json.load(configFile)
    CLOUDFLARE_API_TOKEN = config["CLOUDFLARE_API_TOKEN"]
    CLOUDFLARE_API_BASE_URL = config["CLOUDFLARE_API_BASE_URL"]

def getUpdatedIP():
    try:
        response = requests.get("https://api.ipify.org")
        response.raise_for_status()
        return response.text.strip()
    except requests.RequestException as e:
        print(f"Error fetching updated IP: {e}")
        return None
    
def getZoneID():
    zoneIDs = []
    url = f"{CLOUDFLARE_API_BASE_URL}/zones"
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        zones = response.json().get("result", [])
        for zone in zones:
            zoneIDs.append(zone['id'])
            print(f"Domain: {zone['name']}, Zone ID: {zone['id']}")
        return zoneIDs
    except requests.RequestException as e:
        return(f"Error fetching zones: {e}")

def fetchDNSRecords(zoneID):
    url = f"{CLOUDFLARE_API_BASE_URL}/zones/{zoneID}/DNSRecords"
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get("result", [])
    except requests.RequestException as e:
        print(f"Error fetching DNS records for zone {zoneID}: {e}")
        return []

def updateDNSRecord(zoneID, recordID, data):
    url = f"{CLOUDFLARE_API_BASE_URL}/zones/{zoneID}/DNSRecords/{recordID}"
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.put(url, headers=headers, json=data)
        response.raise_for_status()
        print(f"Successfully updated DNS record")
    except requests.RequestException as e:
        print(f"Error updating DNS record: {e}")

def main():

    for zoneID in getZoneID():
        print(f"Processing zone: {zoneID}")

        updatedIP = getUpdatedIP()
        if not updatedIP:
            print("Failed to fetch updated IP. Exiting.")
            return

        DNSRecords = fetchDNSRecords(zoneID)
        if not DNSRecords:
            print("No DNS records found. Exiting.")
            return

        recordsToUpdate = []

        for record in DNSRecords:
            if record["comment"] is not None:
                if "HH" in record["comment"]:
                    print(f'Updating {record["name"]} with comment "{record["comment"]}" to IP {updatedIP}')
                    recordsToUpdate.append(record)

        for record in recordsToUpdate:
            record["content"] = updatedIP
            updateDNSRecord(zoneID, record["id"], record)

if __name__ == "__main__":
    main()