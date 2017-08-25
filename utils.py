import hashlib
import random
import string

import time

from sqlalchemy import desc

from config import MD5_SALT
from models import User, DBSession, UserProfile, Article, Comment, Like, CLike
from tools.identicon import render_identicon
session = DBSession()

def hash_password(text):
    text_encoded = (text+MD5_SALT).encode('utf-8')
    md5_code = hashlib.md5(text_encoded).hexdigest()
    return md5_code


def valid_email(email):
    pass


def gen_random_avatar():
    code = ''.join(random.choice(string.digits) for x in range(20))
    img = render_identicon(code, 32)
    fname = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(6)) + str(int(time.time() * 1000)) + '.png'
    img.save("static/media/avatar/" + fname)
    return fname


def create_user(info):
    try:
        session.add(User(username=info["username"], email=info["email"], password=hash_password(info["password"])))
        session.commit()
        user = session.query(User).filter_by(username=info["username"]).first()
        avatar = gen_random_avatar()
        session.add(UserProfile(user=user, avatar=avatar))
        session.commit()
        return user
    except Exception as e:
        print(e)
        return None


def change_avatar(p_id=None, avatar=None):
    try:
        res = {"success": False, "msg": ""}
        session = DBSession()
        user_profile = session.query(UserProfile).filter_by(id=p_id).first()
        user_profile.avatar = avatar
        session.commit()
        res["success"] = True
        return res
    except Exception as e:
        res["msg"] = str(e)
        return res



def authenticate(email=None, password=None):
    res = {"success": False, "msg": "", "user_id": None}
    user = session.query(User).filter_by(email=email).first()
    if not user:
        res["msg"] = "用户名不存在"
        return res
    if user.password != hash_password(password):
        res["msg"] = "用户名与密码不符"
        return res
    res["success"] = True
    res["user_id"] = user.id
    res["msg"] = "认证成功"
    return res


def get_user(u_id=None):
    user = session.query(User).filter_by(id=u_id).first()
    return user



def create_article(info):
    try:
        res = {"success": False, "msg": ""}
        session.add(Article(content=info["content"], author_id=info["author_id"], image=info["image"]))
        session.commit()
        session.close()
        res["success"] = True
        return res
    except Exception as e:
        res["msg"] = str(e)
        return res


def get_articles(u_id=None):
    if not u_id:
        articles = session.query(Article).order_by(desc(Article.create_at)).all()
    else:
        articles = session.query(Article).order_by(desc(Article.create_at)).filter_by(author_id=u_id).all()
    return articles


def get_article(a_id=None):
    article = session.query(Article).filter_by(id=a_id).first()
    return article


def add_like_count(a_id=None, u_id=None):
    try:
        like = session.query(Like).filter_by(article_id=a_id, user_id=u_id).first()
        if like:return False
        session.add(Like(article_id=a_id, user_id=u_id))
        session.commit()
        article = session.query(Article).filter_by(id=a_id).first()
        article.like_count += 1
        session.commit()
        return True
    except:
        return False


def add_comment_like_count(c_id=None, u_id=None):
    try:
        c_like = session.query(CLike).filter_by(comment_id=c_id, user_id=u_id).first()
        if c_like:return False
        session.add(CLike(comment_id=c_id, user_id=u_id))
        session.commit()
        comment = session.query(Comment).filter_by(id=c_id).first()
        comment.like_count += 1
        session.commit()
        return True
    except Exception as e:
        print(str(e))
        return False



def create_comment(**kwargs):
    try:
        res = {"success": False, "msg": ""}
        session.add(Comment(content=kwargs["content"], author_id=kwargs["author_id"], article_id=kwargs["article_id"]))
        session.commit()
        article = session.query(Article).filter_by(id=kwargs["article_id"]).first()
        article.comment_count += 1
        session.commit()
        res["success"] = True
        return res
    except Exception as e:
        res["msg"] = str(e)
        return res


def get_comments(a_id):
    comments = session.query(Comment).filter_by(article_id=a_id).order_by(desc(Comment.create_at)).all()
    return comments