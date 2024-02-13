from sqlalchemy import create_engine,ForeignKey, Column, Integer, String, DateTime, Boolean, Float, Text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists, create_database
from server_script.login_script.local_settings import postgresql as settings

Base = declarative_base()

# class User(Base):
#     '''User Model'''
#     __tablename__ = 'users'
#     id = Column('id',Integer, primary_key=True)
#     username = Column('username',String(25), unique=True, nullable=False )
#     password = Column('password',String(),nullable=False)

#     def __init__(self,id,username,password):
#         self.id = id
#         self.username = username
#         self.password = password
    
#     def __repr__(self):
#         return f"({self.id}) {self.username} {self.password}"

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(25), unique=True, nullable=False)
    password = Column(String(),nullable=False)

def get_engine(user,passwd,host, port, db):
    url = f"postgresql://{user}:{passwd}@{host}:{port}/{db}"
    if not database_exists(url):
        create_database(url)
    engine = create_engine(url, pool_size=50, echo=False)
    try:
        with engine.connect() as connection:
            print("Successfully connected to the database!")
    except Exception as e:
        print(f"An error occurred: {e}")
    return engine


def return_session():
    engine = get_engine(settings['pguser'],settings['pgpassword'],settings['pghost'],settings['pgport'],settings['pgdatabase'])
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()
    return session

session = return_session()

def user_exist(username):
    user = session.query(User).filter(User.username == username).first()
    if user:
        return True
    return False

def login(username,password):
    user = session.query(User).filter(User.username == username).first()
    if user.password == password:
        return True
    else:
        return False

def register(username,password):
    new_user = User(username=username, password=password)
    session.add(new_user)
    session.commit()
    print('Registered : ',username)