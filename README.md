Sunshine App Updater

This script is designed to automatically manage your Sunshine apps.json file by synchronizing it with your installed Steam games. It adds shortcuts for all games currently in your Steam library and removes any that have been uninstalled.
Prerequisites

This script requires the following Python libraries to be installed:

    vdf: For parsing Steam's VDF (Valve Data Format) files.

    requests: For making API calls to the Steam Store and SteamGridDB.

    Pillow (PIL): For handling and saving image files.

    psutil: For managing and restarting the Sunshine process.

Installation

You can install all the required libraries using pip with the following command:

pip install vdf requests Pillow psutil

Configuration

Before running the script, you must update the following paths in update_sunshine_apps.py:

    library_vdf_path: The location of your Steam libraryfolders.vdf file.

    apps_json_path: The location of your Sunshine apps.json file.

    grids_folder: The folder where you want to store the downloaded game grid images.

    STEAMGRIDDB_API_KEY: Your personal API key from SteamGridDB.

Once configured, you can run the script to automatically update your Sunshine game list.
