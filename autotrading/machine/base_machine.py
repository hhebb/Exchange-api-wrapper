from abc import ABC, abstractmethod

class Machine(ABC):
    @abstractmethod
    def get_filled_orders(self):
        """체결정보를 얻어오기 위한 메소드입니다.
        """
        pass

    @abstractmethod
    def get_ticker(self):
        """마지막 체결정보(Tick)을 얻기 위한 메소드입니다.
        """
        pass

    @abstractmethod
    def get_wallet_status(self):
        """사용자의 지갑정보를 조회하는 메소드입니다.
        """
        pass

    @abstractmethod
    def get_token(self):
        """액세스토큰 정보를 받기 위한 메소드입니다.
        """
        pass

    @abstractmethod
    def set_token(self):
        """액세스토큰 정보를 만들기 위한 메소드입니다.
        """
        pass

    @abstractmethod
    def get_username(self):
        """현재 사용자 이름을 받기 위한 메소드입니다.
        """
        pass

    @abstractmethod
    def buy_order(self):
        """매수 주문을 실행하는 메소드입니다. 
        """
        pass

    @abstractmethod
    def sell_order(self):
        """매도 주문을 실행하는 메소드입니다.
        """
        pass

    @abstractmethod
    def cancel_order(self):
        """취소 주문을 실행하는 메소드입니다.
        """
        pass

    @abstractmethod
    def get_my_order_status(self):
        """사용자의 주문정보 상세정보를 조회하는 메소드입니다. 
        """
        pass
