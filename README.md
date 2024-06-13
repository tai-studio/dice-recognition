# dice-recognition
2024, Till Bovermann


![setup](data/setup_single_IMG_0677-3000px.jpg)

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


## Usage

### single image

```bash
python getDiceEyes.py --help
```

run an example
```bash
python getDiceEyes.py --min 0.3 --max 0.9 data/dice_5_eyes_4.jpg
```


### video

![](data/diceEyes.gif)

```bash
python videoGrabber.py --window --src 0 --fps 1 --min 0.025 --dilateIterations 2 --kernelSize 1 --max 0.08 2>/dev/null
```
