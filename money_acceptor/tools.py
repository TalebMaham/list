import ctypes
import time
from __main__ import app 


class MDBTools:
    def __init__(self, mdb_api):
        self.mdb_api = ctypes.CDLL('src/devices/money_acceptor/mdb/MDB_master.dll')

    def check_result(self, result, operation_name):
        if result == 0:
            print(f"Operation '{operation_name}' failed with result {result}")
            app.logger.error(f"Operation '{operation_name}' failed with result {result}")
            raise Exception(f"Operation '{operation_name}' failed with result {result}")
        else : 
            print(f"Operation '{operation_name}' succed with result {result}")
            app.logger.error(f"Operation '{operation_name}' succed with result {result}")

    def accepter(self, coin_enable_mask):
        while True:
            result = self.mdb_api.MDB_CA_coinType(coin_enable_mask, coin_enable_mask)
            try:
                self.check_result(result, "MDB_CA_coinType")
                break  # Exit loop on success
            except Exception as e:
                print(e)
                time.sleep(2)

    def refuser(self):
        while True:
            result = self.mdb_api.MDB_CA_coinType(0, 0)
            try:
                self.check_result(result, "MDB_CA_coinType")
                break  # Exit loop on success
            except Exception as e:
                print(e)
                time.sleep(2)

    def ecouter(self, events_buffer):
        while True:
            result = self.mdb_api.MDB_CA_poll(events_buffer)
            try:
                self.check_result(result, "MDB_CA_poll")
                return result  # Return on success
            except Exception as e:
                print(e)
                time.sleep(2)

    def rendre_monnaie(self, payout_buffer):
        while True:
            result = self.mdb_api.MDB_CA_PAYOUT(payout_buffer)
            try:
                self.check_result(result, "MDB_CA_PAYOUT")
                return result  # Return on success
            except Exception as e:
                print(e)
                time.sleep(2)

    def mdb_open_comm(self, port_number):
        while True:
            result = self.mdb_api.MDB_openComm(5)
            print(f"Resultat de la commincation est : {result}")
            try:
                self.check_result(result, "MDB_openComm")
                return result  # Return on success
            except Exception as e:
                print(f"Port number  : {port_number} ")
                print(e)
                time.sleep(2)

    def mdb_ca_reset(self):
        while True:
            result = self.mdb_api.MDB_CA_reset()
            try:
                self.check_result(result, "MDB_CA_reset")
                return result  # Return on success
            except Exception as e:
                print(e)
                time.sleep(2)

    def mdb_ca_init(self, buffer_to_send):
        while True:
            result = self.mdb_api.MDB_CA_init(buffer_to_send)
            try:
                self.check_result(result, "MDB_CA_init")
                return result  # Return on success
            except Exception as e:
                print(e)
                time.sleep(2)

    def mdb_ca_setup_scaling_factor(self):
        while True:
            result = self.mdb_api.MDB_CA_SETUP_SCALING_FACTOR(bytes(1))
            try:
                self.check_result(result, "MDB_CA_SETUP_SCALING_FACTOR")
                return result  # Return on success
            except Exception as e:
                print(e)
                time.sleep(2)

    def mdb_ca_tube_status(self, events_buffer):
        while True:
            result = self.mdb_api.MDB_CA_Tube_Status(events_buffer)
            try:
                self.check_result(result, "MDB_CA_Tube_Status")
                return result  # Return on success
            except Exception as e:
                print(e)
                time.sleep(2)
