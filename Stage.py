import numpy as np
from Donut import Donut
from matplotlib import pyplot as plt


class Stage:
    """ 
    Esta clase representa un escenario en el cual colocaremos un dona
    y la proyectaremos sobre la pantalla, dada una iluminación y un observador.
    Dado un punto de la dona X = (x, y, z), un observador F = (0, f, 0), y un plano y = d,  
    donde f > d > R1+R2 > 0, queremos proyectar el punto X sobre el plano y = d con la perspectiva de F.
    Dicha proyección será sobre una pantalla de num_pixels x num_pixels pixeles.
    En cada pixel se renderizará el caracter correspondiente a la intensidad de luz que recibe
    el punto más cernano de la dona proyectado sobre dicho pixel.
    """

    def __init__(self, dona: Donut, light: np.array = np.array([0, -1, -1]), f: float = 10, d: float = 5, num_pixels: int = 30):
        """
        Inicializa el escenario.
        """
        assert f > d > dona.R1 + dona.R2 > 0, "f > d > R1 + R2 > 0"
        self.dona = dona
        self.light = light
        self.f = f
        self.d = d
        self.num_pixels = num_pixels
        self.illumination = np.fromiter(".,-~:;=!*#$@", dtype="<U1")
        self.screen = np.full((num_pixels, num_pixels), " ")

    def project(self):
        """
        Dado un punto de la dona X = (x, y, z), un observador F = (0, f, 0), y un plano y = d,  
        donde f > d > R1+R2 > 0, queremos proyectar el punto X sobre el plano y = d con la perspectiva de F.
        Para esto, consideremos la recta que pasa por X y F. Esta recta intersecta al plano y = d en el punto
        P = (x', d, z'). Queremos encontrar x' y z'.
        La ecuación de la recta R que pasa por X y F es:
            R(t) = F + t * (X - F) = (0, f, 0) + t * (x, y - f, z)
        Queremos encontrar t' tal que R intersecte al plano y = d. Es decir, queremos encontrar t' tal que:
            R(t') = (0, f, 0) + t' * (x, y - f, z) = (x', d, z')
        De la segunda coordenada de la ecuación anterior, tenemos que:
            f + t' * (y - f) = d
            t' = (d - f) / (y - f)
        Sustituyendo t' en las primeras y terceras coordenadas, tenemos que:
            x' = t' * x = (d - f) * x / (y - f)
            z' = t' * z = (d - f) * z / (y - f)
        """
        x, y, z = self.dona.points
        oyo = np.reciprocal(y - self.f)  # Calculamos 1/(y - f)
        # Proyectamos los puntos sobre el plano y = d
        xp = (self.d - self.f) * x * oyo
        zp = (self.d - self.f) * z * oyo

        return xp, zp, oyo

    def luminance(self):
        """
        Calcula la luminancia de cada punto de la dona como el negativo 
        del producto punto entre el vector normal y el vector de luz.
        """
        return - self.light @ self.dona.normals

    def animation(self, A: float, B: float):
        """
        Esta función crea un gif de la dona proyectada en 2D rotando.
        """
        from matplotlib.animation import FuncAnimation
        # Graficamos la dona proyectada
        xp, zp, _ = self.project()
        L = self.luminance()
        fig, ax = plt.subplots()
        sc = ax.scatter(xp, zp, s=1, c=L, cmap='viridis', vmin=-1, vmax=1)
        ax.set_xlabel('X')
        ax.set_ylabel('Z')
        ax.set_aspect('equal')
        fig.savefig('projected_dona.png')
        I = (self.dona.R2 + self.dona.R1) * (self.f - self.d) / self.f
        ax.set(xlim=[-1.1*I, 1.1*I], ylim=[-1.1*I, 1.1*I])

        def animate(frame, *fargs):
            dona = fargs[0]
            A = fargs[1]
            B = fargs[2]
            dona.rotate_x(A)
            dona.rotate_y(B)
            xp, zp, _ = self.project()
            # L = self.luminance()
            sc.set_offsets(np.c_[xp, zp])
            # sc.set_array(L)
            return sc,

        anim = FuncAnimation(fig, animate, frames=90, fargs=(
            self.dona, A, B), interval=50, blit=True)
        print("Creating gif...")
        anim.save('projected_dona.gif', dpi=100)
        plt.close()

    def render_frame(self, A: float, B: float) -> np.ndarray:
        """
        Renderiza un frame de la dona rotada A radianes en el eje x y B radianes en el eje y.
        """
        # Reiniciamos la pantalla
        self.screen = np.full((self.num_pixels, self.num_pixels), " ")
        # Rotamos la dona
        self.dona.rotate_x(A)
        self.dona.rotate_y(B)
        # Obtenemos los puntos rotados
        xp, zp, oyo = self.project()

        """ Calculamos la intensidad de luz que recibe cada punto
        como el negativo del producto punto entre el vector normal y el vector de luz.
        Entre más cercano a 1, más iluminado está el punto.
        Con esto, podemos asignar un caracter a cada punto. Si L < 0, el punto
        no está iluminado, por lo que se asigna un '.' .
        Si L > 0, el punto está iluminado, por lo que se asigna un caracter
        de la lista illumination según la intensidad de luz.
        """
        L = self.luminance()
        Lrange = (0, 0.9*L.max())  # Rango de valores de L.
        # Multiplicamos por 0.9 para que la dona esté un poco más iluminada.
        # Mapeamos los valores de L al rango de indices de la lista illumination
        char_index = np.interp(
            L, Lrange, (0, len(self.illumination)-1)).astype(int)
        chars = self.illumination[char_index]

        """ 
        Ahora, queremos proyectar los puntos sobre los correspondientes pixeles de la pantalla.
        Para ello, primero calculamos el intervalo de valores de x y z que abarca la dona proyectada.
        Para *estimar* este rango, es suficiente calcular la proyección del punto más alto de la dona.
        Dicho punto es (0, 0, R2 + R1).
        Usando semejanza de triángulos. La incognita es L:
            I / (R2 + R1) = (f - d) / f
            I = (R2 + R1) * (f - d) / f
        Así tenemos que los valores de xp y zp están en un intervalo un poco más amplio que [-I, I], 
        digamos [-1.1*I, 1.1*I].
        """
        I = (self.dona.R2 + self.dona.R1) * (self.f - self.d) / self.f

        """
        Siguiente, queremos mapear los valores de xp y zp al intervalo de enteros [0, num_pixels - 1].
        Es decir, queremos mapear el intervalo [-1.1*I, 1.1*I] al intervalo de enteros [0, num_pixels - 1].
        """
        xp = np.interp(xp, (-1.1*I, 1.1*I),
                       (0, self.num_pixels - 1)).astype(int)
        zp = np.interp(-zp, (-1.1*I, 1.1*I),
                       (0, self.num_pixels - 1)).astype(int)
        # -zp porque las filas de la pantalla van de 0 a num_pixels - 1 de arriba hacia abajo

        """
        Por último, queremos asignar un caracter a cada pixel. El caracter que le corresponde
        a cada pixel es el caracter del punto más cercano a la pantalla. Esta información la podemos
        obtener de la variable 'oyo' (0y0).
        Sean X = (x, y, z) y Y = (x', y', z') dos puntos de la dona. Notemos que y - f < 0 y y' - f < 0
        pues f > R1 + R2 > 0. Entonces, y < y' si y solo si:
            <=>          y < y'
            <=>      y - f < y' - f
            <=> 1/(y' - f) < 1/(y - f)
        Esto quiere decir que si ordenamos nuestros puntos (xp, zp) de forma descendente según el valor
        de oyo, entonces el primer punto (xp[0], zp[0]) es el punto más lejano a la pantalla, y el último
        punto (xp[-1], zp[-1]) es el punto más cercano a la pantalla.
        """
        # Ordenamos los puntos según el valor de oyo
        order = np.argsort(oyo)[::-1]
        xp = xp[order]
        zp = zp[order]
        chars = chars[order]
        # Asignamos los caracteres a los pixeles
        # zp, xp pues las filas de la pantalla representan el eje 'y' y las columnas el eje 'x'
        self.screen[zp, xp] = chars
        """
        Por qué la línea anterior funciona? Note que es posible que dos puntos x1 = (x1, y1, z1) y x2 = (x2, y2, z2) se proyecten en el mismo pixel.
        Supongamos que (xp1, zp1) son las coordenadas del pixel al que se proyecta x1, (xp2, zp2) son las coordenadas del pixel al que se proyecta x2,
        el caracter asignado a x1 es c1 y el caracter de x2 es c2.
        Se tiene entonces que (xp1, zp1) == (xp2, zp2). Ahora, asumamos sin pérdida de generalidad que (xp1, zp1)
        aparece antes que (xp2, zp2) en 'order'.
        Como (xp1, zp1) aparece antes que (xp2, zp2) en 'order', (xp1, zp1) está más lejos de la pantalla que (xp2, zp2).
        Al hacer self.screen[zp, xp] = chars, primero se asigna el caracter c1 al pixel (xp1, zp1) porque aparece primero en 'order' 
        y luego se asigna el caracter c2 al pixel (xp2, zp2).
        Pero (xp1, zp1) == (xp2, zp2) así que dicho pixel se asigna dos veces, primero con el caracter c1 y luego con el caracter c2.
        Así que el caracter que se muestra en el pixel (xp2, zp2) es correctamente el caracter c2 ya que (xp2, zp2) está más cerca de la pantalla.
        """

    def pprint(self) -> None:
        """ 
        Imprime los pixeles guardados en 'screen'.
        """
        print(*[" ".join(row) for row in self.screen], sep="\n", flush=True)
