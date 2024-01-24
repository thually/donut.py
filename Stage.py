import numpy as np
from Donut import Donut
from matplotlib import pyplot as plt


class Stage:
    """ 
    This class represents a stage in which we place a donut and project it onto the screen, given lighting and an observer.
    Given a point on the donut X = (x, y, z), an observer F = (0, f, 0), and a plane y = d,
    where f > d > R1+R2 > 0, we want to project point X onto the y = d plane with the perspective of F.
    This projection will be onto a screen with num_pixels x num_pixels pixels.
    Each pixel will render the character corresponding to the light intensity received by
    the nearest point on the donut projected onto that pixel.
    """

    def __init__(self, donut: Donut, light: np.array = np.array([0, -1, -1]), f: float = 10, d: float = 5, num_pixels: int = 30):
        """
        Initializes the stage.
        """
        assert f > d > donut.R1 + donut.R2 > 0, "f > d > R1 + R2 > 0"
        self.donut = donut
        self.light = light
        self.f = f
        self.d = d
        self.num_pixels = num_pixels
        self.illumination = np.fromiter(".,-~:;=!*#$@", dtype="<U1")
        self.screen = np.full((num_pixels, num_pixels), " ")

    def project(self):
        """
        Given a point on the donut X = (x, y, z), an observer F = (0, f, 0), and a plane y = d,
        where f > d > R1+R2 > 0, we want to project point X onto the plane y = d with the perspective of F.
        For this, consider the line passing through X and F. This line intersects the plane y = d at point
        P = (x', d, z'). We want to find x' and z'.
        The equation of the line R passing through X and F is:
            R(t) = F + t * (X - F) = (0, f, 0) + t * (x, y - f, z)
        We want to find t' such that R intersects the plane y = d. That is, we want to find t' such that:
            R(t') = (0, f, 0) + t' * (x, y - f, z) = (x', d, z')
        From the second coordinate of the above equation, we have:
            f + t' * (y - f) = d
            t' = (d - f) / (y - f)
        Substituting t' into the first and third coordinates, we have:
            x' = t' * x = (d - f) * x / (y - f)
            z' = t' * z = (d - f) * z / (y - f)
        """
        x, y, z = self.donut.points
        oyo = np.reciprocal(y - self.f)  # Calculate 1/(y - f)
        # Project points onto the y = d plane
        xp = (self.d - self.f) * x * oyo
        zp = (self.d - self.f) * z * oyo

        return xp, zp, oyo

    def luminance(self):
        """
        Calculates the luminance of each point on the donut as the negative
        of the dot product between the normal vector and the light vector.
        """
        return - self.light @ self.donut.normals

    def animation(self, A: float, B: float):
        """
        This function creates a gif of the projected donut in 2D rotation.
        """
        from matplotlib.animation import FuncAnimation
        # Plot the projected donut
        xp, zp, _ = self.project()
        L = self.luminance()
        fig, ax = plt.subplots()
        sc = ax.scatter(xp, zp, s=1, c=L, cmap='viridis', vmin=-1, vmax=1)
        ax.set_xlabel('X')
        ax.set_ylabel('Z')
        ax.set_aspect('equal')
        fig.savefig('projected_dona.png')
        I = (self.donut.R2 + self.donut.R1) * (self.f - self.d) / self.f
        ax.set(xlim=[-1.1*I, 1.1*I], ylim=[-1.1*I, 1.1*I])

        def animate(frame, *fargs):
            donut = fargs[0]
            A = fargs[1]
            B = fargs[2]
            donut.rotate_x(A)
            donut.rotate_y(B)
            xp, zp, _ = self.project()
            # L = self.luminance()
            sc.set_offsets(np.c_[xp, zp])
            # sc.set_array(L)
            return sc,

        anim = FuncAnimation(fig, animate, frames=90, fargs=(
            self.donut, A, B), interval=50, blit=True)
        print("Creating gif...")
        anim.save('projected_dona.gif', dpi=100)
        plt.close()

    def render_frame(self, A: float, B: float) -> np.ndarray:
        """
        Renders a frame of the rotated donut A radians on the x-axis and B radians on the y-axis.
        """
        # Reset the screen
        self.screen = np.full((self.num_pixels, self.num_pixels), " ")
        # Rotate the donut
        self.donut.rotate_x(A)
        self.donut.rotate_y(B)
        # Get the rotated points
        xp, zp, oyo = self.project()

        """ Calculate the light intensity received by each point
        as the negative of the dot product between the normal vector and the light vector.
        Closer to 1 means more illuminated the point is.
        With this, we can assign a character to each point. If L < 0, the point
        is not illuminated, so a '.' is assigned.
        If L > 0, the point is illuminated, so a character
        from the illumination list is assigned according to the light intensity.
        """
        L = self.luminance()
        Lrange = (0, 0.9*L.max())  # Range of L values.
        # Multiply by 0.9 so that the donut is a bit more illuminated.
        # Map the values of L to the range of indices of the illumination list
        char_index = np.interp(
            L, Lrange, (0, len(self.illumination)-1)).astype(int)
        chars = self.illumination[char_index]

        """ 
        Now, we want to project the points onto the corresponding pixels of the screen.
        To do this, first calculate the interval of x and z values covered by the projected donut.
        To *estimate* this range, it is sufficient to calculate the projection of the highest point on the donut.
        That point is (0, 0, R2 + R1).
        Using triangle similarity. The unknown is I:
            I / (R2 + R1) = (f - d) / f
            I = (R2 + R1) * (f - d) / f
        So we have that the values of xp and zp are in a slightly wider interval than [-I, I],
        say [-1.1*I, 1.1*I].
        """
        I = (self.donut.R2 + self.donut.R1) * (self.f - self.d) / self.f

        """
        Next, we want to map the values of xp and zp to the range of integers [0, num_pixels - 1].
        That is, we want to map the interval [-1.1*I, 1.1*I] to the interval of integers [0, num_pixels - 1].
        """
        xp = np.interp(xp, (-1.1*I, 1.1*I),
                       (0, self.num_pixels - 1)).astype(int)
        zp = np.interp(-zp, (-1.1*I, 1.1*I),
                       (0, self.num_pixels - 1)).astype(int)
        # -zp because the rows of the screen go from 0 to num_pixels - 1 from top to bottom

        """
        Finally, we want to assign a character to each pixel. The character that corresponds
        to each pixel is the character of the point nearest to the screen. This information can be
        obtained from the variable 'oyo' (0y0).
        Let X = (x, y, z) and Y = (x', y', z') be two points on the donut. Note that y - f < 0 and y' - f < 0
        since f > R1 + R2 > 0. So, y < y' if and only if:
            <=>          y < y'
            <=>      y - f < y' - f
            <=> 1/(y' - f) < 1/(y - f)
        This means that if we order our points (xp, zp) in descending order according to the value
        of oyo, then the first point (xp[0], zp[0]) is the point furthest from the screen, and the last
        point (xp[-1], zp[-1]) is the point closest to the screen.
        """
        # Sort the points according to the value of oyo
        order = np.argsort(oyo)[::-1]
        xp = xp[order]
        zp = zp[order]
        chars = chars[order]
        # Assign characters to pixels
        # zp, xp because the rows of the screen represent the 'y' axis and the columns the 'x' axis
        self.screen[zp, xp] = chars
        """
        Why does the above line work? Note that it is possible that two points x1 = (x1, y1, z1) and x2 = (x2, y2, z2) are projected onto the same pixel.
        Suppose (xp1, zp1) are the coordinates of the pixel to which x1 is projected, (xp2, zp2) are the coordinates of the pixel to which x2 is projected,
        the character assigned to x1 is c1, and the character of x2 is c2.
        Then (xp1, zp1) == (xp2, zp2). Now, assuming without loss of generality that (xp1, zp1)
        appears before (xp2, zp2) in variable 'order'.
        Since (xp1, zp1) appears before (xp2, zp2) in 'order', (xp1, zp1) is further from the screen than (xp2, zp2).
        By doing self.screen[zp, xp] = chars, the character c1 is first assigned to the pixel (xp1, zp1) because it appears first in 'order'
        and then the character c2 is assigned to the pixel (xp2, zp2).
        But (xp1, zp1) == (xp2, zp2) so that pixel is assigned twice, first with the character c1 and then with the character c2.
        So the character shown in pixel (xp2, zp2) is correctly the character c2 since (xp2, zp2) is closer to the screen.
        """

    def pprint(self) -> None:
        """ 
        Prints the pixels stored in 'screen'.
        """
        print(*[" ".join(row) for row in self.screen], sep="\n", flush=True)
