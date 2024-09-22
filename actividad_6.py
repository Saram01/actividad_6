import random
from dataclasses import dataclass, field
from typing import ClassVar, Optional, Union

CORAZON = "\u2764\uFE0F"
TREBOL = "\u2663\uFE0F"
DIAMANTE = "\u2666\uFE0F"
ESPADA = "\u2660\uFE0F"
TAPADA = "\u25AE\uFE0F"
FICHAS_INICIALES = 100


@dataclass
class Carta:
    VALORES: ClassVar[list[str]] = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    PINTAS: ClassVar[list[str]] = [CORAZON, TREBOL, DIAMANTE, ESPADA]
    pinta: str
    valor: str
    tapada: bool = field(default=False, init=False)

    def calcular_valor(self, as_como_11=True) -> int:
        if self.valor == "A":
            return 11 if as_como_11 else 1
        elif self.valor in ["J", "Q", "K"]:
            return 10
        else:
            return int(self.valor)

    def __str__(self):
        return f"{TAPADA}" if self.tapada else f"{self.valor}{self.pinta}"


class Mano:

    def __init__(self, cartas: tuple[Carta, Carta]):
        self.cartas: list[Carta] = list(cartas)

    def es_blackjack(self) -> bool:
        if len(self.cartas) > 2:
            return False
        return (self.cartas[0].valor == "A" and self.cartas[1].valor in ["10", "J", "Q", "K"]) or \
               (self.cartas[1].valor == "A" and self.cartas[0].valor in ["10", "J", "Q", "K"])

    def agregar_carta(self, carta: Carta):
        self.cartas.append(carta)

    def calcular_valor(self) -> Union[int, str]:
        if any(carta.tapada for carta in self.cartas):
            return "--"

        valor = 0
        for carta in self.cartas:
            valor += carta.calcular_valor(valor < 11)

        return valor

    def destapar(self):
        for carta in self.cartas:
            carta.tapada = False

    def limpiar(self):
        self.cartas.clear()

    def __str__(self):
        return " | ".join(f"{str(carta):^5}" for carta in self.cartas)


class Baraja:

    def __init__(self):
        self.cartas: list[Carta] = [Carta(pinta, valor) for valor in Carta.VALORES for pinta in Carta.PINTAS]

    def reiniciar(self):
        self.cartas = [Carta(pinta, valor) for valor in Carta.VALORES for pinta in Carta.PINTAS]

    def revolver(self):
        random.shuffle(self.cartas)

    def repartir_carta(self, tapada=False) -> Optional[Carta]:
        if len(self.cartas) > 0:
            carta = self.cartas.pop()
            carta.tapada = tapada
            return carta
        return None


@dataclass
class Jugador:
    nombre: str
    fichas: int
    mano: Mano = field(default=None, init=False)

    def inicializar_mano(self, cartas: tuple[Carta, Carta]):
        self.mano = Mano(cartas)

    def recibir_carta(self, carta: Carta):
        self.mano.agregar_carta(carta)

    def agregar_fichas(self, fichas: int):
        self.fichas += fichas

    def tiene_fichas(self) -> bool:
        return self.fichas > 0

    def puede_apostar(self, cantidad: int) -> bool:
        return self.fichas >= cantidad


class Casa:

    def __init__(self):
        self.mano: Optional[Mano] = None

    def inicializar_mano(self, cartas: tuple[Carta, Carta]):
        self.mano = Mano(cartas)

    def recibir_carta(self, carta: Carta):
        self.mano.agregar_carta(carta)


class Blackjack:

    def __init__(self):
        self.apuesta_actual: int = 0
        self.jugador: Optional[Jugador] = None
        self.casa: Casa = Casa()
        self.baraja: Baraja = Baraja()

    def registrar_usuario(self, nombre: str):
        self.jugador = Jugador(nombre, FICHAS_INICIALES)

    def iniciar_juego(self, apuesta: int):
        self.apuesta_actual = apuesta

        self.baraja.reiniciar()
        self.baraja.revolver()

        if self.jugador.mano is not None:
            self.jugador.mano.limpiar()
            self.casa.mano.limpiar()

        # Repartir cartas
        carta_1 = self.baraja.repartir_carta()
        carta_2 = self.baraja.repartir_carta()
        self.jugador.inicializar_mano((carta_1, carta_2))

        carta_1 = self.baraja.repartir_carta()
        carta_2 = self.baraja.repartir_carta(tapada=True)
        self.casa.inicializar_mano((carta_1, carta_2))

    def repartir_carta_a_jugador(self):
        self.jugador.recibir_carta(self.baraja.repartir_carta())

    def jugador_perdio(self) -> bool:
        return self.jugador.mano.calcular_valor() > 21

    def destapar_mano_de_la_casa(self):
        self.casa.mano.destapar()

    def casa_puede_pedir(self) -> bool:
        valor_mano_casa = self.casa.mano.calcular_valor()
        return valor_mano_casa <= self.jugador.mano.calcular_valor() and valor_mano_casa <= 16

    def repartir_carta_a_la_casa(self):
        self.casa.recibir_carta(self.baraja.repartir_carta())

    def jugador_gano(self) -> bool:
        valor_mano_jugador = self.jugador.mano.calcular_valor()
        valor_mano_casa = self.casa.mano.calcular_valor()
        return self.jugador.mano.es_blackjack() or valor_mano_jugador > valor_mano_casa or valor_mano_casa > 21

    def casa_gano(self) -> bool:
        valor_mano_jugador = self.jugador.mano.calcular_valor()
        valor_mano_casa = self.casa.mano.calcular_valor()
        return self.casa.mano.es_blackjack() or valor_mano_jugador < valor_mano_casa or valor_mano_jugador > 21

    def hay_empate(self) -> bool:
        valor_mano_jugador = self.jugador.mano.calcular_valor()
        valor_mano_casa = self.casa.mano.calcular_valor()
        return valor_mano_casa == valor_mano_jugador

    def jugar(self):
        while self.jugador.tiene_fichas():
            print(f"\nFichas disponibles: {self.jugador.fichas}")
            apuesta = int(input("¿Cuántas fichas deseas apostar? "))
            if not self.jugador.puede_apostar(apuesta):
                print("No tienes suficientes fichas para apostar.")
                continue
            
            self.iniciar_juego(apuesta)
            print(f"\nMano de {self.jugador.nombre}: {self.jugador.mano}")
            print(f"Valor: {self.jugador.mano.calcular_valor()}")
            if self.jugador.mano.es_blackjack():
                print("¡Blackjack! Ganaste.")
                self.jugador.agregar_fichas(self.apuesta_actual * 2)
                continue
            
            while True:
                accion = input("¿Quieres pedir carta (p) o plantarte (s)? ").lower()
                if accion == 'p':
                    self.repartir_carta_a_jugador()
                    print(f"\nMano de {self.jugador.nombre}: {self.jugador.mano}")
                    print(f"Valor: {self.jugador.mano.calcular_valor()}")
                    if self.jugador_perdio():
                        print("Te pasaste de 21. ¡Perdiste!")
                        self.jugador.agregar_fichas(-self.apuesta_actual)
                        break
                elif accion == 's':
                    break

            self.destapar_mano_de_la_casa()
            print(f"\nMano de la casa: {self.casa.mano}")
            while self.casa_puede_pedir():
                self.repartir_carta_a_la_casa()
                print(f"Mano de la casa: {self.casa.mano}")
                if self.casa.mano.calcular_valor() > 21:
                    print("La casa se pasó de 21. ¡Ganaste!")
                    self.jugador.agregar_fichas(self.apuesta_actual)
                    break

            if not self.jugador_perdio() and not self.casa.mano.calcular_valor() > 21:
                if self.jugador_gano():
                    print("¡Ganaste!")
                    self.jugador.agregar_fichas(self.apuesta_actual)
                elif self.casa_gano():
                    print("La casa gana.")
                    self.jugador.agregar_fichas(-self.apuesta_actual)
                else:
                    print("Es un empate.")

        print("Te has quedado sin fichas. Fin del juego.")


# Iniciar el juego
if __name__ == "__main__":
    juego = Blackjack()
    nombre_jugador = input("Introduce tu nombre: ")
    juego.registrar_usuario(nombre_jugador)
    juego.jugar()
