# stl-to-text
An extremely ineffcient way to render a 3D model in the convenience of the command line.  
Simply pass one or more binary stl files as arguments (best used with only one).  
Automatically centers, applies a perspective effect, and scale to fit your current terminal size  
Now with command line arguments!
# How to Use
Enter each file you want to display followed by arguments to apply transformations to each model individually  
For example, if with two files foo.stl and bar.stl you can rotate foo by 1 radian in the x axis, translate bar by 50 cells on the y axis, and display both with the following command: `python3 main.py foo.stl -rx=1 bar.stl -y=50`

Transformations done through flags will be done in the order in which they are typed so if you do multiple tranforms on the same object ensure that they are done in the correct order.

Additionally, each object is scaled to fit the terminal before being transformed then after transformation the entire scene is then scaled to fit the current terminal size. This ensures that objects has a similar relative size and the entire scene fits in the terminal.
