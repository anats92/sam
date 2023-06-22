from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework import status, views
from rest_framework.response import Response
import requests
from datetime import datetime, timedelta, time
from django.core.cache import cache


class HealthCheck(views.APIView):
    def get(self, request, *args, **kwargs):
        return Response(status=status.HTTP_200_OK, data="Alive!")


total_cost_val = 0

GLOBAL_QUOTE = 'Global Quote'


class QuoteView(views.APIView):
    query_cost = 0.1

    @staticmethod
    def get_quote_response(data):
        return {
            'symbol': data[GLOBAL_QUOTE]['01. symbol'],
            'update_time': data[GLOBAL_QUOTE]['07. latest trading day'],
            'price': data[GLOBAL_QUOTE]['05. price'],
            'change_percent': data[GLOBAL_QUOTE]['10. change percent'],
        }

    def get(self, request, *args, **kwargs):
        symbol = kwargs['symbol']
        now = datetime.now()

        # get the key from the cache
        if cached_data := cache.get(symbol):
            update_time = cached_data['update_time']
            start_trade = time(10, 0)
            end_trade = time(17, 0)
            between_trade_hours = start_trade <= now.time() <= end_trade

            if between_trade_hours:
                freshness_threshold = timedelta(minutes=10) if float(
                    cached_data[GLOBAL_QUOTE]['03. high']) > 1.03 or float(
                    cached_data[GLOBAL_QUOTE]['04. low']) > 1.03 else timedelta(minutes=20)
            else:
                freshness_threshold = timedelta(hours=1)

            # return the data from the cache in case that it's fresh
            if now - update_time <= freshness_threshold:
                return Response(data=self.get_quote_response(cached_data), status=status.HTTP_200_OK)

        # access the alphavantage api and update the total cost
        api_url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&apikey=Y2R9RKOESRRHSO10&symbol={symbol}'
        global total_cost_val
        total_cost_val += self.query_cost
        response = requests.get(api_url)

        # if the response is valid - save in the cache and return to the user the relevant keys
        if response.status_code == 200:
            data = response.json()

            # add an update_time key to the json to check freshness in the next APIs calls
            data["update_time"] = now
            cache.set(symbol, data)

            quote_data = self.get_quote_response(data)
            return Response(data=quote_data, status=status.HTTP_200_OK)
        else:
            return Response(data=f"Failed to access the alphavantage data for {symbol=}", status=response.status_code)


class QuoteViewRateLimits(QuoteView):
    """
    Rate limits API with the same logic but with a limitation of 10 requests per ip per minute
    currently is returning 'permission denied' error
    """
    @method_decorator(ratelimit(key='ip', rate='10/m'))
    def get(self, request, *args, **kwargs):
        if getattr(request, 'limited', False):
            return Response(status=status.HTTP_429_TOO_MANY_REQUESTS)

        return super().get(request, *args, **kwargs)


class TotalCostView(views.APIView):
    def get(self, request, *args, **kwargs):
        return Response(total_cost_val, status=status.HTTP_200_OK)


class ResetCostView(views.APIView):
    def post(self, request, *args, **kwargs):
        global total_cost_val
        total_cost_val = 0
        return Response('The total cost was reset', status=status.HTTP_200_OK)


health_check = HealthCheck.as_view()
quote_data = QuoteView.as_view()
quote_data_with_rate_limits = QuoteViewRateLimits.as_view()
total_cost = TotalCostView.as_view()
reset_cost = ResetCostView.as_view()
