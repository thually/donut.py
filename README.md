# donut.py 🍩🥯
This project consists of creating a visual animation on the console of a three-dimensional donut that rotates centered at the origin using ASCII characters to represent its illumination.  
Despite the apparent simplicity, this project is technically and artistically challenging, with a lot of mathematics involved!

For this project my inspiration was the classic [donut.c](https://www.a1k0n.net/2011/07/20/donut-math.html) by [Andy Sloane](https://www.a1k0n.net/about.html). When I first saw the animation of his 'spinning donut' a few years ago I was mesmerized and knew that at some point I had to implement it myself.

My goal was to come up with the same donut animation, but on my own. For this I used the same mathematical reasoning illustrated by Andy in the [article](https://www.a1k0n.net/2011/07/20/donut-math.html), but a quite different programming approach than the one he originally used.

## Differences between Andy's and my implementation 💻

* The first difference between Andy's creation and mine, is that I left the donut fixed at the origin, and moved the along the y-axis. Andy leaves the screen fixed in the y = 0 plane and moves the donut on the y-axis, so in his animation when the donut rotates around the axes it looks like it is flying and moving, while mine looks like it is rotating still at its position.

* Second, my approach to coding the donut in Python is for the program logic to be declarative, rather than the imperative approach that Andy uses. To achieve this, I relied heavily on vector operations, using the numpy package. 

* Third, I divided the program logic into classes:
   - The first class Dona.py encapsulates everything related to the donut as an object. This includes: the generation of all the donut points and normal vectors of the donut, and the necessary methods to rotate these points and normals simultaneously around two other axes. Additionally I implemented a method to visualize the donut in 3D using the plotly library.

   - The second class Stage.py comprises all the logic related to the projection of the donut. This class takes into account a donut object, the position of the screen on which it is to be projected and the position of the observer. With this, the methods of this class manage to project the donut points on a discrete mesh and assigns them an illumination. With this information it is possible to print a frame of the animation through the console.

   - Finally, the App.py file is in charge of gathering all the classes and methods to generate the animation. This file contains the animation logic, which consists of rotating the donut on the x-axis and y-axis, and then projecting it on the screen. This process is repeated for each frame of the animation, and is printed on the console.

The source code is very well commented and explains in great detail each of the steps and their involved mathematics to get to the flying donut.

**NOTE:** To run the project, you must have all the necessary packages installed and the Donaut.py, Stage.py and App.py files in the same folder. Then, you must run the App.py file with Python.
