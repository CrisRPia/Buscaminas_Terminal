"""
    Personal library to store common console input functions.
"""


def ask_num(s: str = "Ingrese un número entero: ") -> int | float:
    """
        Imprime s y devuelva un entero que pide por consola al usuario.
    """
    n = input(s)
    try:
        return int(n)
    except Exception as e:
        if e is KeyboardInterrupt:
            raise e
        try:
            print("float")
            return float(n)
        except Exception as e:
            if e is KeyboardInterrupt:
                raise e
            print("Error, el valor ingresado debe ser un número real.")
            return ask_num(s)


def ask_int(s: str) -> int:
    """
        Imprime s y devuelva un entero que pide por consola al usuario.
    """
    try:
        return int(input(s))
    except Exception as e:
        if e is KeyboardInterrupt:
            raise e
        print("Error, el valor ingresado debe ser un número entero.")
        return ask_int(s)


def ask_float(s: str) -> float:
    """
        Imprime s y devuelva un entero que pide por consola al usuario.
    """
    try:
        return float(input(s))
    except Exception as e:
        if e is KeyboardInterrupt:
            raise e
        print("Error, el valor ingresado debe ser un número real.")
        return ask_float(s)

