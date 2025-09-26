import os
import json
import vdf
import requests
from PIL import Image
import io
import subprocess
import time
import psutil

# Paths
library_vdf_path = r"/home/<USER>/.local/share/Steam/steamapps/libraryfolders.vdf" #Change this to where your steam install is located
apps_json_path = r"/home/<USER>/.config/sunshine/apps.json"  # Update to your correct path
grids_folder = r"/home/<USER>/Documents/Sunshine-Steam-GridDB"  # This should be the correct path for Sunshine grids on your computer
STEAMGRIDDB_API_KEY = "<API_KEY>" #Make an account on steamgridDB, get the API key under account settings

def restart_steam():
    if os.name != 'nt':
        print("Steam restarting is not supported on this OS. Please restart Steam manually if any game is missing.")
        return
    print("Restarting Steam...")
    for proc in psutil.process_iter(['name']):
        if proc.name().lower() == 'steam.exe':
            proc.terminate()
            proc.wait()
    time.sleep(10)  # Wait for Steam to start up

def restart_sunshine():
    # --- START OF CHANGES ---
    # The original code used a hardcoded list of process names.
    # This change uses a more robust method by checking if the process name starts with 'sunshine'.
    print("Restarting Sunshine...")
    process_found = False

    # Debugging: Print all running process names to help identify the correct one.
    print("Searching for Sunshine process...")

    # Store process names to print later
    found_process_names = []
    sunshine_proc = None

    for proc in psutil.process_iter(['name']):
        name = proc.name().lower()
        found_process_names.append(name)

        # Check if the process name starts with 'sunshine'
        if name.startswith('sunshine'):
            sunshine_proc = proc
            break # Found it, so we can stop searching.

    if sunshine_proc:
        print(f"Found Sunshine process with PID {sunshine_proc.pid}. Terminating...")
        try:
            sunshine_proc.terminate()
            sunshine_proc.wait(timeout=5)  # Wait for a few seconds for the process to terminate
            process_found = True
        except psutil.NoSuchProcess:
            print("Process already terminated.")
        except psutil.TimeoutExpired:
            print("Timeout expired, forcing kill.")
            sunshine_proc.kill()

    if not process_found:
        print("Sunshine process not found. No restart performed.")
        # Print the list of process names for debugging
        print("\n--- Processes Found ---")
        for name in sorted(list(set(found_process_names))):
            print(name)
        print("-----------------------\n")
        print("If 'sunshine' is running, its process name may be different. "
              "Check the list above and update the `if` statement if needed.")
    else:
        # Give the system a moment to clean up before attempting to restart the process
        time.sleep(2)
        print("Attempting to restart Sunshine (detached)...")
        try:
            # --- MODIFICATION FOR DETACHED RESTART ---
            # Using 'nohup' and a double ampersand '&&' or simply 'sunshine &'
            # can be tricky with Popen's list-based command.
            # The most reliable Popen method for a clean daemon/background
            # start on Linux is to use 'start_new_session=True'
            # and redirect stdout/stderr to /dev/null to avoid blocking.
            # However, for a user-space application like Sunshine that may rely
            # on the terminal for some output, a more common method is:
            #
            # The simple `subprocess.Popen(['sunshine'])` already makes it
            # asynchronous (non-blocking) in Python. The reason the output
            # shows up in your terminal is because the child process (Sunshine)
            # is inheriting the parent's standard streams (stdout/stderr).
            #
            # To completely detach the new process and prevent its output from
            # cluttering the main script's terminal, we can redirect its I/O.

            # Redirect I/O to /dev/null and start in a new session
            # This is a common pattern for fully detaching a process/daemon on Linux.
            DEVNULL = open(os.devnull, 'w')
            subprocess.Popen(['sunshine'],
                             stdout=DEVNULL,
                             stderr=DEVNULL,
                             start_new_session=True)
            DEVNULL.close() # Close the file handle in the main script

            print("Sunshine restarted successfully and is running in the background.")
        except FileNotFoundError:
            print("Could not find the 'sunshine' executable. Please start it manually.")
        except Exception as e:
            print(f"An error occurred while trying to restart Sunshine: {e}")
    # --- END OF CHANGES ---

def get_game_name(app_id):
    try:
        url = f"https://store.steampowered.com/api/appdetails?appids={app_id}"
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        if data and str(app_id) in data and data[str(app_id)]['success']:
            return data[str(app_id)]['data']['name']
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching name for AppID {app_id} (network/HTTP error): {e}")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON for AppID {app_id}. Response content: {response.text}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred fetching name for AppID {app_id}: {e}")
        return None

def fetch_grid_from_steamgriddb(app_id):
    try:
        url = f"https://www.steamgriddb.com/api/v2/grids/steam/{app_id}"
        headers = {"Authorization": f"Bearer {STEAMGRIDDB_API_KEY}"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        if "data" in data and len(data["data"]) > 0:
            grid_url = data["data"][0]["url"]
            grid_response = requests.get(grid_url)
            grid_response.raise_for_status()
            image = Image.open(io.BytesIO(grid_response.content))
            grid_path = os.path.join(grids_folder, f"{app_id}.png")
            image.save(grid_path, "PNG")
            return grid_path
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching grid for AppID {app_id} (network/HTTP error): {e}")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON for AppID {app_id}. Response content: {response.text}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred fetching grid for AppID {app_id}: {e}")
        return None

def get_sunshine_config(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as file:
            config = json.load(file)
        print(f"Loaded Sunshine config with {len(config.get('apps', []))} apps")
    else:
        config = {"env": "", "apps": []}
        print("Sunshine config not found, initializing empty config")
    return config

def save_sunshine_config(path, config):
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(config, file, indent=4)
    print(f"Saved Sunshine config with {len(config.get('apps', []))} apps")

# --- Main Script ---

# Restart Steam before processing
restart_steam()

print(f"Loading Steam library from {library_vdf_path}")
try:
    with open(library_vdf_path, 'r', encoding='utf-8') as file:
        steam_data = vdf.load(file)
except FileNotFoundError:
    print(f"Error: Steam library VDF file not found at {library_vdf_path}")
    exit()
except Exception as e:
    print(f"Error loading Steam library VDF: {e}")
    exit()

installed_games = {}
for folder_data in steam_data.get('libraryfolders', {}).values():
    if "apps" in folder_data:
        for app_id, app_info in folder_data["apps"].items():
            game_name = get_game_name(app_id)
            if game_name:
                installed_games[app_id] = game_name

print(f"Found {len(installed_games)} installed games")
print("Installed games:", installed_games)

sunshine_config = get_sunshine_config(apps_json_path)

os.makedirs(grids_folder, exist_ok=True)

# Preserve specific apps
preserved_apps = []
apps_to_delete_grids = []

for app in sunshine_config.get('apps', []):
    if app.get('name') in ["Desktop", "Steam Big Picture"]:
        preserved_apps.append(app)
    elif 'cmd' in app and app['cmd'].startswith('steam://rungameid/'):
        # This is a Steam game shortcut, mark its grid for deletion if it exists
        grid_path = app.get('image-path')
        if grid_path and os.path.exists(grid_path):
            apps_to_delete_grids.append(grid_path)

print(f"Preserving {len(preserved_apps)} apps: {[app['name'] for app in preserved_apps]}")
print(f"Grids to delete for removed Steam shortcuts: {apps_to_delete_grids}")

# Delete grid images for removed Steam shortcuts
for grid_path in apps_to_delete_grids:
    try:
        os.remove(grid_path)
    except OSError as e:
        print(f"Error deleting grid image {grid_path}: {e}")

# Clear all existing apps from Sunshine config, except the preserved ones
sunshine_config['apps'] = preserved_apps
print("Removed all Steam game shortcuts from Sunshine config.")

# Now add all currently installed Steam games
newly_added_count = 0
for app_id, game_name in installed_games.items():
    grid_path = fetch_grid_from_steamgriddb(app_id)
    cmd = f"steam://rungameid/{app_id}" if os.name == 'nt' else f"steam steam://rungameid/{app_id}"
    new_app = {
        "name": game_name,
        "cmd": cmd,
        "output": "",
        "detached": "",
        "elevated": "false",
        "hidden": "true",
        "wait-all": "true",
        "exit-timeout": "5",
        "image-path": grid_path or ""
    }
    sunshine_config['apps'].append(new_app)
    newly_added_count += 1
    print(f"Adding shortcut for: {game_name}")

print(f"Added {newly_added_count} new Steam game shortcuts to Sunshine config.")

save_sunshine_config(apps_json_path, sunshine_config)
print("Sunshine apps.json update process completed")

# Restart Sunshine after processing
restart_sunshine()

