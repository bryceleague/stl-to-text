# stl-to-text
An extremely ineffcient way to render a 3D model in the convenience of the command line.  
Simply pass one or more binary stl files as arguments (best used with only one).  
Automatically centers, applies a perspective effect, and scale to fit your current terminal size  
Now with command line arguments!
## Example Output
![Example Output of Stanford Bunny](./sample_output.png)  
Produced by `./stl-to-text Bunny-LowPoly.stl -rx=-1` given that the file `Bunny-LowPoly.stl` exists and is the correct model.
## How to Use
Enter each file you want to display followed by arguments to apply transformations to each model individually  
For example, if with two files foo.stl and bar.stl you can rotate foo by 1 radian in the x axis, translate bar by 50 cells on the y axis, and display both with the following command: `./stl_to_text foo.stl -rx=1 bar.stl -y=50`

Transformations done through flags will be done in the order in which they are typed so if you do multiple tranforms on the same object ensure that they are done in the correct order.

Additionally, each object is scaled to fit the terminal before being transformed then after transformation the entire scene is then scaled to fit the current terminal size. This ensures that objects has a similar relative size and the entire scene fits in the terminal.
### --help
```
Usage: stl-to-text [OPTIONS]... [FILE [OPTIONS]...]...
Display mesh encoded by binary stl FILE transformed by OPTIONS
transformations are done in the order OPTIONS is listed
Example: stl-to-text foo.stl -x=50 bar.stl -ry=2

Transforms:
  -x=, -y=, -z=           translates the preceding object by the 
                          amount of cells that follows the equals sign
  -s=, -sx=, -sy=, -sz=   scales the preceding object by the amount that 
                          follows the equals sign; -s scales all axises 
                          equally
  -rx=, -ry=, -rz=        rotates the preceding object by the amount of 
                          radians that follows the equals sign
```
