from sqlalchemy import create_engine,ForeignKey, Column, Integer, String, DateTime, Boolean, Float, Text
from sqlalchemy.orm import sessionmaker,relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists, create_database
from server_script.login_script.local_settings import postgresql as settings
import hashlib


Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(25), unique=True, nullable=False)
    password = Column(String(50 ),nullable=False)

class Contact(Base):
    __tablename__ = 'contact'

    id = Column(Integer, primary_key=True)
    username = Column(String(25), ForeignKey('users.username'), nullable=False)
    email = Column(String(50), nullable=False)
    lineid = Column(String(50), nullable=True)
    line_notif = Column(Boolean, nullable=False, default=False)

    user = relationship('User', backref='contact')

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

def login_db(username,password):
    user = session.query(User).filter(User.username == username).first()
    if user.password == password:
        return True
    else:
        return False

def signup_db(username,password):
    new_user = User(username=username, password=password)
    session.add(new_user)
    session.commit()
    print('Registered : ',username)

def contact_logic(username,email,lineid=None,line_notif=False):
    new_contact = Contact(username=username, email=email, lineid=lineid, line_notif=line_notif)
    # if username exist just change the email
    if session.query(Contact).filter(Contact.username == username).first():
        session.query(Contact).filter(Contact.username == username).update({'email':email,'lineid':lineid,'line_notif':line_notif})
        session.commit()
        print('Email updated : ',email)
        return
    else:
        session.add(new_contact)
        session.commit()
        print('Email added : ',email)

def check_contact(username):
    contact = session.query(Contact).filter(Contact.username == username).first()
    if contact:
        return dict(email=contact.email,lineid=contact.lineid,line_notif=contact.line_notif)
    return False
    
def hash_password(password):
    password = hashlib.sha256(password.encode()).hexdigest()   
    return password
