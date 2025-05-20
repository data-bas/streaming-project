from src.coinbase_producer.coinbase_producer import CoinbaseProducer


if __name__ == "__main__":
    symbol = "BTC-USD"
    coin_base_producer = CoinbaseProducer([symbol])
    coin_base_producer.run()

