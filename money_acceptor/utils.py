
import logging
from __main__ import app 

# Configurer le journalisation
logging.basicConfig(level=logging.DEBUG, format='%(message)s')

class MDBUtils:
    def calculate_coin_enable_mask(self, coin_values, accepted_coin_values):
        coin_enable_mask = 0
        for coin in accepted_coin_values:
            if coin in coin_values:
                index = coin_values.index(coin)
                coin_enable_mask |= (1 << index)
        return coin_enable_mask

    def process_events(self, events_buffer, coin_values, coin_routing, total_inserted_amount):
        events = [int.from_bytes(events_buffer[i], byteorder='big') for i in range(1, 4)]
        event_1, event_2, event_3 = events

        if event_1 == 0x00 and event_2 == 0x03 and event_3 == 0x02:
            event_4 = int.from_bytes(events_buffer[4], byteorder='big')
            routing_code = (event_4 >> 4) & 0b11
            coin_index = event_4 & 0b1111
            if coin_routing[routing_code] in ("CASH_BOX", "TUBES"):
                inserted_coin_value = round(coin_values[coin_index], 2)
                total_inserted_amount += inserted_coin_value
                total_inserted_amount = round(total_inserted_amount, 2)
                message = f"Coin inserted: {inserted_coin_value} in {coin_routing[routing_code]}"
                print(message)
            elif coin_routing[routing_code] in ("NOT_USED", "REJECT"):
                inserted_coin_value = round(coin_values[coin_index], 2)
                message = f"Coin inserted: {inserted_coin_value} in {coin_routing[routing_code]}"
                print(message)
        return total_inserted_amount

    def parse_tube_status(self, events_buffer):
        pieces = [int.from_bytes(events_buffer[i], byteorder="big") for i in range(4, 9)]
        data = {
            "0.1": pieces[0],
            "0.2": pieces[1],
            "0.5": pieces[2],
            "1.0": pieces[3],
            "2.0": pieces[4]
        }
        app.logger.error(data)
        return data
