# MTA ARRIVAL TIME CLOCK
Show arrival trains for stations you want.

## DEMO Python Script
`mta_arrival_demo.py` is a small Python demo script that prints live NYC subway arrival times in the terminal.
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install requests gtfs-realtime-bindings
python mta_arrival_demo.py
```
To keep it refreshing:
```bash
python mta_arrival_demo.py --refresh 30
```
Expected output looks like:
```
Updated 11:38:59 AM EDT

36 St Uptown
  R - 3 min
  N - 6 min

36 St Downtown
  R - 2 min
  D - 7 min

145 St Uptown
  D - 5 min
  D - 22 min

145 St Downtown
  D - 2 min
  D - 20 min
```
### Configure Stations and Routes and number of Arrivals
Change values of these variables in python script:
- `ROUTES_TO_SHOW`: train lines you want to see
- `STOPS`: stops you want to see. Use format `"station_name": "stop_id"`, **stop id** are find from file [stops.txt](gtfs_subway/stops.txt), and include **N (Uptown)** or **S (Downtown)** in the end.
- `ARRIVALS_PER_STATION`: number of upcoming arrivals to shown for stations

## COMPONENTS
- Orange Pi Zero 2W 1G
- Hosyond 3.5 inch ESP32 Display

# USEFUL LINKS
- [Orange Pi Zero 2W Offcial Site](http://www.orangepi.org/html/hardWare/computerAndMicrocontrollers/service-and-support/Orange-Pi-Zero-2W.html)
    - User Manual [download](https://drive.google.com/drive/folders/1KIZMMDBlqf1rKmOEhGH7_7A-COAgYoGZ)
    - Schematic [download](https://drive.google.com/drive/folders/1tyaEemq5COwmbvGT7v_cfKhg2_t4u_yg)
    - Official tools [download](https://drive.google.com/drive/folders/1vsbWC8RqeLDxNBWgYmiKxOYcF6l9iJq1)
- [Orange Pi Debian Image](https://drive.google.com/drive/folders/1EH8mMQbgh4IgtOWKgg4nmRuZ57Gvfp9X)
- [3.5inch Display Tutorials](https://www.lcdwiki.com/3.5inch_ESP32-32E_Display)
    - data pack [download](https://www.dropbox.com/scl/fi/ulceplqf7xn9knpinxuja/3.5inch_ESP32-32E_ST7796_E32R35T_E32N35T_V1.0.zip?rlkey=qd2678p262tmonbbfml5yramo&e=1&st=5xl85jtt&dl=1)

# REFERENCES
- [boscacci/Arduino-Subway-Clock](https://github.com/boscacci/Arduino-Subway-Clock)
