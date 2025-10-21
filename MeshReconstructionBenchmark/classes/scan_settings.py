"""this settings are used to MVS scanning and the keys of the settings are used for lidar scanning
"""
scan_settings = dict()

scan_settings["0"] = dict()
scan_settings["0"]["points"] = "100000"
scan_settings["0"]["noise"] = "0"
scan_settings["0"]["outliers"] = "0"
scan_settings["0"]["cameras"] = "10"

scan_settings["1"] = dict()
scan_settings["1"]["points"] = "10000"
scan_settings["1"]["noise"] = "0.005"
scan_settings["1"]["outliers"] = "0.01"
scan_settings["1"]["cameras"] = "10"

scan_settings["2"] = dict()
scan_settings["2"]["points"] = "100000"
scan_settings["2"]["noise"] = "0.005"
scan_settings["2"]["outliers"] = "0.01"
scan_settings["2"]["cameras"] = "10"