import numpy as np

class Donut:
    """
    Class representing a torus or donut shape.

    Attributes:
        R1 (float): Radius of the torus cross-section.
        R2 (float): Revolution radius of the torus.
        num_thetas (int): The number of points to use in the theta direction.
        num_phis (int): The number of points to use in the phi direction.
    """
    def __init__(self, R1:float = 1, R2:float = 2, num_thetas:int = 100, num_phis:int = 150):
        self.R1 = R1
        self.R2 = R2
        # Generate angles
        theta = np.linspace(0, 2*np.pi, num_thetas)
        phi = np.linspace(0, 2*np.pi, num_phis)

        """1. Create donut points:
        To generate coordinates, first create points for the cross-section of the donut in the xz plane.
        Then, rotate the points of the donut cross-section around the z-axis.
        Cross-section in xz:
                [x]   [R2]   [R1*cos(theta)]
            X = [y] = [0 ] + [      0      ]
                [z]   [0 ]   [R1*sin(theta)]
        Rotation matrix:
            R = [cos(phi) -sin(phi)  0]
                [sin(phi)  cos(phi)  0]
                [0         0         1]
        Donut points:
            X' = R*X
                 [(R2 + R1*cos(theta))*cos(phi)]
            X' = [(R2 + R1*cos(theta))*sin(phi)]
                 [       R1*sin(theta)         ]
        """
        # Generate a mesh pairing all theta points with all phi points
        theta, phi = np.meshgrid(theta, phi)
        cosTHETA = np.cos(theta).flatten()
        sinTHETA = np.sin(theta).flatten()
        cosPHI = np.cos(phi).flatten()
        sinPHI = np.sin(phi).flatten()
        # Generate donut points
        x = (R2 + R1*cosTHETA) * cosPHI
        y = (R2 + R1*cosTHETA) * sinPHI
        z = R1 * sinTHETA

        self.points = np.array([x, y, z])

        """2. Create normal vectors
        The normal vectors to the surface (Nx, Ny, Nz) are obtained similarly as before,
        except that the starting point is simply (cos(theta), 0, sin(theta)).
        Then, apply the same rotation.
                [Nx]   [cos(phi) -sin(phi)  0]   [cos(theta)]   [cos(phi)*cos(theta)]
            N = [Ny] = [sin(phi)  cos(phi)  0] * [    0     ] = [sin(phi)*cos(theta)]
                [Nz]   [0         0         1]   [sin(theta)]   [     sin(theta)    ]
        """
        # Generate normal vectors
        Nx = cosPHI * cosTHETA
        Ny = sinPHI * cosTHETA
        Nz = sinTHETA

        self.normals = np.array([Nx, Ny, Nz])

    def plot(self, ord:np.array = None, colorscale:str = 'Viridis'):
        import plotly.graph_objs as go

        if type(ord) == type(None): ord = np.arange(len(self.points[0]))

        print("3D Plotting...")
        # create a scatter3d trace
        trace = go.Scatter3d(
            x=self.points[0],
            y=self.points[1],
            z=self.points[2],
            mode='markers',
            marker=dict(
                size=2,
                color=ord,                # set color to the z-axis value
                colorscale=colorscale,   # choose a colorscale
                opacity=0.8
            )
        )

        # create a layout
        layout = go.Layout(
            title='Donut',
            scene=dict(
                xaxis=dict(title='X'),
                yaxis=dict(title='Y'),
                zaxis=dict(title='Z'),
                aspectmode='data'
            ),
            margin=dict(l=0, r=0, b=0, t=0)
        )

        # create a figure
        fig = go.Figure(data=[trace], layout=layout)
        fig.show()

    def rotate_x(self, A:float):
        """
        Rotate the donut around the x-axis.
        """
        # Generate rotation matrix
        R = np.array([
            [1, 0, 0],
            [0, np.cos(A), -np.sin(A)],
            [0, np.sin(A),  np.cos(A)]
        ])
        # Rotate points
        self.points = R @ self.points
        # Rotate normal vectors
        self.normals = R @ self.normals

    def rotate_y(self, B:float):
        """
        Rotate the donut around the y-axis.
        """
        # Generate rotation matrix
        R = np.array([
            [np.cos(B), 0, np.sin(B)],
            [0, 1, 0],
            [-np.sin(B), 0, np.cos(B)]
        ])
        # Rotate points
        self.points = R @ self.points
        # Rotate normal vectors
        self.normals = R @ self.normals
