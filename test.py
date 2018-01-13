from app import db
from app.models import User, Post
import datetime

u = User(nickname='john', email='john@email.com')
db.session.add(u)
db.session.commit()

u = User(nickname='susan', email='susan@email.com')
db.session.add(u)
db.session.commit()

users = User.query.all()
print('Users')
print(users)

print('For loop users')
for u in users:
    print(u.id, u.nickname)


print('Get john')
u = User.query.get(1)
print(u)

print('Making post')
u = User.query.get(1)
p = Post(body='my first post!', timestamp=datetime.datetime.utcnow(), author=u)
db.session.add(p)
db.session.commit()

print('Posts de john')
u = User.query.get(1)
posts = u.posts.all()
print(posts)

print('Obtain author for each post')
for p in posts:
    print(p.id, p.author.nickname, p.body)

print('User with no posts')
u = User.query.get(2)
print(u)
print(u.posts.all())

print('User in reverse alphabetical order')
print(User.query.order_by('nickname desc').all())

print('Erasing users database')
users = User.query.all()
for u in users:
    db.session.delete(u)

posts = Post.query.all()
for post in posts:
    db.session.delete(post)

db.session.commit()
