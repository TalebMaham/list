import ctypes
import os
import time
from .tools import MDBTools
from .utils import MDBUtils
import threading
import logging
import requests
from requests.auth import HTTPBasicAuth
from __main__ import app 


# Configurer le journalisation
logging.basicConfig(level=app.logger.error, format='%(message)s')
port_number = int(os.environ.get("COIN_ACCEPTOR_PORT"))

class Cashier:
    def __init__(self):
        self.mdb_api = ctypes.CDLL('src/devices/money_acceptor/mdb/MDB_master.dll')
        self.tools = MDBTools(self.mdb_api)
        self.utils = MDBUtils()
        self.coin_values = [0.10, 0.20, 0.50, 1.00, 2.00, 5.00, 10.00, 20.00, 50.00, 100.00]
        self.coin_routing = ["CASH_BOX", "TUBES", "NOT_USED", "REJECT"]
        self.accepted_coin_values = [0.1, 0.2, 0.5, 1.0, 2.0]
        self.events_buffer = [ctypes.c_ubyte()]
        self.port_number = port_number
        self.total = 0
        self.compting = False
        self.total_inserted_amount = 0 
        

        self.initialize_cashier()


    def initialize_cashier(self):
        self.connect_mdb()
        self.reset_mdb()
        self.init_mdb()
        self.setup_scaling_factor()
        self.setup_coin_types()

    def connect_mdb(self):
        result = self.tools.mdb_open_comm(self.port_number)
        app.logger.error(f"connection {result}")
        


    def reset_mdb(self):
        result = 0
        while result == 0:
            result = self.tools.mdb_ca_reset()
            app.logger.error(f"MDB_CA_reset {result}")
            if result == 0:
                time.sleep(2.5)

    def init_mdb(self):
        byte_array = bytearray([255])
        char_array = ctypes.c_char * len(byte_array)
        buffer_to_send = char_array.from_buffer(byte_array)

        result = 0
        while result == 0:
            result = self.tools.mdb_ca_init(buffer_to_send)
            app.logger.error(f"MDB_CA_init {result}")
            if result == 0:
                time.sleep(2.5)

    def setup_scaling_factor(self):
        result = 0
        while result == 0:
            app.logger.error(f"MDB_CA_SETUP_SCALING_FACTOR {result}")
            result = self.tools.mdb_ca_setup_scaling_factor()
            if result == 0:
                time.sleep(2.5)

    def setup_coin_types(self):
        self.coin_enable_mask = self.utils.calculate_coin_enable_mask(self.coin_values, self.accepted_coin_values)
        app.logger.error(f"coin_enable: 0x{self.coin_enable_mask:04X}")
        app.logger.error(self.coin_enable_mask)
        result = self.mdb_api.MDB_CA_coinType(0, 0)
        app.logger.error(f"MDB_CA_poll {result}")

    def monitoring(self):
        while True:
            try:
                self.check_tube_status()
            except Exception as e:
                logging.error(e)
            time.sleep(3)

    def check_tube_status(self):
        events_buffer = ctypes.create_string_buffer(18)
        result = self.tools.mdb_ca_tube_status(events_buffer)
        if result:
            data = self.utils.parse_tube_status(events_buffer)
            app.logger.error(data)
            if data["0.1"] < 0:
                self.tools.refuser()
                app.logger.error("pas suffisament de monnaie ...")
            else:
                if self.compting:
                    self.tools.accepter(self.coin_enable_mask)
                    self.compter(self.total)
                    app.logger.error("Comptage terminé")
                    self.tools.refuser()
                    time.sleep(5)
        self.init_total_inserted_amount()

    def compter(self, total):
        events_buffer = ctypes.create_string_buffer(8)
        if total : 
            while self.compting:
                try:
                    result = self.tools.ecouter(events_buffer)
                    if result:
                        self.total_inserted_amount = self.utils.process_events(events_buffer, self.coin_values, self.coin_routing, self.total_inserted_amount)
                        app.logger.error(f"Montant Totale inseré {self.total_inserted_amount}")
                        if self.total_inserted_amount >= total:
                            payout = round(self.total_inserted_amount - total, 2)
                            self.total = 0 
                            app.logger.error(f"le montant à rendre est : {payout}")
                            self.compting = False
                    time.sleep(0.02)
                except Exception as e:
                    logging.error(e)
        else : 
            self.compting = False
            

    def payout_change(self, amount_to_payout):
        payout_cents = int((round(amount_to_payout, 2) * 10))
        app.logger.error(f"PAYOUT AMOUNT IS: {payout_cents}")
        payout_data = [payout_cents]
        payout_buffer = ctypes.create_string_buffer(bytes(payout_data))
        result = self.tools.rendre_monnaie(payout_buffer)
        app.logger.error(f"payout called and result is: {result}")
        return result

    def start_monitoring(self):
        monitoring_thread = threading.Thread(target=self.monitoring)
        monitoring_thread.daemon = True
        monitoring_thread.start()

    def get_total_inserted_amount(self) : 
        return self.total_inserted_amount
    def init_total_inserted_amount(self) : 
        self.total_inserted_amount = 0 

machine_id = os.environ.get("MACHINE_ID")
api_url =  os.environ.get("API_BASE_URL") + f"/machines/{machine_id}"
username = os.environ.get("API_USERNAME ")
password = os.environ.get("API_PASSWORD ")


cashier = None
#cashier = Cashier()
try:
    response = requests.request(
        "GET",
        f"{api_url}",
        auth=HTTPBasicAuth(username, password)
    )

    if response.status_code == 200:
        data = response.json()
        print(f"data: {data}") 
        has_coin_acceptor = True #data.get('has_coin_acceptor', False) 
        print(f"has_coin_acceptor: {has_coin_acceptor}")
        
        cashier = Cashier() if has_coin_acceptor else None
    else:
        logging.error(f"Request failed with status code {response.status_code}")
        app.logger.error(f"Request failed with status code {response.status_code}")

except Exception as e:

    logging.error(f"An error occurred: {e}")
    app.logger.error(f"An error occurred: {e}")














