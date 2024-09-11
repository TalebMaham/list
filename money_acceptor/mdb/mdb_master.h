/**
 * mdb_master.h 
 *
 * @copyright
 * 					 
 * Copyright by
 *    Symotronic se
 *    Parc Republique
 *    75 Rue Francis de Pressense
 *	  69100 VILLEURBANNE
 *    FRANCE
 *    +33 (0)4 72 43 00 55
 *    info@symotronic.com
 *
 * The copyright to the computer program(s) herein is the property of
 * Symotronic se, France.
 * The program(s) may be used and/or copied only with the written
 * permission of Symotronic or in accordance
 * with the terms and conditions stipulated in the agreement/contract
 * under which the program(s) have been supplied.
 * 
 * @version   2.0.0.0
 * 				 
 * @brief
 *
 * Header file for mdb_master API interface.
 * 
 * Purpose of the mdb_master API is to connect arbitrary payment devices mdb
 * to the OS Windows platform. 
 * 
 * @details
 * 
 * General:
 * 
 * @author St�phane MENARD
 * 				 
 */
#include "stdafx.h"

#define MDBMASTER_EXPORTS 1

#ifdef MDB_API_EXPORTS
#define MDB_API __declspec(dllexport) 
#else
#define MDB_API __declspec(dllimport) 
#endif

#ifndef MDBMASTER_EXPORTS
typedef char* (*PFNGETDLLINFO)(void);
#else
MDB_API char* GetDllInfo(void);
#endif


#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNOPENCOM)(UINT8 portNum);
#else
	MDB_API BOOL MDB_openComm(UINT8 portNum);
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNCLOSECOM)();
#else
	MDB_API BOOL MDB_closeComm();
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBCAINIT)(BYTE coinTypeCredit[]);
#else
	MDB_API BOOL MDB_CA_init(BYTE coinTypeCredit[]);
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBCACOINTYPE)(UINT16  coinEnable, UINT16 CoinDispense);
#else
	MDB_API BOOL MDB_CA_coinType(UINT16  coinEnable, UINT16 CoinDispense);
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBCAPOLL)(BYTE events[]);
#else
	MDB_API BOOL MDB_CA_poll(BYTE events[]);
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBCARESET)();
#else
	MDB_API BOOL MDB_CA_reset();
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBCADISPENSE)(UINT8 coinDispense, UINT8 coinQuantity);
#else
	MDB_API BOOL MDB_CA_Dispense(UINT8 coinDispense, UINT8 coinQuantity);
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBCATUBESTATUS)(BYTE coinstatus[]);
#else
	MDB_API BOOL MDB_CA_Tube_Status(BYTE coinstatus[]);
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBCAPAYOUT)(BYTE payout[]);
#else
	MDB_API BOOL MDB_CA_PAYOUT(BYTE payout[]);
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBCAPAYOUTSTATUS)(BYTE status[]);
#else
	MDB_API BOOL MDB_CA_PAYOUT_Status(BYTE status[]);
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBCAVALUEPOLL)(BYTE Changer_Payout_Activity[]);
#else
	MDB_API BOOL MDB_CA_VALUE_POLL(BYTE Changer_Payout_Activity[]);
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBCASETUPLEVEL)(BYTE level[]);
#else
	MDB_API BOOL MDB_CA_SETUP_LEVEL(BYTE level[]);
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBCASETUPCCODE)(BYTE countryCode[]);
#else
	MDB_API BOOL MDB_CA_SETUP_CCODE(BYTE countryCode[]);
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBCASETUPSCALINGFACTOR)(BYTE ScalingFactor[]);
#else
	MDB_API BOOL MDB_CA_SETUP_SCALING_FACTOR(BYTE ScalingFactor[]);
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBCASETUPDECIMALPOINT)(BYTE decimalPlace[]);
#else
	MDB_API BOOL MDB_CA_SETUP_DECIMAL_POINT(BYTE decimalPlace[]);
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBCASETUPCOINTYPEROUTING)(BYTE coinTypeRouting[]);
#else
	MDB_API BOOL MDB_CA_SETUP_COIN_TYPEROUTING(BYTE coinTypeRouting[]);
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBCAIDENTIFICATION_MANUFCODE)(BYTE coinTypeRouting[]);
#else
	MDB_API BOOL MDB_CA_IDENTIFICATION_manufacturerCode(BYTE manufacturerCode[]);
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBCAIDENTIFICATION_SERIALNUMBER)(BYTE serialNumber[]);
#else
	MDB_API BOOL MDB_CA_IDENTIFICATION_serialNumber(BYTE serialNumber[]);
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBCAIDENTIFICATION_MODELTUNREVISION)(BYTE modelTuningRevision[]);
#else
	MDB_API BOOL MDB_CA_IDENTIFICATION_modelTuningRevision(BYTE modelTuningRevision[]);
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBCAIDENTIFICATION_SOFTWAREREVISION)(BYTE softwareVersion[]);
#else
	MDB_API BOOL MDB_CA_IDENTIFICATION_softwareVersion(BYTE softwareVersion[]);
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBCAIDENTIFICATION_OPTIONFEATURES)(BYTE optionalFeatures[]);
#else
	MDB_API BOOL MDB_CA_IDENTIFICATION_optionalFeatures(BYTE optionalFeatures[]);
#endif



#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBBVINIT)(BYTE billTypeCredit[]);
#else
	MDB_API BOOL MDB_BV_init(BYTE billTypeCredit[]);
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBBVRESET)();
#else
	MDB_API BOOL MDB_BV_reset();
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBBVPOLL)(BYTE events[]);
#else
	MDB_API BOOL MDB_BV_poll(BYTE events[]);
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBBVESCROW)(BOOL stack);
#else
	MDB_API BOOL MDB_BV_escrow(BOOL stack);
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBBVBILLTYPE)(UINT16 enable, UINT16 escrow);
#else
	MDB_API BOOL MDB_BV_billType(UINT16 enable, UINT16 escrow);
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBBVSTACKER)(BOOL* full, UINT16* nBillInStack);
#else
	MDB_API BOOL MDB_BV_stacker(BOOL* full, UINT16* nBillInStack);
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBBVSETUPLEVEL)(BYTE level[]);
#else
	MDB_API BOOL MDB_BV_SETUP_LEVEL(BYTE level[]);
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBBVSETUPCCODE)(BYTE countryCode[]);
#else
	MDB_API BOOL MDB_BV_SETUP_CCODE(BYTE countryCode[]);
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBBVSETUPSCALINGFACTOR)(BYTE billScalingFactor[]);
#else
	MDB_API BOOL MDB_BV_SETUP_SCALING_FACTOR(BYTE billScalingFactor[]);
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBBVSETUPDECIMALPOINT)(BYTE decimalPlace[]);
#else
	MDB_API BOOL MDB_BV_SETUP_DECIMAL_POINT(BYTE decimalPlace[]);
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBBVSETUPBILLSTACKERCAPACITY)(BYTE stackerCapacity[]);
#else
	MDB_API BOOL MDB_BV_SETUP_BILL_STACKERCAPACITY(BYTE stackerCapacity[]);
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBBVSETUPBILLESCROW)(BYTE escrow[]);
#else
	MDB_API BOOL MDB_BV_SETUP_BILL_ESCROW(BYTE escrow[]);
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBBVSETUPBILLTYPECREDIT)(BYTE billSecurityLevels[]);
#else
	MDB_API BOOL MDB_BV_SETUP_BILL_TYPECREDIT(BYTE billSecurityLevels[]);
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBBVIDENTIFICATION_MANUFCODE)(BYTE manufacturerCode[]);
#else
	MDB_API BOOL MDB_BV_IDENTIFICATION_manufacturerCode(BYTE manufacturerCode[]);
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBBVIDENTIFICATION_SERIALNUMBER)(BYTE serialNumber[]);
#else
	MDB_API BOOL MDB_BV_IDENTIFICATION_serialNumber(BYTE serialNumber[]);
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBBVIDENTIFICATION_MODELTUNREVISION)(BYTE modelTuningRevision[]);
#else
	MDB_API BOOL MDB_BV_IDENTIFICATION_modelTuningRevision(BYTE modelTuningRevision[]);
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBBVIDENTIFICATION_SOFTVERSION)(BYTE softwareVersion[]);
#else
	MDB_API BOOL MDB_BV_IDENTIFICATION_softwareVersion(BYTE softwareVersion[]);
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBBVIDENTIFICATION_OPTFEATURES)(BYTE optionalFeatures[]);
#else
	MDB_API BOOL MDB_BV_IDENTIFICATION_optionalFeatures(BYTE optionalFeatures[]);
#endif


//Cashless #1 Function
#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBCASHLESSBEGIN)();
#else
	MDB_API BOOL MDB_CASHLESS_BEGIN();
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBCASHLESSEND)();
#else
	MDB_API BOOL MDB_CASHLESS_END();
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBCASHLESSRESET)();
#else
	MDB_API BOOL MDB_CASHLESS_RESET();
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBCASHLESSREVALUE)(BYTE Amount[]);
#else
	MDB_API BOOL MDB_CASHLESS_REVALUE(BYTE Amount[]);
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBCASHLESSPOLL)(BYTE events[]);
#else
	MDB_API BOOL MDB_CASHLESS_poll(BYTE events[]);
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBCASHLESSVEND)(BYTE itemPrice[], BYTE itemNumber[]);
#else
	MDB_API BOOL MDB_CASHLESS_VEND(BYTE itemPrice[], BYTE itemNumber[]);
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBCASHLESSVENDCANCEL)();
#else
	MDB_API BOOL MDB_CASHLESS_VEND_CANCEL();
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBCASHLESSVENDSUCCESS)(BYTE itemNumber[]);
#else
	MDB_API BOOL MDB_CASHLESS_VEND_SUCCESS(BYTE itemNumber[]);
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBCASHLESSVENDFAILURE)();
#else
	MDB_API BOOL MDB_CASHLESS_VEND_FAILURE();
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBCASHLESSSESSIONCOMPLETE)();
#else
	MDB_API BOOL MDB_CASHLESS_SESSION_COMPLETE();
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBCASHLESSENABLE)(BOOL enable);
#else
	MDB_API BOOL MDB_CASHLESS_ENABLE(BOOL enable);
#endif
//MDB_API BOOL MDB_CASHLESS_ENABLE(BOOL enable, int NumCashless);

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBCASHLESSSETUPLEVEL)(BYTE level[]);
#else
	MDB_API BOOL MDB_CASHLESS_SETUP_LEVEL(BYTE level[]);
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBCASHLESSSETUPCCODE)(BYTE countryCode[]);
#else
	MDB_API BOOL MDB_CASHLESS_SETUP_CCODE(BYTE countryCode[]);
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBCASHLESSSETUPSCALINGFACTOR)(BYTE ScalingFactor[]);
#else
	MDB_API BOOL MDB_CASHLESS_SETUP_SCALING_FACTOR(BYTE ScalingFactor[]);
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBCASHLESSSETUPDECIMALPOINT)(BYTE decimalPlace[]);
#else
	MDB_API BOOL MDB_CASHLESS_SETUP_DECIMAL_POINT(BYTE decimalPlace[]);
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBCASHLESSIDENTIFICATION_SERIALNUMBER)(BYTE serialNumber[]);
#else
	MDB_API BOOL MDB_CASHLESS_IDENTIFICATION_serialNumber(BYTE serialNumber[]);
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBCASHLESSIDENTIFICATION_MANUFCODE)(BYTE manufacturerCode[]);
#else
	MDB_API BOOL MDB_CASHLESS_IDENTIFICATION_manufacturerCode(BYTE manufacturerCode[]);
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBCASHLESSIDENTIFICATION_MODELNUMBER)(BYTE modelNumber[]);
#else
	MDB_API BOOL MDB_CASHLESS_IDENTIFICATION_modelNumber(BYTE modelNumber[]);
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBCASHLESSIDENTIFICATION_SOFTWAREREVISION)(BYTE softwareVersion[]);
#else
	MDB_API BOOL MDB_CASHLESS_IDENTIFICATION_softwareVersion(BYTE softwareVersion[]);
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBCASHLESSIDENTIFICATION_OPTIONFEATURES)(BYTE optionalFeatures[]);
#else
	MDB_API BOOL MDB_CASHLESS_IDENTIFICATION_optionalFeatures(BYTE optionalFeatures[]);
#endif




//Cashless #2 Function
#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBCASHLESS2BEGIN)();
#else
	MDB_API BOOL MDB_CASHLESS2_BEGIN();
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBCASHLESS2END)();
#else
	MDB_API BOOL MDB_CASHLESS2_END();
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBCASHLESS2RESET)();
#else
	MDB_API BOOL MDB_CASHLESS2_RESET();
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBCASHLESS2REVALUE)(BYTE Amount[]);
#else
	MDB_API BOOL MDB_CASHLESS2_REVALUE(BYTE Amount[]);
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBCASHLESS2POLL)(BYTE events[]);
#else
	MDB_API BOOL MDB_CASHLESS2_poll(BYTE events[]);
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBCASHLESS2VEND)(BYTE itemPrice[], BYTE itemNumber[]);
#else
	MDB_API BOOL MDB_CASHLESS2_VEND(BYTE itemPrice[], BYTE itemNumber[]);
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBCASHLESS2VENDCANCEL)();
#else
	MDB_API BOOL MDB_CASHLESS2_VEND_CANCEL();
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBCASHLESS2VENDSUCCESS)(BYTE itemNumber[]);
#else
	MDB_API BOOL MDB_CASHLESS2_VEND_SUCCESS(BYTE itemNumber[]);
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBCASHLESS2VENDFAILURE)();
#else
	MDB_API BOOL MDB_CASHLESS2_VEND_FAILURE();
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBCASHLESS2SESSIONCOMPLETE)();
#else
	MDB_API BOOL MDB_CASHLESS2_SESSION_COMPLETE();
#endif

#ifndef MDBMASTER_EXPORTS
	typedef bool(*PFNMDBCASHLESS2ENABLE)(BOOL enable);
#else
	MDB_API BOOL MDB_CASHLESS2_ENABLE(BOOL enable);
#endif



#ifndef MDBMASTER_EXPORTS
typedef const unsigned long(*PFNGETFIRMWAREVERSION)(unsigned char* version);
#else
	MDB_API const unsigned long  getFirmwareVersion(unsigned char* version);
#endif

	/** \file symo_mdb.h
 * \brief API pour le MDB
 *
 * Les �tats MDB sont les suivants:
 * INACTIF, DESACTIVE, ACTIVE, SESSION, VENTE, REEVALUATION, VENTE NEGATIVE.\n
 * Le bo�tier a le comportement d'un lecteur de carte sans contact sur le bus MDB.
 *
 * \date 04.09.2014 Cr�ation de la documentation et renseignement pour le RS232
*/


/**
 *\fn unsigned long __stdcall OpenCOMSB(int gCOM)
 *\brief Ouvre le port s�rie, puis communique.
 * Si une session est ouverte, une vente ou une r��valuation en cours
 *  le boitier dis � la VMS qu'il se r�initialise.
 *
 *\param gCOM num�ro du port s�rie
 *
 *\return
 *	1000 succ�s\n
 *	1001 impossible d'ouvrir le port s�rie\n
 *	1002 impossible d'�mettre ou pas de r�ponse du bo�tier\n
 *	1003 MDB �tats INACTIF, DESACTIVE
*/
	MDB_API unsigned long  OpenCOMSB(int gCOM);

	/**
	 *\fn unsigned long __stdcall CloseCOMSB()
	 *\brief Informe le bo�tier de la fin de la communication et ferme le port s�rie.
	 *
	 *\return
	 *	2000 succ�s\n
	 *	2001 impossible d'�mettre sur le port s�rie\n
	 *	2002 pas de r�ponse du bo�tier\n
	 *	2003 MDB �tats VENTE, REEVALUATION\n
	 *           Il faut valider ou non la vente, effectuer un GetVendInfo pour valider la r��valuation.
	*/
	MDB_API unsigned long CloseCOMSB();

	/**
	 *\fn unsigned long __stdcall ResetSB()
	 *\brief R�initialisation de la communication MDB avec la VMC.
	 *
	 *\return
	 *	3000 succ�s\n
	 *	3001 impossible d'�mettre sur le port s�rie\n
	 *	3002 pas de r�ponse du bo�tier\n
	 *	3003 MDB �tat diff�rent de ACTIVE cad la VMC n'a pas compl�tement
	 *       initialis� le lecteur
	 *
	*/
	MDB_API unsigned long  ResetSB();

	/**
	 *\fn unsigned long __stdcall ReevEnable()
	 *\brief Autorisation de la r��valuation.
	 *
	 *\return
	 *	10000 succ�s\n
	 *	10001 impossible d'�mettre sur le port s�rie\n
	 *	10002 pas de r�ponse du bo�tier
	*/
	MDB_API unsigned long  ReevEnable();

	/**
	 *\fn unsigned long __stdcall ReevDisable()
	 *\brief Interdiction de la r��valuation.
	 *
	 *\return
	 *	11000 succ�s\n
	 *	11001 impossible d'�mettre sur le port s�rie\n
	 *	11002 pas de r�ponse du bo�tier
	*/
	MDB_API unsigned long  ReevDisable();

	/**
	 *\fn unsigned long __stdcall HotStart()
	 *\brief R�d�marrage du microcontr�leur et du contr�leur ethernet.
	 * Lors du d�marrage, le boitier informe la VMC (sur le bus MDB) de sa r�initialisation ce qui entra�ne une
	 * nouvelle s�quence d'initialisation MDB Cashless.
	 *
	 *\return
	 *	12000 succ�s\n
	 *	12001 impossible d'�mettre sur le port s�rie\n
	 *	12002 pas de r�ponse du bo�tier
	 */
	MDB_API unsigned long  HotStart();

	/**
	 *\fn char* __stdcall ScanSB()
	 *\brief Non impl�ment�.
	 *
	 *\return une cha�ne
	 * l'ID sur 4 octets\n
	 * "12001" impossible d'�mettre sur le port s�rie\n
	 * "12002" pas de r�ponse du bo�tier\n
	 * "12003" pas de carte
	 */
	MDB_API char* ScanSB();

	/**
	 *\fn unsigned long __stdcall SendEpurse(int ePurse)
	 *\brief Ouverture d'une session avec le montant fourni en param�tre.
	 *
	 *\param ePurse montant
	 *
	 *\return
	 * 5000 succ�s\n
	 * 5001 impossible d'�mettre sur le port s�rie\n
	 * 5002 pas de r�ponse du bo�tier\n
	 * 5003 MDB �tat diff�rent de ACTIF\n
	 * 5004 erreur de communication
	 */
	MDB_API unsigned long  SendEpurse(int ePurse);

	/**
	 *\fn char* __stdcall GetVendInfo()
	 *\brief Interrogation du bo�tier sur l'�tat de la session.
	 *
	 *\return une cha�ne
	 * "6000" succ�s\n
	 * "6001" impossible d'�mettre sur le port s�rie\n
	 * "6002" pas de r�ponse du bo�tier\n
	 * "6003" MDB �tat SESSION\n
	 * "6004" la vente a �t� annul�e\n
	 * "V x y" demande de vente pour la s�lection x et le prix y\n
	 * "R x" une r��valuation d'un montant x a �t� faite
	 */
	MDB_API char* GetVendInfo();

	/**
	 *\fn unsigned long __stdcall ConfirmVend(int vState)
	 *\brief Acceptation ou refus de la vente.
	 *
	 *\param vState 0: confirmer 1: annuler
	 *\return
	 * 7000 succ�s\n
	 * 7001 impossible d'�mettre sur le port s�rie\n
	 * 7002 pas de r�ponse du bo�tier\n
	 * 7003 MDB �tat diff�rent de VENTE
	 */
	MDB_API unsigned long  ConfirmVend(int vState);

	/**
	 *\fn char* __stdcall GetVMCconfig()
	 *\brief Interrogation du bo�tier sur l'�tat de la session.
	 *
	 *\return une cha�ne
	 *  "x y" x niveau MDB et y nombre de caract�res de l'afficheur\n
	 * "8001" impossible d'�mettre sur le port s�rie\n
	 * "8002" pas de r�ponse du bo�tier\n
	 * "8003" MDB �tat INACTIF
	 */
	MDB_API char* GetVMCconfig();

	/**
	 *\fn unsigned long __stdcall sendVMCDISPLAY(int dTime, char *Message)
	 *\brief Affichage d'un message.
	 *
	 *\param dTime dur�e de l'affichage
	 *\param Message le message
	 *\return
	 * 9000 succ�s\n
	 * 9001 impossible d'�mettre sur le port s�rie\n
	 * 9002 pas de r�ponse du bo�tier\n
	 * 9003 erreur de communication\n
	 * 9004 message trop long
	 */
	MDB_API unsigned long  sendVMCDISPLAY(int dTime, char* Message);

	/**
	 *\fn const unsigned long __stdcall getFirmwareVersion(unsigned char *version)
	 *\brief Renvoie la version du logiciel du bo�tier.\n
	 * Format M.m.r\n
	 * M: majeure\n
	 * m: mineure\n
	 * r: r�vision\n
	 *
	 *\param version tableau d'au moins 3 octets
	 *
	 *\return
	 * 16000 succ�s\n
	 * 16001 impossible d'�mettre sur le port s�rie\n
	 * 16002 pas de r�ponse du bo�tier
	 */
	//MDB_API const unsigned long  getFirmwareVersion(unsigned char* version);

	MDB_API unsigned long DeliveryState(void);

	MDB_API unsigned long  MaxRevalueAmount(int MaxAmount);

