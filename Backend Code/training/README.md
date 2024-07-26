# Overview

This is the backend training part of our system to predict the location of the Water Hyacinth mat on lakes.

For the satellite imagery it uses images from the [Waterweeds Watcher](https://davidkinsler123.users.earthengine.app/view/macrophyte-monitoring-tool) developed by Rhodes University and Centre for Biological Control.

Weather data is not yet used.

# Installation

You need to have Python installed.

All required pip dependencies can be installed at once with the following command:

```bash
pip install -r requirements.txt
```

# Starting the application

Please make sure that beforehand the preprocessing is done or you start the program with option `--preprocess`. Preprocessing must only be done once or after constants have been changed in the program to run it again.

```bash
python3 main.py --preprocess
```

For normal operation:

```bash
python3 main.py
```
