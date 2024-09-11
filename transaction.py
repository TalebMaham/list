from decimal import Decimal
import json
import os
import sys
import time
import copy

import pika

import pika
import requests
from requests.auth import HTTPBasicAuth
from src.devices.money_acceptor.cashier import cashier

from src.api.machine_user import machine_user
from src.sales.customer.customer_class import customer

from src.api.machine_user import machine_user
from src.devices.ingenico_apt.ingenico_class import ingenicoAPT  # To uncomment
from src.machine.distributor.distributor import Distributor
# from ..rabbitmq_queue.rsa_keys.rsa_decrypt import rsa_key_manager
# from ..rabbitmq_queue.rsa_keys.rsa_decrypt import rsa_key_manager
from src.common.singleton_decorator import singleton
from src.machine.locker.locker import Locker
from src.api.stock.locker_and_distributor import *
from src.sales.transaction.cart import Cart
from src.messaging.rabbitmq_queue.rabbitmq_sender_class import RabbitMQSender
from src.devices.ticket_printer.ticket_generation import ticket_generation
from src.sales.transaction.stock_sorter.menu_discount_regular_calculations import get_homepage_for_module
from src.sales.transaction.apis.ThreadingHttpRequest import *
from src.sales.transaction.TransactionFeedbackFormatter import *
from collections import Counter
from src.staff.StockPatcher import StockPatcher
from src.messaging.rabbitmq_queue.lift_data_scheduled import thread_options_module_manager
import threading
import datetime
from datetime import datetime, timedelta
from src.sales.transaction.real_time_dispensation.distributor import real_time_distributor_dispensation_handle
from src.sales.transaction.real_time_dispensation.utils import functions as real_time_dispensation_utils

from src.api.stock.prefix_machine import PrefixMachine
from src.staff.delivery.delivery import delivery
from src.machine.MachineRelations import machine_relations

from src.machine.distributor.actions.DistributorLight import distributor_light_manager
from src.devices.ingenico_apt.scheduled_apt_class import thread_apt_status
from flask import current_app, jsonify

from __main__ import app
from dotenv import load_dotenv

load_dotenv(dotenv_path=app.config['DOT_ENV_PATH'])


@singleton
class Transaction:

    def __init__(self):
        self.cart = None
        self.locker = None
        self.stock_raw = None
        self.distributor = None
        self.stock_clean = None
        self.ticket_printer = None
        self.is_ready_for_dispensation = False
        self.record_process_status = {"is_running": False, "is_finished": True}
        self.thread_record = None
        self.product_class = None
        self.locale = 'fr_FR'
        self.is_dispensed = False

        self.card_type = None
        self.is_already_finished_one_time = False
        self.timestamp_first_finish = None
        self.mapping_name_list_before_recalculation = []

        self.distributor_light_status = False
        self.timestamp_last_send_elevator_go_down = None
        self.data_money_acceptor = {}
        self.is_coin_already_enabled = False

    def get_product_sorted_homepage_front(self, can_sell_with_age_limit=False):
        app.logger.error(f"REQUEST FOR HOMEPAGE SUMMARY")
        thread_apt_status.Pause()
        # USED FOR REOPEN LOCKERS
        threading.Thread(target=delivery.machine_grid_stock.set_stock)
        start_time = time.time()
        api_values = ThreadingHttpRequest()
        api_values.run()
        print('DUREE APPEL API')
        print(time.time() - start_time)
        start_time = time.time()

        prefix_machine_formatter = PrefixMachine()
        # get raw stock (lockers + distributors)
        self.stock_raw = prefix_machine_formatter.add_missing_infos_to_stock(api_values.stock_raw_api)

        if api_values.is_lock_dlc:
            print('LOCK DLC IS ACTIVATED')
            self.stock_raw = copy.deepcopy(self.stock_raw)

            for elem in self.stock_raw['distributors'] + self.stock_raw['lockers']:
                for product in elem['grid']:
                    if len(product['product']['dlcs']) == 0:
                        continue
                    product['product']['dlcs'] = sorted(
                        copy.deepcopy(product['product']['dlcs']),
                        key=lambda x: x["dlc"]
                    )

            for elem in self.stock_raw['distributors'] + self.stock_raw['lockers']:
                for product in elem['grid']:
                    if len(product['product']['dlcs']) == 0:
                        continue

                    dlc_product = datetime.strptime(
                        product['product']['dlcs'][0]['dlc'],
                        "%Y-%m-%d"
                    )

                    dlc_product = dlc_product.replace(
                        day=dlc_product.day,
                        month=dlc_product.month,
                        year=dlc_product.year,
                        hour=23,
                        minute=59,
                        second=59,
                        microsecond=0
                    )
                    if datetime.now() > dlc_product:
                        for dlc in product['product']['dlcs']:
                            dlc['count'] = 0

            for elem in api_values.stock_raw_api[0]['distributors'] + api_values.stock_raw_api[0]['lockers']:
                for product in elem['grid']:
                    if len(product['product']['dlcs']) == 0:
                        continue
                    product['product']['dlcs'] = sorted(
                        copy.deepcopy(product['product']['dlcs']),
                        key=lambda x: x["dlc"]
                    )

            for elem in api_values.stock_raw_api[0]['distributors'] + api_values.stock_raw_api[0]['lockers']:
                for product in elem['grid']:
                    if len(product['product']['dlcs']) == 0:
                        continue

                    dlc_product = datetime.strptime(
                        product['product']['dlcs'][0]['dlc'],
                        "%Y-%m-%d"
                    )

                    dlc_product = dlc_product.replace(
                        day=dlc_product.day,
                        month=dlc_product.month,
                        year=dlc_product.year,
                        hour=23,
                        minute=59,
                        second=59,
                        microsecond=0
                    )
                    if datetime.now() > dlc_product:
                        for dlc in product['product']['dlcs']:
                            dlc['count'] = 0

        self.card_type = None

        # self.stock_raw = api_values.stock_raw_api
        # get this stock formatted like fridge (for homepage sorting)
        self.stock_clean = get_stock_locker_and_distributor_formatted_like_fridge(stock_raw=self.stock_raw)
        # hydrate distributor class to easily get wanted data
        self.distributor = Distributor(self.stock_raw)
        # # hydrate distributor class to easily get wanted data
        self.locker = Locker(self.stock_raw)
        # # Create fresh new empty cart
        self.cart = Cart(
            self.stock_raw,
            self.stock_clean,
            api_values.product_class,
            api_values.discount
        )
        self.is_dispensed = False
        self.product_class = copy.deepcopy(api_values.product_class)

        # Reset Ticket printer
        self.ticket_printer = None
        # Reset flag dispensation
        self.is_ready_for_dispensation = False
        # Return stock sorted to front_end
        self.is_already_finished_one_time = False
        self.timestamp_first_finish = None
        self.mapping_name_list_before_recalculation = []

        cashier.total_inserted_amount = 0 
        self.is_coin_already_enabled = False

        homepage = get_homepage_for_module(
            api_values.product_class,
            api_values.discount,
            api_values.stock_raw_api,
            can_sell_with_age_limit
        )

        print('DUREE CALCULS')
        print(time.time() - start_time)

        return homepage

    def cart_update(self, list_dict_mapping, wanted_type='add'):
        def extract_mappings(list_dict_mapping):
            if 'locations' in list_dict_mapping:
                mapping_json = json.loads(list_dict_mapping['locations'])
                mappings = []
                for mapping in mapping_json:
                    for _ in range(mapping['count']):
                        mappings.append(str(mapping['name']))
                return mappings
            return ''

        self.is_ready_for_dispensation = False
        if wanted_type == 'add':
            mappings = extract_mappings(list_dict_mapping)
            ticket_front_build = None
            for mapping in mappings:
                ticket_front_build = self.cart.add_product(mapping_name=mapping)  # TICKET FRONT
            ticket_front = ticket_front_build
            return ticket_front
        elif wanted_type == 'remove':
            mappings = extract_mappings(list_dict_mapping)
            ticket_front_build = None
            for mapping in mappings:
                ticket_front_build = self.cart.remove_product(mapping_name=mapping)  # TICKET FRONT
            ticket_front = ticket_front_build
            return ticket_front
        elif wanted_type == 'remove_all':
            self.cart.mapping_name_list = []
            return True

    def decrement_machines_stock(self):
        # AIM: UPDATE STOCK COUNT
        print('DECREMENTS STOCK')
        stock_patcher = StockPatcher()
        stock_patcher.patch_stock_with_mappings(
            mappings=self.cart.mapping_name_list,
            stock_raw=self.cart.stock_raw
        )

    def save_transaction(
            self,
            amount=0,
            card_type='VISA',
            payment_method='CC',
            pan="0000########0000",
            private_number_customer_card='',
    ):
        print('TICKET BACK')
        transaction_feedback_formatter = TransactionFeedbackFormatter(
            self.cart.ticket_back,
            self.product_class
        )
        feedback_api = transaction_feedback_formatter.format()
        print(json.dumps(feedback_api, indent=4))

        have_discount = False
        discount_amount = 0
        if len(feedback_api['discounts']) > 0 or len(feedback_api['menus']) > 0:
            have_discount = True
            discount_amount = abs(feedback_api['recap']['discount_amount'])

        private_number_customer_card, customer_id, card_type, payment_method = '', '', 'VISA', 'CC'
        print(f'THIS IS CUSTOMER : {customer.id}')
        print(f'THIS IS PRIVATE_NUMBER_CARD : {customer.private_number_card}')
        customer_id = customer.id
        if customer.id is not None and customer.id != '':
            private_number_customer_card = str(customer.private_number_card)
            payment_method, card_type = 'CP', 'CP'

        if private_number_customer_card != '':
            pan = private_number_customer_card

        if customer_id is None or customer_id == '':
            # CUSTOMER WITH CREDIT CARD
            print(json.dumps([{
                "products": feedback_api['products'],
                "total": str(round(float(feedback_api['recap']['ttc']), 2)),
                "tva": str(round(float(feedback_api['recap']['total_tva_price']), 2)),
                "client_id": os.environ.get('CLIENT_ID'),
                "machine_id": os.environ.get('MACHINE_ID'),
                "have_discount": have_discount,
                "discount_amount": discount_amount,
                "paiement_method": payment_method,
                "acceptation_date": time.time(),
                "contact_less_card": True,
                "card_type": ingenicoAPT.cardInstance.GetCardType(),
                "max_auth": feedback_api['recap']['ttc'],
                # "contact_less_card": str(ingenicoAPT.cardInstance.GetIsContactLess()),
                # "card_type": str(ingenicoAPT.cardInstance.GetCardType()),
                "sale_ok": True,
                "pan": ingenicoAPT.GetPan(),
                "id_private_card": private_number_customer_card,
                "id_app_mobile": "",
                "menus": feedback_api['menus'],
                "discounts": feedback_api['discounts'],
                "participation": self.cart.get_participation_employer_total_amount()
            }]))

            if self.card_type == 'MONEY_ACCEPTOR':
                card_type = 'CASH'
                pan = '9999########9999'
            else:
                card_type = ingenicoAPT.cardInstance.GetCardType()
                pan = ingenicoAPT.GetPan()

            rabbitmq_sender = RabbitMQSender()
            rabbitmq_sender.SendSale(value=json.dumps(
                [{
                    "products": feedback_api['products'],
                    "total": str(round(float(feedback_api['recap']['ttc']), 2)),
                    "tva": str(round(float(feedback_api['recap']['total_tva_price']), 2)),
                    "client_id": os.environ.get('CLIENT_ID'),
                    "machine_id": os.environ.get('MACHINE_ID'),
                    "have_discount": have_discount,
                    "discount_amount": discount_amount,
                    "paiement_method": payment_method,
                    "acceptation_date": time.time(),
                    "contact_less_card": True,
                    "card_type": card_type,
                    "max_auth": feedback_api['recap']['ttc'],
                    # "contact_less_card": str(ingenicoAPT.cardInstance.GetIsContactLess()),
                    # "card_type": str(ingenicoAPT.cardInstance.GetCardType()),
                    "sale_ok": True,
                    "pan": pan,
                    "id_private_card": private_number_customer_card,
                    "id_app_mobile": "",
                    "menus": feedback_api['menus'],
                    "discounts": feedback_api['discounts'],
                    "participation": self.cart.get_participation_employer_total_amount()
                }],
                ensure_ascii=False)
            )
            rabbitmq_sender.Disconnect()
        else:
            # CUSTOMER WITH PRIVATIVE CARD

            print(f'this is customer id stored {customer_id}')

            print(json.dumps([{
                "products": feedback_api['products'],
                "total": str(round(float(feedback_api['recap']['ttc']), 2)),
                "tva": str(round(float(feedback_api['recap']['total_tva_price']), 2)),
                "client_id": os.environ.get('CLIENT_ID'),
                "machine_id": os.environ.get('MACHINE_ID'),
                "have_discount": have_discount,
                "discount_amount": discount_amount,
                "paiement_method": payment_method,
                "acceptation_date": time.time(),
                "contact_less_card": True,
                "card_type": 'CP',
                "max_auth": feedback_api['recap']['ttc'],
                # "contact_less_card": str(ingenicoAPT.cardInstance.GetIsContactLess()),
                # "card_type": str(ingenicoAPT.cardInstance.GetCardType()),
                "sale_ok": True,
                "pan": pan,
                "id_private_card": private_number_customer_card,
                "id_machine_user": customer_id,
                "id_app_mobile": "",
                "menus": feedback_api['menus'],
                "discounts": feedback_api['discounts'],
                "participation": self.cart.get_participation_employer_total_amount()
            }]))

            rabbitmq_sender = RabbitMQSender()
            rabbitmq_sender.SendSale(value=json.dumps(
                [{
                    "products": feedback_api['products'],
                    "total": str(round(float(feedback_api['recap']['ttc']), 2)),
                    "tva": str(round(float(feedback_api['recap']['total_tva_price']), 2)),
                    "client_id": os.environ.get('CLIENT_ID'),
                    "machine_id": os.environ.get('MACHINE_ID'),
                    "have_discount": have_discount,
                    "discount_amount": discount_amount,
                    "paiement_method": payment_method,
                    "acceptation_date": time.time(),
                    "contact_less_card": True,
                    "card_type": 'CP',
                    "max_auth": feedback_api['recap']['ttc'],
                    # "contact_less_card": str(ingenicoAPT.cardInstance.GetIsContactLess()),
                    # "card_type": str(ingenicoAPT.cardInstance.GetCardType()),
                    "sale_ok": True,
                    "pan": pan,
                    "id_private_card": private_number_customer_card,
                    "id_machine_user": customer_id,
                    "id_app_mobile": "",
                    "menus": feedback_api['menus'],
                    "discounts": feedback_api['discounts'],
                    "participation": self.cart.get_participation_employer_total_amount()
                }],
                ensure_ascii=False)
            )
            rabbitmq_sender.Disconnect()

    def _thread_record(self, total_price, card):

        if card != 'free':
            time.sleep(7)
            print(f'TOTAL PRICE TO RECORD  : {total_price}')
            print('1. RECORD PROCESS')
            try:
                ingenicoAPT.Record(amount=total_price)
            except Exception as e:
                print('ERROR IN RECORD TRANSACTION APT')
                print(e)
            app.logger.error(f'RECORD RESPONSE RECEIVED')

            time.sleep(2)

            if ingenicoAPT.GetPan() == "########":
                app.logger.error(f'PAN IS ######## -> RETRY TO RECORD THE SALE')
                timeout = time.time() + 30
                while True:
                    if time.time() > timeout or \
                            ingenicoAPT.GetPan() != "########":
                        break
                    print('WAIT FOR TPA OK')
                    time.sleep(15)
                    print('RETRY RECORD')
                    print(f'TOTAL PRICE TO RECORD  : {total_price}')
                    print('1. RECORD PROCESS')
                    try:
                        ingenicoAPT.Record(amount=total_price)
                    except Exception as e:
                        print('ERROR IN RECORD TRANSACTION APT')
                        print(e)

        print('2. TRANSACTION API SAVING PROCESS')
        app.logger.error(f'TRANSACTION API SAVING PROCESS')
        try:
            self.save_transaction(
                card_type='VISA',
                payment_method='CC',
                pan="0000########0000",
                private_number_customer_card='',
            )
        except Exception as e:
            print('ERROR IN RECORD TRANSACTION TO API')
            app.logger.error(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(e)

        return None

    def is_solvency_accepted(self, solvency, total_price) -> bool:
        if solvency is None:
            return False

        if isinstance(solvency, bool):
            # ingenicoAPT.Record(amount=0)
            return False

        if 'card' in solvency:
            if solvency['card'] in ("delivery", "maintenance"):
                return False

            if solvency['card'] == 'tpa':
                return False

        if 'isAccepted' in solvency:
            if solvency['isAccepted'] is False:
                # ingenicoAPT.Record(amount=0)
                return False

        if 'isAccepted' not in solvency:
            return False

        if 'card' in solvency:
            if solvency['card'] == 'free':
                self.card_type = 'free'

            if solvency['card'] == 'privative_card':
                if solvency['badge_uid'] is None:
                    return False
                customer.Reset_Customer()
                customer.Hydrate(machine_user.get_user_with_card_id(solvency['badge_uid']))
                if customer.credit < total_price:
                    # CUSTOMER HAS NOT ENOUGH CREDIT
                    return False

                if customer.id is not None:
                    try:
                        app.logger.info('CONVIVE ID IDENTIFIE : ')
                        app.logger.info(customer.id)
                        app.logger.info("INFOS CONVIVE: ")
                        app.logger.info(customer.get_object_camel_case())
                    except Exception as e:
                        print(e)
                self.card_type = 'privative_card'
            else:
                self.card_type = 'credit_card'

            # FROM HERE, TRANSACTION IS ACCEPTED
            self.is_ready_for_dispensation = True
            return True

    def Pay(self, locale='fr_FR'):
        self.locale = locale
        # Reset customer values
        customer.Reset_Customer()

        # Wait for the terminal to be available
        start_wait_time = time.time()
        while ingenicoAPT.isInUse:
            time.sleep(1)
            app.logger.error("APT IS IN USE")
            print("APT IS IN USE")
            if time.time() >= start_wait_time + 15:
                app.logger.error("APT IS FREE BY TIMEOUT")
                print("APT IS FREE BY TIMEOUT")
                break

        app.logger.error('PAYMENT PROCESS IN PROGRESS')
        total_price = self.cart.get_total_price()
        solvency = ingenicoAPT.Debit(
            amount=total_price
        )

        #solvency = {"isAccepted": True, "card": "free"}
        app.logger.error('DEBIT RESPONSE RECEIVED')

        try:
            app.logger.error(f'DEBIT RESPONSE CONTAINS : {solvency}')
        except Exception as e:
            app.logger.error(f'DEBIT RESPONSE ERROR : {e}')
            print(e)

        if (
                solvency is None or
                isinstance(solvency, bool) or
                solvency.get('card', '') == 'tpa'
        ):
            for _ in range(1, 3):
                time.sleep(3)
                solvency = ingenicoAPT.Debit(
                    amount=total_price
                )
                if (
                        solvency is not None and
                        not isinstance(solvency, bool) and
                        solvency.get('card', '') != 'tpa'
                ):
                    break

        return self.is_solvency_accepted(solvency, total_price)

    def __get_product_only(self, mapping_name, all_machine_data):

        if 'distributors' in all_machine_data:
            for distributor in all_machine_data['distributors']:
                if 'grid' in distributor:
                    for product in distributor['grid']:
                        if "mapping" in product and str(product['mapping']) == str(mapping_name):
                            return product

        if 'lockers' in all_machine_data:
            for locker in all_machine_data['lockers']:
                if 'grid' in locker:
                    for product in locker['grid']:
                        if "mapping" in product and str(product['mapping']) == str(mapping_name):
                            return product

    def get_distribution_real_time_status(self):
        list_mapping_status = (
                self.distributor.dispensation.get_dispensation_real_time_status()
                + self.locker.dispensation.get_dispensation_real_time_status()
        )

        app.logger.error("list_mapping_status")
        app.logger.error(list_mapping_status)

        list_mapping = self.mapping_name_list_before_recalculation
        stock_raw_copy = copy.deepcopy(self.stock_raw)
        list_products = []

        for mapping in list_mapping:
            product = self.__get_product_only(mapping, stock_raw_copy)
            list_products.append(
                {
                    "id": product['product']['product']['id'],
                    "name": product['product']['product']['name'],
                    "photo": product['product']['product']['photo'],
                    "mapping": mapping
                }
            )

        # {
        #     "A": ["A1", "A2"],
        #     "C": ["C1"],
        #     "D": ["D1"],
        #     "E": ["E1"]
        # }
        result_unique_machine_orders = real_time_dispensation_utils.regroup_mapping_by_machine_order(
            list_mapping=list_mapping
        )

        machine_real_time_status = []
        for machine_order in result_unique_machine_orders:
            list_of_mapping_for_this_machine_order = result_unique_machine_orders[machine_order]

            filtered_mapping_status = real_time_dispensation_utils.filter_by_machine_order(
                list_mapping_status=list_mapping_status,
                machine_order=machine_order
            )

            filtered_list_products = real_time_dispensation_utils.filter_products_by_machine_order(
                list_products=list_products,
                machine_order=machine_order
            )

            app.logger.error(machine_order)
            app.logger.error(list_of_mapping_for_this_machine_order)
            app.logger.error(filtered_mapping_status)

            result = real_time_distributor_dispensation_handle(
                list_of_mapping_for_this_machine_order,
                filtered_mapping_status,
                filtered_list_products
            )

            app.logger.error(result)
            products_list = []
            for elem in result:
                if elem == "isFinished" or elem == "isLiftDown":
                    continue

                products_list.append(
                    result[elem]['products']
                )

            machine_real_time_status.append({
                "order": machine_order,
                "type": machine_relations.get_machine_type_with_order(
                    order=machine_order
                ),
                "products": products_list,
                "isFinished": result['isFinished'],
                "isLiftDown": result['isLiftDown'],
            })

        # Check if there is at least one product "WAIT_FOR_PICKUP"
        # To ask the elevator to do down
        is_at_least_one_wait_for_pickup = False
        for mapping_ordered in list_mapping_status:
            if mapping_ordered['status'] == "WAIT_FOR_PICKUP":
                is_at_least_one_wait_for_pickup = True


        # if is_at_least_one_wait_for_pickup:
        #     if self.timestamp_last_send_elevator_go_down is None:
        #         self.timestamp_last_send_elevator_go_down = time.time()
        #         self.distributor.dispensation.send_elevator_go_down(
        #             distributor_address=0
        #         )
        #     elif time.time() >= self.timestamp_last_send_elevator_go_down + 3:
        #         self.timestamp_last_send_elevator_go_down = time.time()
        #         self.distributor.dispensation.send_elevator_go_down(
        #             distributor_address=0
        #         )

        is_total_finished, is_lift_down = True, False
        for machine in machine_real_time_status:
            if not machine["isFinished"]:
                is_total_finished = False
            if machine["isLiftDown"]:
                is_lift_down = True

            is_dispensation_started = False
            for product in machine['products']:
                if product['quantityDelivered'] > 0:
                    is_dispensation_started = True

            # # TODO : put this in distributor class
            # # Light blinking
            # if (
            #         machine["isLiftDown"] and
            #         is_dispensation_started and
            #         machine.get('type', '') == 'DISTRIBUTOR'
            # ):
            #     if self.distributor_light_status and not is_total_finished:
            #         self.distributor_light_status = False
            #         distributor_light_manager.set_light(
            #             wanted_state='off',
            #             distributor_address=machine_relations.get_machine_address_with_order(
            #                 order=machine['order']
            #             )
            #         )
            #     else:
            #         self.distributor_light_status = True
            #         distributor_light_manager.set_light(
            #             wanted_state='on',
            #             distributor_address=machine_relations.get_machine_address_with_order(
            #                 order=machine['order']
            #             )
            #         )
            # elif machine.get('type', '') == 'DISTRIBUTOR':
            #     self.distributor_light_status = True
            #     distributor_light_manager.set_light(
            #         wanted_state='on',
            #         distributor_address=machine_relations.get_machine_address_with_order(
            #             order=machine['order']
            #         )
            #     )


        # Pop unwanted dictionnary attributes
        for machine in machine_real_time_status:
            try:
                del machine['isFinished']
                del machine['isLiftDown']
            except Exception as e:
                print(e)

        return {
            "machines": machine_real_time_status,
            "isFinished": is_total_finished,
            "isLiftDown": is_lift_down,
        }

    def __thread_dispensation(self):

        self.distributor.dispensation.dispensation_real_time_status.reset()
        self.locker.dispensation.dispensation_real_time_status.reset()

        self.mapping_name_list_before_recalculation = copy.deepcopy(
            self.cart.mapping_name_list
        )

        self.locker.dispensation.add_product_in_real_time_dispensation(
            stock_raw=self.stock_raw,
            mappings=self.cart.mapping_name_list,
            wanted_to_shut_off_light=False
        )

        print('DISTRIBUTOR DISPENSATION')
        try:
            self.distributor.dispensation.dispense_distributor_products(
                stock_raw=self.stock_raw,
                mappings=self.cart.mapping_name_list
            )
        except Exception as e:
            print(e)
            app.logger.error(e)

        print('LOCKER DISPENSATION')
        try:
            self.locker.open_door(
                input_type="products",
                stock_raw=self.stock_raw,
                mappings=self.cart.mapping_name_list,
                wanted_to_shut_off_light=True
            )
        except Exception as e:
            print(e)
            app.logger.error(e)


    def get_mapping_well_dispensed(self):
        list_mapping_status = (
                self.distributor.dispensation.get_dispensation_real_time_status()
                + self.locker.dispensation.get_dispensation_real_time_status()
        )

        picked_up_mappings = []
        for mapping in list_mapping_status:
            if mapping['status'] == 'PICKED_UP':
                picked_up_mappings.append(mapping['mapping'])

        return picked_up_mappings

    def thread_record_after_dispensation(self):
        if self.card_type is None:
            thread_apt_status.Resume()
            return

        total_price = self.cart.get_total_price()

        if self.card_type == 'privative_card':
            # GET OLD CREDIT
            customer_credit_before_purchase = customer.get_credit()
            # CALCULATE NEW CREDIT
            credit = round(float(customer_credit_before_purchase - total_price), 2)
            # UPDATE CREDIT
            machine_user.set_credit_to_user(customer.id, credit)
            # CALCULATE NEW FIDELITY POINTS
            fidelity_points = int(round(float(customer.fidelity_point) + float(total_price) * 0.054 * 100, 2))
            # UPDATE FIDELITY POINTS
            machine_user.set_fidelity_points_to_user(customer.id, fidelity_points)

            print('3. DECREMENT STOCK API PROCESS')
            app.logger.error(f'DECREMENT STOCK API PROCESS')
            try:
                self.decrement_machines_stock()
            except Exception as e:
                print(e)
                print('ERROR IN DECREMENT MACHINE STOCK')

            print('2. TRANSACTION API SAVING PROCESS')
            print(customer.private_number_card)
            app.logger.error(f'TRANSACTION API SAVING PROCESS')
            try:
                self.save_transaction(
                    card_type='CP',
                    payment_method='CP',
                    pan=customer.private_number_card,
                    private_number_customer_card=customer.private_number_card,
                )
            except Exception as e:
                print('ERROR IN RECORD TRANSACTION TO API')
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                print(e)

            try:
                ingenicoAPT.set_banking_ticket_to_remove_client_ticket()
            except Exception as e:
                print(e)
                app.logger.error(e)

            time.sleep(3.5)

            thread_apt_status.Resume()
            return True

        app.logger.error(f'DECREMENT STOCK API PROCESS')
        try:
            self.decrement_machines_stock()
        except Exception as e:
            app.logger.error(f'ERROR IN DECREMENT MACHINE STOCK')

        app.logger.error(f'RECORD PROCESS...')
        try:
            app.logger.error(f'TOTAL PRICE TO RECORD  : {total_price}')
        except Exception as e:
            print(e)

        if self.card_type == 'MONEY_ACCEPTOR':
            # Retour monnaie 
            app.logger.error(f'RENDU MONNAIE')
            print("Appel de ticket_cash ...")
            to_pay = self.cart.get_total_price()
            montant_a_rendre = 0
            app.logger.error(f'TO PAY {to_pay}')
            app.logger.error(f'INSERE {cashier.montant_insere}')
            if to_pay  <= cashier.montant_insere :
                montant_a_rendre = Decimal(cashier.montant_insere) - Decimal(to_pay)
                cashier.payout(montant_a_rendre)
        else:
            # Payment through APT/TPE
            app.logger.error(f'PAIEMENT TPA')
            try:
                ingenicoAPT.Record(amount=total_price)
            except Exception as e:
                print('ERROR IN RECORD TRANSACTION APT')
                print(e)
            app.logger.error(f'RECORD RESPONSE RECEIVED')

            time.sleep(2)

            # Retry record when response is not ok
            if ingenicoAPT.GetPan() == "########":
                app.logger.error(f'PAN IS ######## -> RETRY TO RECORD THE SALE')
                timeout = time.time() + 30
                while True:
                    if time.time() > timeout or \
                            ingenicoAPT.GetPan() != "########":
                        break
                    print('WAIT FOR TPA OK')
                    time.sleep(15)
                    print('RETRY RECORD')
                    print(f'TOTAL PRICE TO RECORD  : {total_price}')
                    print('1. RECORD PROCESS')
                    try:
                        ingenicoAPT.Record(amount=total_price)
                    except Exception as e:
                        print('ERROR IN RECORD TRANSACTION APT')
                        print(e)

        app.logger.error(f'TRANSACTION API SAVING PROCESS')
        try:
            self.save_transaction(
                card_type='VISA',
                payment_method='CC',
                pan="0000########0000",
                private_number_customer_card='',
            )
        except Exception as e:
            app.logger.error(f'ERROR TRANSACTION API SAVING PROCESS')
            app.logger.error(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(e)


        try:
            ingenicoAPT.set_banking_ticket_to_remove_client_ticket()
        except Exception as e:
            print(e)
            app.logger.error(e)

        time.sleep(3.5)

        thread_apt_status.Resume()
        return None

    def dispense_products(self):
        print(self.cart.mapping_name_list)
        if not self.is_dispensed:
            self.is_dispensed = True
            threading.Thread(
                target=self.__thread_dispensation,
                args=()
            ).start()
            time.sleep(0.6)

        real_time_status = self.get_distribution_real_time_status()
        app.logger.error('AVANT LE PROCESSUS DE RENDU')
        if real_time_status['isFinished'] and not self.is_already_finished_one_time:
            app.logger.error('ENTREE DANS LE PROCESSUS DE RENDU')
            self.timestamp_first_finish = time.time()
            self.is_already_finished_one_time = True

            mappings_well_dispensed = self.get_mapping_well_dispensed()
            self.cart.mapping_name_list = mappings_well_dispensed
            self.cart.update_ticket()
            try:
                threading.Thread(
                    target=ticket_generation.generate_ticket_html_and_pdf,
                    args=(
                        None,
                        None,
                        self.cart.ticket_back,
                        self.locale,
                        current_app._get_current_object()
                    )
                    # productMismatch = None,
                    # msg_mismatch = None,
                    # ticket_back = self.cart.ticket_back,
                    # locale = self.locale
                ).start()
            except Exception as e:
                print(e)
                app.logger.error(e)

            app.logger.error('RECORD THE SALE')
            self.thread_record = threading.Thread(
                target=self.thread_record_after_dispensation,
                args=()
            )
            self.thread_record.start()

        if self.is_already_finished_one_time:
            if (
                    (time.time() <= self.timestamp_first_finish + 10 and
                     (
                             ticket_generation.printing_status.status != 'FINISHED' or
                             time.time() <= ticket_generation.printing_status.timestamp + 20
                     )
                    ) or
                    self.thread_record.is_alive()
            ):
                real_time_status['isFinished'] = False
        return real_time_status

    def reopen_locker_door(self, locker_mapping_name: list):
        purchased_products = self.cart.stock_clean
        # List of {
        #       "type": "distributor",
        #       "product": product,
        #       "position": (product['x_position'], product['y_position']),
        #       "address": distributor['address']
        # }

        # Find the product formatted associated with the mapping name
        # Open the locker door when find
        lockers_to_reopen = []
        for mapping in locker_mapping_name:
            for product in purchased_products:
                if product['mapping'] == mapping:
                    try:
                        self.locker.open_door(
                            input_type='products',
                            product_stock=list(product)
                        )
                    except Exception as e:
                        print(e)
        time.sleep(0.25)
        return 'true'

    def print_ticket_paper(self):
        return ticket_generation.print_ticket(mode='paper')  # bool

    def print_ticket_email(self, email=None):
        return ticket_generation.print_ticket(mode='email', email=email)
   
    def ticket_cash(self):
        is_finished = not cashier.compting
        paid = cashier.get_total_inserted_amount()
        to_pay = cashier.total
        change = round(paid - to_pay, 2) if paid >= to_pay else 0

        data = {
            "is_finished": is_finished,
            "paid": paid,
            "to_pay": to_pay,
            "change": change,
            "has_enough_coins" : True
        }

        return jsonify(data)


    def ticket_cash_give_back(self):
        inserted_amount = cashier.get_total_inserted_amount()
        give_back = Decimal(inserted_amount)
        if cashier.payout_change(give_back):
            cashier.init_total_inserted_amount()
            return jsonify(True)
        return jsonify(False)


transaction = Transaction()


# class RabbitMQReceiver:
#     def __init__(self):
#
#         self.connection = pika.BlockingConnection(
#             pika.ConnectionParameters(
#                 str(os.environ['RABBITMQ_ADDR']),
#                 int(os.environ['RABBITMQ_PORT']),
#                 '/',
#                 pika.PlainCredentials(
#                     str(os.environ['RABBITMQ_USERNAME']),
#                     str(os.environ['RABBITMQ_PASSWORD'])
#                 )
#             )
#         )
#         self.channel = self.connection.channel()
#         self.CreateNewQueue(f'machine_{int(os.environ.get("MACHINE_ID"))}_notifications')
#
#
#     def __callback_queue_machine_qrcode(self, ch, method, properties, body):
#         # CALLED WHEN QRCODE NOTIFICATION IS RECEIVED
#         print('CALLBACK')
#         decoded_message = rsa_key_manager.decrypt_rsa_message(body)
#         print(decoded_message)
#         json_message = json.loads(decoded_message)
#         if 'id_machine' in json_message and 'id_machine_user' in json_message:
#             customer_object = machine_user.get_customer_with_id(json_message['id_machine_user'])
#             customer.Hydrate(customer_object)
#             qrcode_manager.hydrate(customer_object)
#             qrcode_manager.timestamp_last_received_message = time.time()
#
#
#     def thread_consume_qrcode_queue(self):
#         # START CONSUMING QRCODE QUEUE IN THREAD
#         while int(os.environ.get('MACHINE_ID')) is None:
#             time.sleep(0.5)
#         print(f'machine_{int(os.environ.get("MACHINE_ID"))}_notifications')
#         while True:
#             try:
#                 if not self.channel.is_open:
#
#                     print('QRCODE : RabbitMQ QUEUE UNREACHABLE -> Program Tries to reconnect')
#
#                     self.connection = pika.BlockingConnection(
#                         pika.ConnectionParameters(
#                             str(os.environ['RABBITMQ_ADDR']),
#                             int(os.environ['RABBITMQ_PORT']),
#                             '/',
#                             pika.PlainCredentials(
#                                 str(os.environ['RABBITMQ_USERNAME']),
#                                 str(os.environ['RABBITMQ_PASSWORD'])
#                             )
#                         )
#                     )
#                     self.channel = self.connection.channel()
#
#                 self.channel.basic_consume(
#                     queue=f'machine_{int(os.environ.get("MACHINE_ID"))}_notifications',
#                     auto_ack=True,
#                     on_message_callback=self.__callback_queue_machine_qrcode
#                 )
#                 self.channel.start_consuming()
#             except Exception as e:
#                 print(e)
#
#     def start_to_consume_qrcode_notifications(self):
#         # RUN THREAD TO CONSUME QRCODE
#         t = threading.Thread(target=self.thread_consume_qrcode_queue)
#         t.start()
#         # CHANGE THIS TODO
#         print('START QRCODE CONSUMING')
#
#     def CreateNewQueue(self, QueueName=''):
#         self.channel.queue_declare(QueueName, durable=True)
#
#     def Disconnect(self):
#         self.connection.close()
#
# qr_code_receiver = RabbitMQReceiver()
# qr_code_receiver.start_to_consume_qrcode_notifications()
#
# @singleton
# class QRcodeManager:
#     def __init__(self):
#         self.machine_user = None
#         self.timestamp_last_received_message = None
#
#     def hydrate(self, machine_user):
#         self.machine_user = machine_user
#
#     def is_qr_code_scanned(self):
#         return self.machine_user is not None
#
#     def get_customer_id(self):
#         return self.machine_user['id']
#
#     def get_customer_credit(self):
#         return self.machine_user['credit']
#
#     def thread_qr_code_process(self):
#         ingenicoAPT.Abort()
#         time.sleep(2)
#         timeout = time.time() + 10
#         while not transaction.is_transaction_ended:
#             if time.time() >= timeout:
#                 print('[ QRCODE ] TIMEOUT WAITING FOR TRANSACTION END\n')
#                 return json.dumps({})
#             time.sleep(1)
#         time.sleep(0.5)
#         transaction.qr_code_process()
#
#
#     def check_qr_code_identification(self, request=None):
#         # AVOID SIMULTANEOUS TRANSACTION PROCESS
#         if transaction.accepted_card_timestamp is not None and time.time() - transaction.accepted_card_timestamp < 15:
#             return json.dumps({})
#         # AVOID OPEN MACHINE DOOR IF FRONT-END IS DOWN AND THEN UP
#         if self.timestamp_last_received_message is not None and self.timestamp_last_received_message + 30 <= time.time():
#             return json.dumps({})
#
#         if self.machine_user is None:
#             return json.dumps({})
#
#         machine_user_response = json.dumps({
#             "customer": {
#                 "firstName": self.machine_user['first_name'],
#                 "lastName": self.machine_user['last_name'],
#             }
#         })
#
#         self.machine_user = None
#         threading.Thread(target=self.thread_qr_code_process).start()
#         return machine_user_response
#
# qrcode_manager = QRcodeManager()
