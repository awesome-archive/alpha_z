# alpha_z
## 这是一个简易的微博系统🌴

## 0. Python3环境
#### 1). 创建一个Python3虚拟环境
#### 2). pip install -r requirements.txt

## 1. 创建MySQL数据库
```
mysql> create database alpha_z default charset utf8;
```

## 2. 配置参数
```
vim config.py
```

## 3. 创建数据库表
```
python models.py
```

## 4. 运行
```
python app.py
```