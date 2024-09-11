import ctypes
import time
from tools import MDBTools
from utils import MDBUtils
import threading
import logging

# Configurer le journalisation
logging.basicConfig(level=logging.DEBUG, format='%(message)s')

class Cashier:
    def __init__(self):
        self.mdb_api = ctypes.CDLL('mdb/MDB_master.dll')
        self.tools = MDBTools(self.mdb_api)
        self.utils = MDBUtils()
        self.coin_values = [0.10, 0.20, 0.50, 1.00, 2.00, 5.00, 10.00, 20.00, 50.00, 100.00]
        self.coin_routing = ["CASH_BOX", "TUBES", "NOT_USED", "REJECT"]
        self.accepted_coin_values = [0.1, 0.2, 0.5, 1.0, 2.0]
        self.events_buffer = [ctypes.c_ubyte()]
        self.port_number = 7
        self.total = 0
        self.compting = False
        self.total_inserted_amount = 0 
        self.finish = False
        self.has_enough_coins = True

        self.initialize_cashier()

    def initialize_cashier(self):
        self.connect_mdb()
        time.sleep(2.5)
        self.reset_mdb()
        time.sleep(2.5)
        self.init_mdb()
        time.sleep(2.5)
        self.setup_scaling_factor()
        self.setup_coin_types()


    def connect_mdb(self):
        result = self.tools.mdb_open_comm(self.port_number)
        logging.debug(f"connection {result}")

    def reset_mdb(self):
        result = 0
        while result == 0:
            result = self.tools.mdb_ca_reset()
            logging.debug(f"MDB_CA_reset {result}")
            if result == 0:
                time.sleep(2.5)

    def init_mdb(self):
        byte_array = bytearray([255])
        char_array = ctypes.c_char * len(byte_array)
        buffer_to_send = char_array.from_buffer(byte_array)

        result = 0
        while result == 0:
            result = self.tools.mdb_ca_init(buffer_to_send)
            logging.debug(f"MDB_CA_init {result}")
            if result == 0:
                time.sleep(2.5)

    def setup_scaling_factor(self):
        result = 0
        while result == 0:
            logging.debug(f"MDB_CA_SETUP_SCALING_FACTOR {result}")
            result = self.tools.mdb_ca_setup_scaling_factor()
            if result == 0:
                time.sleep(2.5)

    def setup_coin_types(self):
        self.coin_enable_mask = self.utils.calculate_coin_enable_mask(self.coin_values, self.accepted_coin_values)
        logging.debug(f"coin_enable: 0x{self.coin_enable_mask:04X}")
        logging.debug(self.coin_enable_mask)
        result = self.mdb_api.MDB_CA_coinType(0, 0)
        logging.debug(f"MDB_CA_poll {result}")
        time.sleep(3)


    def check_tube_status(self):
        events_buffer = ctypes.create_string_buffer(18)
        result = self.tools.mdb_ca_tube_status(events_buffer)
        if result:
            data = self.utils.parse_tube_status(events_buffer)
            logging.debug(data)
            if data["0.1"] < 2:
                self.has_enough_coins = False
            else : 
                self.has_enough_coins = True
            
    def accepter(self):
        self.tools.accepter(self.coin_enable_mask) 


    def compter(self):
        while True : 
            while self.compting:
                events_buffer = ctypes.create_string_buffer(8)
                if self.has_enough_coins : 
                
                    if self.total : 
                            try:
                                result = self.tools.ecouter(events_buffer)
                                if result:
                                    self.total_inserted_amount = self.utils.process_events(events_buffer, self.coin_values, self.coin_routing, self.total_inserted_amount)
                                    logging.debug(f"Montant Totale inseré {self.total_inserted_amount}")
                                    if self.total_inserted_amount >= self.total:
                                        self.compting = False
                                        payout = round(self.total_inserted_amount - self.total, 2)
                                        self.total = 0 
                                        logging.debug(f"le montant à rendre est : {payout}")
                                        self.payout_change(payout)
                                time.sleep(0.05)
                            except Exception as e:
                                logging.error(e)
                    else : 
                        print("ça tombe ici")
                        self.compting = False
                        self.check_tube_status()
            self.init_total_inserted_amount()
            self.is_finish = True
        
                

    def payout_change(self, amount_to_payout):
        self.compting = False
        self.tools.refuser()
        payout_cents = int((round(amount_to_payout, 2) * 10))
        logging.debug(f"PAYOUT AMOUNT IS: {payout_cents}")
        payout_data = [payout_cents]
        payout_buffer = ctypes.create_string_buffer(bytes(payout_data))
        result = self.tools.rendre_monnaie(payout_buffer)
        logging.debug(f"payout called and result is: {result}")
        return result

    def start_compter(self):
        monitoring_thread = threading.Thread(target=self.compter)
        monitoring_thread.daemon = True
        monitoring_thread.start()

    def get_total_inserted_amount(self) : 
        return self.total_inserted_amount
    def init_total_inserted_amount(self) : 
        self.total_inserted_amount = 0 

    def get_is_finish(self) : 
        return self.finish
cashier = Cashier()
cashier.start_compter()