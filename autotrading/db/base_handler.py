from abc import ABC, abstractmethod

class DBHandler(ABC):
    """
    DBHanlder는 추상화 클래스로 DB작업에 필요한 메소드를 정의합니다.
    이 클래스를 상속받는 클래스는 @abstractmethod로 정의된 메소드는 반드시 구현해야합니다.
    """
    @abstractmethod
    def insert_items(self):
        pass
        
    @abstractmethod
    def find_items(self):
        pass
        
    @abstractmethod
    def find_item(self):
        pass
   
    @abstractmethod
    def delete_items(self):
        pass
      
    @abstractmethod
    def update_items(self):
        pass
    
    @abstractmethod
    def aggregate(self): 
        pass
