# dice-recognition
2024, Till Bovermann


![setup](data/setup_IMG_0671-3000px.jpg)

recognise and count dice eyes 

## Todo

+ [ ] add ROI selection and cropping

## Installation

best to install into a virtual environment


set up a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate
```

install the required packages
```bash
python -m pip install -r requirements.txt
```

get help
```bash
python getDiceEyes.py -h
```

run an example
```bash
python getDiceEyes.py --min 0.3 --max 0.9 data/dice_5_eyes_4.jpg
```
