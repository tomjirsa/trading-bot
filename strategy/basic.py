from database.sqlite import Database
import pandas as pd
from matplotlib import pyplot
from statsmodels.formula.api import ols  as ols
import sys


class BasicStrategy:
    def __init__(self, database_name):
        self.conn = Database(database_name)

    def getData(self, table_name, timewindow):
        """
        Get data from database to analyse
        :param table_name: name of the datasource table
        :param timewindow: timewindow in hours
        :return: Dataframe with data with timestamp set as index
        """
        data_to_analyse = self.conn.getDataNHoursBack(table_name, timewindow)
        if not data_to_analyse:
            print("No data to analyse: ", data_to_analyse)
            return []
        serie = pd.DataFrame(data_to_analyse)
        serie.set_index("timestamp", inplace=True)
        return serie

    def drawPlot(self, data, figure_number):
        data.plot(subplots=True)
        pyplot.figure(figure_number)
        pyplot.show()

    def getFutureTrend(self, table_name, config):
        trend_definition = config["trend_definition"]
        weights = config["weights_total"]
        trends = {
            "short_trend": self.getTotalTrend(table_name, trend_definition["short"], config["weights_partial"]),
            "mid_trend": self.getTotalTrend(table_name, trend_definition["mid"], config["weights_partial"]),
            "long_trend": self.getTotalTrend(table_name, trend_definition["long"], config["weights_partial"])
        }
        sum_of_trends = 0
        for trend in trends:
            sum_of_trends += weights[trend] * trends[trend]

        result_trend = 0
        if sum_of_trends > 0 :
            result_trend = 1
        else:
            result_trend = -1

        return result_trend

    def getPartialTrend(self, table_name, time_window):
        """
        Computes trend
        :param table_name: name of the datasource table
        :param timewindow: timewindow in hours
        :return:
        """
        # Get data
        serie = self.getData(table_name, time_window)
        #self.drawPlot(serie, 1)

        # Create counter
        base_index = "counter"
        serie[base_index] = range(0, len(serie.index))


        # Do regression
        models = {}
        for column in serie.columns.values:
            if column != base_index:
                try:
                    models[column] = ols(formula=column + " ~ counter", data=serie).fit()
                except Exception as e:
                    print("Cannot create OLS model: ", e)
                    raise

        # Process results
        result = {}
        for model in models:
            result[model] = 1 if models[model].params[base_index] > 0 else -1
        return result

    def getTotalTrend(self, table_name, time_window, weights):
        partial_trend = self.getPartialTrend(table_name,time_window)
        sum_of_trends = 0
        for trend in partial_trend:
            sum_of_trends += weights[trend] * partial_trend[trend]

        result_trend = 0
        if sum_of_trends > 0 :
            result_trend = 1
        else:
            result_trend = -1

        return result_trend


