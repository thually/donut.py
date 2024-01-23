import numpy as np

class Donut:
    """
    Clase que representa una forma de toro o dona.

    Atributos:
        R1 (float): Radio de la sección transversal del toro.
        R2 (float): Radio de revolución del toro.
        num_thetas (int): El número de puntos a utilizar en la dirección theta.
        num_phis (int): El número de puntos a utilizar en la dirección phi.
    """
    def __init__(self, R1:float = 1, R2:float = 2, num_thetas:int = 100, num_phis:int = 150):
        self.R1 = R1
        self.R2 = R2
        # Generamos los ángulos
        theta = np.linspace(0, 2*np.pi, num_thetas)
        phi = np.linspace(0, 2*np.pi, num_phis)

        """1. Creamos los puntos de la dona:
        Para generar las coordenadas, primero creamos los puntos de la sección transversal de la dona en el plano xz.
        Luego, rotamos los puntos de la sección transversal de la dona alrededor del eje z.
        Sección transversal en xz:
                [x]   [R2]   [R1*cos(theta)]
            X = [y] = [0 ] + [      0      ]
                [z]   [0 ]   [R1*sin(theta)]
        Matriz de rotación:
            R = [cos(phi) -sin(phi)  0]
                [sin(phi)  cos(phi)  0]
                [0         0         1]
        Puntos de la dona:
            X' = R*X
                 [(R2 + R1*cos(theta))*cos(phi)]
            X' = [(R2 + R1*cos(theta))*sin(phi)]
                 [       R1*sin(theta)         ]
        """
        # Generamos una malla tal que emparejamos todos los puntos de theta con todos los de phi
        theta, phi = np.meshgrid(theta, phi)
        cosTHETA = np.cos(theta).flatten()
        sinTHETA = np.sin(theta).flatten()
        cosPHI = np.cos(phi).flatten()
        sinPHI = np.sin(phi).flatten()
        # Generamos los puntos de la dona
        x = (R2 + R1*cosTHETA) * cosPHI
        y = (R2 + R1*cosTHETA) * sinPHI
        z = R1 * sinTHETA

        self.points = np.array([x, y, z])

        """2. Creamos los vectores normales
        Los vectores normales a la superficie (Nx, Ny, Nz) se obtiene igual que antes,
        excepto que el punto con el que empezamos es simplemente (cos(theta), 0, sen(theta)). 
        Luego aplicamos la misma rotación.
                [Nx]   [cos(phi) -sin(phi)  0]   [cos(theta)]   [cos(phi)*cos(theta)]
            N = [Ny] = [sin(phi)  cos(phi)  0] * [    0     ] = [sin(phi)*cos(theta)]
                [Nz]   [0         0         1]   [sin(theta)]   [     sin(theta)    ]
        """
        # Generamos los vectores normales
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
            title='Dona',
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
        Rotamos la dona alrededor del eje x.
        """
        # Generamos la matriz de rotación
        R = np.array([
            [1, 0, 0],
            [0, np.cos(A), -np.sin(A)],
            [0, np.sin(A),  np.cos(A)]
        ])
        # Rotamos los puntos
        self.points = R @ self.points
        # Rotamos los vectores normales
        self.normals = R @ self.normals
        
    def rotate_y(self, B:float):
        """
        Rotamos la dona alrededor del eje y.
        """
        # Generamos la matriz de rotación
        R = np.array([
            [np.cos(B), 0, np.sin(B)],
            [0, 1, 0],
            [-np.sin(B), 0, np.cos(B)]
        ])
        # Rotamos los puntos
        self.points = R @ self.points
        # Rotamos los vectores normales
        self.normals = R @ self.normals