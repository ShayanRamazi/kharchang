import datetime

from django.contrib.contenttypes.models import ContentType
from django.apps import apps
import requests
import tsetmc.models as models
import re
import ast
import core.utils as ut
import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning


def create_entity_list(entity_dicts_list, arguments_dict, entity_model_name):
    z = ContentType.objects.get(model=entity_model_name.lower())
    EntityModel = apps.get_model(z.app_label, entity_model_name)
    entitys = []
    for entity_dict in entity_dicts_list:
        entitys.append(EntityModel(**entity_dict, **arguments_dict))
    return entitys


def find_previous_record_of_row(best_limit_data, index, row):
    for i in range(index - 1, -1, -1):
        if best_limit_data[i]['row'] == row:
            return best_limit_data[i]
    return None


def create_historical_buy_best_limits_list(best_limit_data, argument_dict):
    buy_best_limits = []
    for i in range(len(best_limit_data)):
        best_limit_datum = best_limit_data[i]
        time = best_limit_datum['time']
        row = best_limit_datum['row']
        amount = best_limit_datum['buy_amount']
        volume = best_limit_datum['buy_vol']
        price = best_limit_datum['buy_price']
        previous_record_of_row = find_previous_record_of_row(best_limit_data, i, row)
        if not previous_record_of_row or previous_record_of_row['buy_amount'] != amount or previous_record_of_row[
            'buy_vol'] != volume or previous_record_of_row['buy_price'] != price:
            buy_best_limits.append(
                models.BestLimitBuyData(time=time, row=row, amount=amount, volume=volume, price=price, **argument_dict))
    return buy_best_limits


def create_historical_sell_best_limits_list(best_limit_data, argument_dict):
    sell_best_limits = []
    for i in range(len(best_limit_data)):
        best_limit_datum = best_limit_data[i]
        time = best_limit_datum['time']
        row = best_limit_datum['row']
        amount = best_limit_datum['sell_amount']
        volume = best_limit_datum['sell_vol']
        price = best_limit_datum['sell_price']
        previous_record_of_row = find_previous_record_of_row(best_limit_data, i, row)
        if not previous_record_of_row or previous_record_of_row['sell_amount'] != amount or previous_record_of_row[
            'sell_vol'] != volume or previous_record_of_row['sell_price'] != price:
            sell_best_limits.append(
                models.BestLimitSellData(time=time, row=row, amount=amount, volume=volume, price=price,
                                         **argument_dict))
    return sell_best_limits


def getHtml(url):
    try:
        html = requests.get(url, timeout=15)
        html = html.text
        return html
    except:
        print("Something wrong for URL :" + url)
        return 0


def parsHtmlToGetVars(url):
    html = getHtml(url)
    shareHolderDataYesterday = ast.literal_eval(re.findall('ShareHolderDataYesterday=(.*);', html)[0])
    shareHolderData = ast.literal_eval(re.findall('ShareHolderData=(.*);', html)[0])
    intraTradeData = ast.literal_eval(re.findall('IntraTradeData=(.*);', html)[0])
    clientTypeData = ast.literal_eval(re.findall('ClientTypeData=(.*);', html)[0])
    closingPriceData = ast.literal_eval(re.findall('ClosingPriceData=(.*);', html)[0])
    instrumentStateData = ast.literal_eval(re.findall('InstrumentStateData=(.*);', html)[0].replace(" ", ""))
    instSimpleDataStr = str(re.findall('InstSimpleData=.*;', html))
    instSimpleDataStartStr, InstSimpleDataEndStr = instSimpleDataStr.find("["), instSimpleDataStr.find("]")
    instSimpleData = ast.literal_eval(
        instSimpleDataStr[instSimpleDataStartStr + len('["InstSimpleData='):InstSimpleDataEndStr + 1])
    bestLimitDataTemp = re.findall('BestLimitData=(.*)]];', html.replace(" ", ""))
    bestLimitData = []
    if (len(bestLimitDataTemp) > 0):
        bestLimitDataTempStr = bestLimitDataTemp[0]
        bestLimitDataTempStrStrs = bestLimitDataTempStr.replace('[', '').split('],')
        bestLimitData = [tmpStr.replace("'", "").split(",") for tmpStr in bestLimitDataTempStrStrs]
    staticTreshholdData = ast.literal_eval(re.findall('StaticTreshholdData=(.*);', html)[0])
    instrumentId, date = url.split("&i=")[1].split("&d=")
    date = ut.string_to_date(date)
    parsedDataDict = {
        "instrumentId": instrumentId,
        "date": date,
        "ShareHolderDataYesterday": shareHolderDataYesterday,
        "ShareHolderData": shareHolderData,
        "IntraTradeData": intraTradeData,
        "ClientTypeData": clientTypeData,
        "InstrumentPriceData": closingPriceData,
        "InstSimpleData": instSimpleData,
        "BestLimitData": bestLimitData,
        "StaticTreshholdData": staticTreshholdData,
        "InstrumentStateData": instrumentStateData
    }
    return parsedDataDict


def jsonInstrumentStateData(InstrumentStateData):
    InstrumentStateDataJsonList = []
    for i in range(len(InstrumentStateData)):
        InstrumentStateDataJson = {
            "time": time_for_status(InstrumentStateData[i][1]),
            "status": InstrumentStateData[i][2],
        }
        InstrumentStateDataJsonList.append(InstrumentStateDataJson)
    return InstrumentStateDataJsonList


def jsonShareHolderDataYesterday(ShareHolderDataYesterday):
    shareHolderDataYesterdayJsonList = []
    for i in range(len(ShareHolderDataYesterday)):
        shareHolderDataYesterdayJson = {
            "name": ShareHolderDataYesterday[i][5],
            "isinShareHolder": ShareHolderDataYesterday[i][1],
            "percentage": ShareHolderDataYesterday[i][3],
            "amountOfShares": ShareHolderDataYesterday[i][2]
        }
        shareHolderDataYesterdayJsonList.append(shareHolderDataYesterdayJson)
    return shareHolderDataYesterdayJsonList


def jsonShareHolderData(shareHolderData):
    shareHolderDataJsonList = []
    for i in range(len(shareHolderData)):
        shareHolderDataJson = {
            "name": shareHolderData[i][5],
            "isinShareHolder": shareHolderData[i][1],
            "percentage": shareHolderData[i][3],
            "amountOfShares": shareHolderData[i][2]
        }
        shareHolderDataJsonList.append(shareHolderDataJson)
    return shareHolderDataJsonList


def jsonIntraTradeData(intraTradeData):
    intraTradeDataJsonList = []
    for i in range(len(intraTradeData)):
        intraTradeDataJson = {
            "time": ut.string_to_time_with_separator(intraTradeData[i][1]),
            "amount": intraTradeData[i][2],
            "price": intraTradeData[i][3],
            "canceled": intraTradeData[i][4]
        }
        intraTradeDataJsonList.append(intraTradeDataJson)
    return intraTradeDataJsonList


def jsonClientTypeData(clientTypeData):
    clientTypeJsonList = []
    if (len(clientTypeData) > 0):
        clientTypeData = [clientTypeData]
    for i in range(len(clientTypeData)):
        clientTypeDataJson = {
            "numberBuyReal": clientTypeData[i][0],
            "volumeBuyReal": clientTypeData[i][4],
            "valueBuyReal": clientTypeData[i][12],
            "priceBuyReal": clientTypeData[i][16],
            "numberBuyLegal": clientTypeData[i][1],
            "volumeBuyLegal": clientTypeData[i][6],
            "valueBuyLegal": clientTypeData[i][13],
            "priceBuyLegal": clientTypeData[i][17],
            "numberSellReal": clientTypeData[i][2],
            "volumeSellReal": clientTypeData[i][8],
            "valueSellReal": clientTypeData[i][14],
            "priceSellReal": clientTypeData[i][18],
            "numberSellLegal": clientTypeData[i][3],
            "volumeSellLegal": clientTypeData[i][10],
            "valueSellLegal": clientTypeData[i][15],
            "priceSellLegal": clientTypeData[i][19],
            "changeLegalToReal": clientTypeData[i][20]
        }
        clientTypeJsonList.append(clientTypeDataJson)
    return clientTypeJsonList


def jsonClosingPriceData(closingPriceData):
    closingPriceDataJsonList = []
    for i in range(len(closingPriceData)):
        closingPriceDataJson = {
            "time": ut.string_to_time_and_date(closingPriceData[i][0])[1],
            "lastTradePrice": closingPriceData[i][2],
            "lastPrice": closingPriceData[i][3],
            "firstPrice": closingPriceData[i][4],
            "yesterdayPrice": closingPriceData[i][5],
            "maxPrice": closingPriceData[i][6],
            "minPrice": closingPriceData[i][7],
            "numberOfTransactions": closingPriceData[i][8],
            "turnover": closingPriceData[i][9],
            "valueOfTransactions": closingPriceData[i][10],
            "status": closingPriceData[i][11]
        }
        closingPriceDataJsonList.append(closingPriceDataJson)
    return closingPriceDataJsonList


def jsonBestLimitData(bestLimitData):
    bestLimitDataJsonList = []
    for i in range(len(bestLimitData)):
        bestLimitDataJson = {
            "time": ut.string_to_time_with_out_separator(bestLimitData[i][0]),
            "row": bestLimitData[i][1],
            "buy_amount": bestLimitData[i][2],
            "buy_vol": bestLimitData[i][3],
            "buy_price": bestLimitData[i][4],
            "sell_price": bestLimitData[i][5],
            "sell_vol": bestLimitData[i][6],
            "sell_amount": bestLimitData[i][7],
        }
        bestLimitDataJsonList.append(bestLimitDataJson)
    return bestLimitDataJsonList


def jsonStaticTreshholdData(staticTreshholdData, instrumentPriceData, instSimpleData):
    jsonStaticTreshholdData = {
        "maxAllowed": staticTreshholdData[-1][-2],
        "minAllowed": staticTreshholdData[-1][-1],
        "baseVolume": instSimpleData[9],
        "numberOfShares": instSimpleData[8],
        "yesterdayPrice": instrumentPriceData[0][3]
    }
    return jsonStaticTreshholdData


def getJson(url):
    parsedDataDict = parsHtmlToGetVars(url)
    jsonHistory = {
        "InstrumentStateData": jsonInstrumentStateData(parsedDataDict["InstrumentStateData"]),
        "ShareHolderYesterdayData": jsonShareHolderDataYesterday(parsedDataDict["ShareHolderDataYesterday"]),
        "ShareHolderData": jsonShareHolderData(parsedDataDict["ShareHolderData"]),
        "IntraTradeData": jsonIntraTradeData(parsedDataDict["IntraTradeData"]),
        "ClientTypeData": jsonClientTypeData(parsedDataDict["ClientTypeData"]),
        "InstrumentPriceData": jsonClosingPriceData(parsedDataDict["InstrumentPriceData"]),
        "BestLimits": jsonBestLimitData(parsedDataDict["BestLimitData"]),
        "StaticTreshholdData": jsonStaticTreshholdData(parsedDataDict["StaticTreshholdData"],
                                                       parsedDataDict["InstrumentPriceData"],
                                                       parsedDataDict["InstSimpleData"]),
        "instrumentId": parsedDataDict["instrumentId"],
        "date": parsedDataDict["date"]
    }
    return jsonHistory


def time_for_status(time):
    if (time == 1):
        return datetime.time(6, 0, 0)
    else:
        return ut.string_to_time_with_out_separator(time)


def get_instrument_id_list_from_tsetmc():
    resp = requests.get("http://www.tsetmc.com/tsev2/data/MarketWatchPlus.aspx?h=0&r=0")
    parts = resp.text.split("@")
    instrumentIds = [x.split(",")[0] for x in parts[2].split(";")]
    return instrumentIds


def get_instrument_dates_to_crawl(instrumentId):
    urllib3.disable_warnings(InsecureRequestWarning)
    #  A=0 gets dates where the instrument trade volume is greater than zero and A=1 returns all dates
    res = requests.get(
        'https://members.tsetmc.com/tsev2/data/InstTradeHistory.aspx?i=' + str(instrumentId) + '&Top=999999&A=0',
        verify=False)
    date_list = [ut.string_to_date(res.text.split(";")[i][0:8]) for i in range(len(res.text.split(";")) - 1)]
    return date_list
