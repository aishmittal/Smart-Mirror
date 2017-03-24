# Smart-Mirror
A smart mirror is basically a mirror with a screen behind it. That screen can be an Android tablet or a computer monitor. The mirror is a two way glass which is partially reflective and partially transparent.When one side of the mirror is brightly lit and the other is dark, it allows viewing from the darkened side and the people on the bright end side see their own reflection.
It can be powered by many devices such as a raspberry pi, your own unused laptop etc.It reduces the wastage of time where people getting ready for their office or for some other occasion who spent large time in front of mirror can do fruitful work such as getting to know today stocks prices, what kind of weather is going to be today, and Headlines of various kinds of news from different sources.

## Features
1. Face Recognition based User Login
2. Voice commands to control user interface and the information to be displayed
3. Information like
   * Weather at your location.
   * Current time and date
   * User's stock details
   * Users's events
   * News Headlines
   * Business News, Technology News, World News, Sports News 
   * Calender
   * Map of your current location
   * Quotes
4. Customised User Experience by providing information about things like Stocks that the user like to see everyday, what are his events today.

## Implementation
### Registration
1. Every User First Registers himself with **register.py** application where he would provide his username, password, firstname , lastname, dob and email. then a new user is created if username exist. 
2. After new user is created face dataset of user is generated and face identification model is built using microsoft face APIs
3. user could provide details of the various stocks that he would like to view on a daily basis in add stocks tab.
4. user could enter the events that would displayed on that particular day in add events tab.

### Running application
1. smarmirror application can be started by runnig **smartmirror.py**. on starting it would try to identify the user who is currently using the mirror by using a webcam placed at the top of the mirror.
2. Then that person would be logged in and would display his list of stocks and events today along with their time.
3. User can give voice commands for different information to be displayed at the bottom of the screen such as Sports news, Tech News etc as mentioned in the features.
4. A quote would be displayed at the bottom along with weather at top left so that there is space provided in the middle which would help the person to see his reflection on the mirror along with the text.

## Project Setup
currently the project is in Python2.7 but you can use Python3 as per your choice. Install required python packages accordingly.

### Required python packages
1.  opencv2
2.  cloudinary
3.  pyaudio2
4.  PyQt4
5.  feedparser
6.  MySQLdb
7.  speech_recognition
8.  googlefinance


### Clone
`git clone https://github.com/ARIES-IIT-R/Smart-Mirror.git`

**After clonning add following folders in root**

1.  dataset
2.  tmp

### APIs Used
1. Microsoft Cognitive Service
2. Bing Speech Recognition
3. Cloudinary
4. Google Map

### Components currently used
* An old unused laptop. A raspberry pi is better alternative for its short size, but its computing power is comparatively lesser as compared to a multicore processor which provides faster recognition and response.
* A webcam for Face and Voice Recognition
* Good Internet connection in order to send the data to our database and retrieve information about different things like weather, stocks etc.

## Limitations
The current implementation is prone to disturbances like noise from surrounding environment, when a person is giving commands to the mirror. As it is mostly used in a single person or small family environment such as our home, it is free from such kind of errors in those scenarios.

## Future Work
### Following things can be implemented in the near future :-
* The mirror acts like a personal assistant where it has control over all the devices at our house and women who spend most of the time in front of mirror can get their work done by giving voice commands.
* By adding touchscreen facility it improves user experience.

## Final Product
![Our Smart Mirror](/image/img1-small.jpg "Smart Mirror") 

## Video
[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/i0phxXGM5wE/0.jpg)](https://www.youtube.com/watch?v=i0phxXGM5wE)

## Thanks
©[MIT License](https://github.com/ARIES-IIT-R/Smart-Mirror/blob/master/LICENSE)












