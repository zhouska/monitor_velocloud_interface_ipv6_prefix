import requests, ipaddress, json
from datetime import datetime

# Define your credentials and endpoint URLs
base_url = "https://<your_vco>/portal/rest"
login_url = f"{base_url}/login/enterpriseLogin"
edge_url = f"{base_url}/edge/getEdge"
edges_url = f"{base_url}/enterprise/getEnterpriseEdges"
username = "<your user>"
password = "<your password>"
prefix = "<your prefix assigned by ISP>"
edge_id = <your edge id>
interface = "<your interface>"
date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def prepare_output(state, ipv6_address=None, message=None):
    return json.dumps({
        "state": state,
        "attributes": {
            "current_ipv6_address": ipv6_address,
            "expected_prefix": prefix,
            "interface": interface,
            "last_check_time": date,
            "message": message
        }
    })

# Define the login payload
login_payload = {
    "username": username,
    "password": password
}

# Create a session to persist cookies
session = requests.Session()

# Login to get the session cookie
login_response = session.post(login_url, json=login_payload)

# Check if login was successful
if not login_response.status_code == 200:
    print(f"Login failed: {login_response.status_code}")
    print(login_response.text)
    exit()

# Define the payload to get edge details
edge_payload = {
    "id": edge_id,
    "with": ["links"]
}

# Get the edge details using the session with the cookie
edge_response = session.post(edge_url, json=edge_payload)
 
# Check if the request was successful
if edge_response.status_code == 200:
    edge_data = edge_response.json()
    
    # Iterate over the interfaces and find desired interface
    link = next((iface for iface in edge_data.get("links", []) if iface.get("interface") == interface), None)

    if link:
           ipv6_address = link.get("ipV6Address")
           if ipv6_address:
               interface_ip = ipaddress.IPv6Address(ipv6_address)
               prefix_network = ipaddress.IPv6Network(prefix)
    
               if interface_ip in prefix_network:
                   print(prepare_output("Prefix matches", ipv6_address))
               else:
                   print(prepare_output("Prefix doesn't match", ipv6_address, 
                                        f"IPv6 address found on the interface is {ipv6_address}, however, prefix should be {prefix}"))
           else:
               print(prepare_output("Error", message=f"IPv6 address not found for {interface} interface."))
    else:
        print(prepare_output("Error", message=f"{interface} interface not found."))
else:
    print(prepare_output("Error", message=f"Failed to get edge details: {edge_response.status_code}"))
