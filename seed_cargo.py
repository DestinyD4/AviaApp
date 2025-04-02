from app import create_app
from app.extensions import db
from app.models import Cargo

app = create_app()

with app.app_context():
    test_cargos = [
        # 1. Полностью заполненная запись
        Cargo(
            airline_code="SU",
            awb_number="12345678",
            shipper_line1="ООО Рога и Копыта",
            shipper_line2="Москва, ул. Примерная, д.1",
            shipper_line3="ИНН 1234567890",
            shipper_line4="Россия",
            recipient_line1="ИП Иванов И.И.",
            recipient_line2="Санкт-Петербург, ул. Образцовая, д.2",
            recipient_line3="ИНН 0987654321",
            recipient_line4="Россия",
            cargo_description_line1="Комплектующие для оборудования",
            cargo_description_line2="10 коробок, упаковано",
            cargo_description_line3="Вес нетто 100 кг",
            route1_to="SVO", route1_by="SU",
            route2_to="FRA", route2_by="LH",
            route3_to="JFK", route3_by="UA",
            agent_line1="Expeditors",
            agent_line2="Москва",
            agent_line3="Контакт: +7 (495) 123-45-67",
            agent_code="AGT123",
            airport_departure="Sheremetyevo",
            airport_arrival="New York JFK",
            booking="BK001",
            places_count=10,
            weight_brutto=150.0,
            volume=2.5,
            date_issued="2025-04-01",
            place_issued="Москва",
            signature="Иванов",
            payment_line1="Предоплата 100%",
            payment_line2="Безналичный расчёт",
            payment_line3="НДС включён",
            special_customs_info="Без ограничений"
        ),
        # 2. Частично заполненная запись
        Cargo(
            airline_code="LH",
            awb_number="87654321",
            shipper_line1="ООО Мир техники",
            recipient_line1="ИП Петров П.П.",
            cargo_description_line1="Электроника",
            route1_to="DME", route1_by="LH",
            agent_line1="DHL",
            agent_code="DHL456",
            airport_departure="Domodedovo",
            airport_arrival="Frankfurt",
            places_count=5,
            weight_brutto=75.0,
            date_issued="2025-04-01",
            place_issued="Москва",
            signature="Петров"
        ),
        # 3. Минимально заполненная запись
        Cargo(
            awb_number="00000001",
            shipper_line1="Тестовый отправитель",
            recipient_line1="Тестовый получатель"
        )
    ]

    db.session.bulk_save_objects(test_cargos)
    db.session.commit()
    print("Тестовые записи успешно добавлены.")
