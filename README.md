# FaceSwap
FaceSwap program written in _Python_, using _Dlib_ and _OpenCV_ libraries.
While _Dlib_ is used to capture the landmarks over a face, _OpenCV_ is used to manipulate the images data.
It takes two files as input, where each one must contain only one face, the source face and the destination face, respectively.


### Dependencies
- Python 2.7
- OpenCV3
- Dlib

### Install

Some of Linux distributions already come with Python (2.5+). But if you still don't have it installed, click [here](https://www.python.org/downloads/).

To install OpenCV, follow these steps [here](http://www.pyimagesearch.com/2016/10/24/ubuntu-16-04-how-to-install-opencv/).

Next, to install Dlib, you may follow these steps [here](http://www.pyimagesearch.com/2017/03/27/how-to-install-dlib/).

### Run

Once you got all depencies installed and both files downloaded, go to directory containing those files and run the following command:

``` sh
$ python faceSwap.py <image1> <image2>
```

Where **image1** is the name of the file containing the source face, and **image2** is the name of the file containing the destination face. 



