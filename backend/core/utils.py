from decimal import Decimal, InvalidOperation


def to_decimal(value, default="0") -> Decimal:
    """
    Converte qualquer valor para Decimal com segurança.
    Retorna o default se o valor for None, vazio ou inválido.
    """
    try:
        if value is None or str(value).strip() == "":
            return Decimal(default)
        return Decimal(str(value))
    except InvalidOperation:
        return Decimal(default)
