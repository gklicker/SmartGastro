class ProductRepository:
    def __init__(self):
        self.__products = []
        self.__counter = 0

    def add(self, product):
        self.__products.append(product)

    def find_by_id(self, product_id):
        for p in self.__products:
            if p.get_id() == product_id:
                return p
        return None

    def find_by_name(self, name):
        for p in self.__products:
            if p.get_name().lower() == name.lower():
                return p
        return None

    def get_all(self):
        return list(self.__products)

    def exists(self, name):
        return self.find_by_name(name) is not None

    def next_id(self):
        self.__counter += 1
        return self.__counter
