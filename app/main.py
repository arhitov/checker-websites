from app.domain.domain import Domain
from app.request.request import Request
from app.request.method import Method
from app.dto.check import CheckDTO


def check(domain: str) -> CheckDTO:
    domain_cls = Domain(domain)
    domain_resolve = domain_cls.resolve()

    ports = [
        domain_cls.port(80)
    ]
    port_ssl = domain_cls.port(443)
    ports.append(port_ssl)

    ssl = None if not port_ssl.is_open else domain_cls.ssl()

    ports_methods = {}
    for port in ports:
        port_methods = []
        for method in [Method.GET, Method.HEAD]:
            port_methods.append(
                Request(domain).http_method(method, port.number)
            )
        if any(port_methods):
            ports_methods[port.number] = tuple(port_methods)

    return CheckDTO(
        domain=domain_cls.domain(),
        resolve=domain_resolve,
        ssl=ssl,
        ports=tuple(ports),
        ports_methods=ports_methods,
    )


def output(domain: str):
    check_dto = check(domain)
    print(f"Проверка доступности сайта: {check_dto.domain.domain}")

    domain_resolve = check_dto.resolve
    if domain_resolve is not None:
        print(f"IP адрес: {domain_resolve.ip}, Время резолва: {domain_resolve.resolve_time:.2f} сек")

    print("\nSSL-сертификат:")
    if check_dto.is_ssl():
        print(f"\tСертификат валиден: {'Да' if check_dto.ssl.is_valid else 'Нет'}")
        print(f"\tСертификационный центр: {check_dto.ssl.organization}")
        print(f"\tПоддерживаемые домены: {', '.join(check_dto.ssl.names)}")
        print(f"\tСрок действия: с {check_dto.ssl.start_date} до {check_dto.ssl.end_date}")
        print(f"\tОбщий срок действия: {check_dto.ssl.validity_period.days} дней")
        print(f"\tОсталось дней: {check_dto.ssl.left_period.days} дней")
    else:
        print('Сертификат ssl не поддерживается')

    print("\nПорты:")
    if any(check_dto.ports):
        for port_dto in check_dto.ports:
            if port_dto.is_open:
                print(f"Порт {port_dto.number} открыт, Время соединения: {port_dto.timers.connect:.2f} сек")
                if check_dto.has_port_methods(port_dto.number):
                    print("\tПорт поддерживает проверяемые методы:")
                    for method in check_dto.get_port_methods(port_dto.number):
                        if method.allowed:
                            print(f"\t\t- {method.method.value}")
                else:
                    print("\tПорт не поддерживает проверяемые методы")

            else:
                print(f"Порт {port_dto.number} закрыт или недоступен")
    else:
        print('\tНет данных по поддерживаемых портах')


if __name__ == '__main__':
    # domain = 'ya.ru'  # Замените на нужный домен
    domain = 'fl40.ru'  # Замените на нужный домен
    # domain = 'leangroup.ru'  # Замените на нужный домен
    output(domain)
