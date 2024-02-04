import datetime
from app.db.database import session
from sqlalchemy import update, select, inspect
from fastapi import HTTPException
from starlette.status import HTTP_404_NOT_FOUND

class Common():  
  @classmethod
  def all(self, **kwargs):    
    query = select(self)
    
    return session.execute(query).scalars().all()

  @classmethod
  def create(self, **kwargs):
    query = self(**kwargs)
    session.add(query)
    session.commit()
    session.refresh(query)

    return query
  
  @classmethod
  def find_or_create(self, **kwargs):
    query = self.find_by(**kwargs)
    
    if query:
      return query
    else:
      return self.create(**kwargs)
    
  @classmethod
  def find(self, id):
    query = select(self).where(self.id == id)
    
    return session.execute(query).scalars().first()
  
  @classmethod
  def find_with_error(self, id):
    query = select(self).where(self.id == id)
    record = session.execute(query).scalars().first()

    if record == None: raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"{self.__name__} not found")   
    
    return record 
  
  @classmethod
  def find_by(self, **kwargs):
    return session.query(self).filter_by(**kwargs).first()

  @classmethod
  def where(self, **kwargs):
    return session.query(self).filter_by(**kwargs).all()    
  
  def update_attributes(self, **kwargs):
    for key, value in kwargs.items():
      if hasattr(self, key):
        setattr(self, key, value)

    self.updated_at = datetime.datetime.now()
            
    query = update(self.__class__).where(self.__class__.id == self.id).values(self.to_dict()).execution_options(synchronize_session="fetch")
    session.execute(query)
    session.commit()  

    return self
  
  def delete(self):
    session.delete(self)
    session.commit()

  def excludes(self, keys):
    dict = self.to_dict()    
    [dict.pop(key) for key in keys]
      
    return dict
  
  def only(self, keys):    
    dict = self.to_dict()

    for key in list(dict.keys()):
      if key not in keys:
        dict.pop(key)
      
    return dict
  
  def to_dict(self):
    return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }