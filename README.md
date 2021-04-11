# MapleStory Auto Pots
Maplestory Auto Pots Program. This program is designed to work on before BigBang maplestory look.

# To run this program:
1. create a venv with Python 3.7
2. install the requirements from requirements.txt file
3. run initiator.py file

# Explanation
The program executes the following loop:
1. Take a picture of your MapleStory window.
2. Find the countours in said picture.
3. Find 3 countours in the bottom 10% of the screen that are ordered from left to right, roughly with the same size - these are the bars.
4. Calculate the HP percentage and the MP percentage by going through a line in the middle of the bar and count gray pixels vs non-gray pixels. The percentage of current HP or MP is number_of_non_gray_pixels / number_of_gray_pixels.
5. If the percentage of the HP or the MP is below the threshold defined in the GUI, click on the button defined in the GUI to take the appropriate potion.


This program was tailored to work with "Bereshit" private server, but it can work on other private servers as well, as long as they use the look that was present on GMS before the BigBang update. It's important for the HP and MP bars to be next to each other left\right wise instead of one on top of the other. <br/>
In order to make it work with other private servers, change the variable MAPLE_WINDOW_NM in snapshoter.py to be the name of the desired MapleStory private server window. <br/>
A version for current GMS can be created, please let me know if you need it by submitting an issue.
