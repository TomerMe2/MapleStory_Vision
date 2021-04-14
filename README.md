# MapleStory Vision
This program will take potions automatically and pick drops automatically.
This program is designed to work on before BigBang maplestory look.

# To run this program:
1. create a venv with Python 3.7
2. run install_requirements.bat
3. run initiator.py file

# Explanation
This program has 3 parts. The GUI, the auto potions process and the auto drop pick process.

The auto potions executes the following loop:
1. Take a picture of your MapleStory window.
2. Find the countours in said picture.
3. Find 3 countours in the bottom 10% of the screen that are ordered from left to right, roughly with the same size - these are the bars.
4. Calculate the HP percentage and the MP percentage by going through a line in the middle of the bar and count gray pixels vs non-gray pixels. The percentage of current HP or MP is number_of_non_gray_pixels / number_of_gray_pixels.
5. If the percentage of the HP or the MP is below the threshold defined in the GUI, click on the button defined in the GUI to take the appropriate potion.

The auto drop pick process first finds how your player tag look (using OCR). It will be used to detect the location of your player. The detection takes about 6 seconds (may vary on different PCs). <br/>
After the detection was completed, the auto drop pick process executes the following loop:
1. Take a picture of your MapleStory window.
2. Find the location of your player using your name tag.
3. Find the contours in said picture.
4. Find an item around the player. An item is defined by having 2 contours at least that share some X coordinates inside the picture, and that are in distinctly different heights from each other.
5. If such item was found, click on the Z key.

For the auto drop pick to work, you must put your drop pick on Z (the default key) <br/>

# Where Can It Work?
This program was tailored to work with "Bereshit" private server, but it can work on other private servers as well (such as MapleRoyals), as long as they use the look that was present on GMS before the BigBang update. It's important for the HP and MP bars to be next to each other left\right wise instead of one on top of the other.
You can pick the MapleStory window using this apps GUI, so you can pick any private server you'll want, as long as it runs on your PC.
A version for current GMS can be created, please let me know if you need it by submitting an issue.
