from sqlalchemy import ForeignKey
from sqlalchemy import Text
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Sequence
from sqlalchemy import func
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from config import DB

engine = create_engine('mysql+mysqldb://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}?charset=utf8'.format(
    USERNAME=DB['USER'],
    PASSWORD=DB['PASSWORD'],
    HOST=DB['HOST'],
    PORT=DB['PORT'],
    DB_NAME=DB['DB_NAME'],
), convert_unicode=True, echo=False)

DBSession = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = DBSession.query_property()

Base = declarative_base()

def init_db(engine):
  Base.metadata.create_all(bind=engine)


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    username = Column(String(128))
    email = Column(String(128))
    password = Column(String(128))
    is_admin = Column(Boolean())
    is_activated = Column(Boolean())
    profile = relationship("UserProfile", uselist=False, back_populates="user")
    article = relationship("Article", uselist=False, back_populates="author")
    comment = relationship("Comment", uselist=False, back_populates="author")
    like = relationship("Like", uselist=False, back_populates="user")
    c_like = relationship("CLike", uselist=False, back_populates="user")
    last_login = Column(DateTime(timezone=True), default=func.now())
    create_at = Column(DateTime(timezone=True), default=func.now())
    update_at = Column(DateTime(timezone=True), default=func.now())


    def __repr__(self):
        return "<User(username='%s', email='%s', password='%s')>" % (
                                self.username, self.email, self.password)


class UserProfile(Base):
    __tablename__ = 'profile'
    id = Column(Integer, Sequence('profile_id_seq'), primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User", back_populates="profile")
    age = Column(String(128))
    gender = Column(String(128))
    mobile = Column(String(128))
    avatar = Column(String(128))
    create_at = Column(DateTime(timezone=True), default=func.now())
    update_at = Column(DateTime(timezone=True), default=func.now())


class Article(Base):
    __tablename__ = 'article'
    id = Column(Integer, Sequence('article_id_seq'), primary_key=True)
    author_id = Column(Integer, ForeignKey('user.id'))
    author = relationship("User", back_populates="article")
    comment = relationship("Comment", uselist=False, back_populates="article")
    like = relationship("Like", uselist=False, back_populates="article")
    topic_id = Column(Integer, ForeignKey('topic.id'))
    topic = relationship("Topic", back_populates="article")
    content = Column(Text())
    image = Column(String(128))
    comment_count = Column(Integer(), default=0)
    like_count = Column(Integer(), default=0)
    create_at = Column(DateTime(timezone=True), default=func.now())
    update_at = Column(DateTime(timezone=True), default=func.now())


    def __repr__(self):
        return "<Article(id='%s')>" % self.id


class Like(Base):
    __tablename__ = 'like'
    id = Column(Integer, Sequence('like_id_seq'), primary_key=True)
    article_id = Column(Integer, ForeignKey('article.id'))
    article = relationship("Article", back_populates="like")
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User", back_populates="like")
    create_at = Column(DateTime(timezone=True), default=func.now())


class CLike(Base):
    __tablename__ = 'c_like'
    id = Column(Integer, Sequence('c_like_id_seq'), primary_key=True)
    comment_id = Column(Integer, ForeignKey('comment.id'))
    comment = relationship("Comment", back_populates="c_like")
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User", back_populates="c_like")
    create_at = Column(DateTime(timezone=True), default=func.now())


class Comment(Base):
    __tablename__ = 'comment'
    id = Column(Integer, Sequence('comment_id_seq'), primary_key=True)
    article_id = Column(Integer, ForeignKey('article.id'))
    article = relationship("Article", back_populates="comment")
    author_id = Column(Integer, ForeignKey('user.id'))
    author = relationship("User", back_populates="comment")
    c_like = relationship("CLike", back_populates="comment")
    content = Column(Text())
    like_count = Column(Integer(), default=0)
    create_at = Column(DateTime(timezone=True), default=func.now())


class Topic(Base):
    __tablename__ = 'topic'
    id = Column(Integer, Sequence('topic_id_seq'), primary_key=True)
    name = Column(String(128))
    article = relationship("Article", uselist=False, back_populates="topic")
    create_at = Column(DateTime(timezone=True), default=func.now())





if __name__ == '__main__':
    init_db(engine)
