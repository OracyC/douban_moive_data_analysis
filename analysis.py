from bs4 import BeautifulSoup
import re
import urllib.request,urllib.error
import xlwt

# main
def main():
    baseurl = "https://movie.douban.com/top250?start="
    datalist = getData(baseurl)
    savepath = ".\\DoubanTop250.xls"
    saveData(datalist,savepath)

# movie url
findLink = re.compile(r'<a href="(.*?)">')         # create re rules
# movie poster url
findImgSrc = re.compile(r'<img.*src="(.*?)"',re.S) 
# movie name
findTitle = re.compile(r'<span class="title">(.*)</span>')
# movie rate
findRating = re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')
# movie rate count
findJudge = re.compile(r'<span>(\d*)人评价</span>')
# movie description
findInq = re.compile(r'<span class="inq">(.*?)</span>')
# movie information
findBd = re.compile(r'<p class="">(.*?)</p>',re.S)

def getData(baseurl):
    datalist = []
    for i in range(0,10):
        url = baseurl + str(i*25)
        html = askURL(url)
        soup = BeautifulSoup(html,"html.parser")
        for item in soup.find_all('div',class_="item"):
            data = []
            item = str(item)
            # movie url
            link = re.findall(findLink,item)[0]
            data.append(link)
            # movie poster url
            imgSrc = re.findall(findImgSrc,item)[0]
            data.append(imgSrc)
            # movie name
            title = re.findall(findTitle,item)
            if (len(title) == 2):
                cntitle = title[0]
                data.append(cntitle)
                otitle = title[1].replace("/","")
                data.append(otitle)
            else:
                data.append(title[0])
                data.append(" ")
            # movie rate
            rating = re.findall(findRating,item)[0]
            data.append(rating)
            # movie rate count
            judge = re.findall(findJudge,item)[0]
            data.append(judge)
            # movie description
            inq = re.findall(findInq,item)
            if len(inq) != 0:
                inq = inq[0].replace("。","")
                data.append(inq)
            else:
                data.append(" ")
            # movie info
            bd = re.findall(findBd,item)[0]
            data.append(bd.strip())

            datalist.append(data)
    print(datalist)
    return datalist

def askURL(url):
    head = {
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36 Edg/84.0.522.61"
    }
    Urlrequest = urllib.request.Request(url,headers=head)
    html = ""
    try:
        Urlresponse = urllib.request.urlopen(Urlrequest)
        html = Urlresponse.read().decode("utf-8")
    except urllib.error.URLError as e:
        if hasattr(e,"code"):
            print(e.code)
        if hasattr(e,"reason"):
            print(e.reason)
    return html

def saveData(datalist,savepath):
    book = xlwt.Workbook(encoding="utf-8",style_compression=0)
    sheet = book.add_sheet("DoubanTop250",cell_overwrite_ok=True)
    col = ("movie_url","movie_poster_url","movie_name[zh]","movie_name[en]","movie_rate","movie_rate_count","movie_description","movie_info")
    for i in range(0,8):
        sheet.write(0,i,col[i])
    for i in range(0,250):
        print("Writing the %d line of info"%(i+1))
        data = datalist[i]
        for j in range(0,8):
            sheet.write(i+1,j,data[j])

    book.save(savepath)
if __name__ == "__main__":
    main()
    print("Crawler done！")
    
    
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

data = pd.read_excel('DoubanTop250.xls')

temp1 = data['movie_info'].str.split('导演: ',expand=True)[1]
data['movie_director'] = temp1.str.split('主演: ',expand=True)[0]
temp2 = temp1.str.split('主演: ',expand=True)[1]
data['movie_date'] = temp2.str.extract('(\d+)')
temp3 = temp2.str.split('<br/>',expand=True)[1]
data['movie_language'] = temp3.str.split('/',expand=True)[1]
data['movie_type'] = temp3.str.split('/',expand=True)[2]

print(data[data[['movie_date']].isnull().T.any()][['movie_date']])

#manually update null value
data['movie_date'][24] = '2011'
data['movie_date'][56] = '1999'
data['movie_date'][58] = '2006'
data['movie_date'][81] = '2004'
data['movie_date'][124] = '2010'
data['movie_date'][151] = '2002'
data['movie_date'][160] = '2013'
data['movie_date'][179] = '2015'
data['movie_date'][185] = '2002'
data['movie_date'][203] = '2010'
data['movie_date'][211] = '2009'

data.head()
data.describe()
data.iloc[:,2:].describe(include=['O'])
data.to_excel('DoubanTop250_new.xls',index = False)
from pylab import mpl

mpl.rcParams['font.sans-serif'] = ['FangSong']
mpl.rcParams['axes.unicode_minus'] = False
font = r'C:\Windows\Fonts\simhei.ttf'
wordcloud_genres = WordCloud(max_font_size=80, max_words=100, font_path=font, background_color="white", collocations=False).generate(data['movie_type'].to_string())
plt.figure(figsize = (8, 6))
plt.imshow(wordcloud_genres, interpolation="bilinear")
plt.title("Top Genres")
plt.axis("off")
plt.show()
wordcloud_genres = WordCloud(max_font_size=80, max_words=100, font_path=font, background_color="white", collocations=False).generate(data['movie_language'].to_string())
plt.figure(figsize = (8, 6))
plt.imshow(wordcloud_genres, interpolation="bilinear")
plt.title("Top Language")
plt.axis("off")
plt.show()

plt.figure(figsize=(16, 8))
plt.subplot(1, 2, 1)
plt.scatter(data['movie_date'].astype(int), data['movie_rate'])
plt.title('电影发布时间与评分散点图');
plt.subplot(1, 2, 2)
plt.scatter(data['movie_rate_count'], data['movie_rate'])
plt.title('电影评价人数与评分散点图');


new_features = ['movie_rate', 'movie_rate_count', 'movie_date']
train = data[new_features]

dummies1 = data['movie_type'].str.get_dummies(sep=' ')
train = pd.concat([train, dummies1], axis=1) 

dummies2 = data['movie_language'].str.get_dummies(sep=' ')
train = pd.concat([train, dummies2], axis=1) 

from sklearn.model_selection  import train_test_split

y = train.movie_rate

X = train.drop(columns=['movie_rate'])

X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.7, test_size=0.3, random_state=0)

print(X_train.shape, X_test.shape, y_train.shape, y_test.shape)

import math

def rmse(x,y): return math.sqrt(((x-y)**2).mean())

# print_score function depending on the evaluation metric: rmse
def print_score(m):
    res = ['rmse of train: ',rmse(m.predict(X_train), y_train), 'rmse of validation: ', rmse(m.predict(X_test), y_test),
                'r2 of train: ', m.score(X_train, y_train), 'r2 of validation: ', m.score(X_test, y_test)]
    if hasattr(m, 'oob_score_'): res.append('oob Score: '+str(m.oob_score_))
    print(res)
    
#feature importance to dataframe
def feature_importance(m, df):
    return pd.DataFrame({'字段':df.columns, '重要性':m.feature_importances_}
                       ).sort_values('重要性', ascending=True)
# function to plot feature importance
def plot_fi(fi): return fi.plot('字段','重要性','barh', figsize = (10,8), legend=False)

train_null = train.copy()
train_null['movie_rate'] = train_null['movie_rate'].mean()
y_null = train_null['movie_rate']
rmse_null = rmse(y, y_null)
print("The rmse of the null model is",rmse_null)

from sklearn.ensemble import RandomForestRegressor

rf = RandomForestRegressor(n_estimators=999, min_samples_leaf=5, max_features=0.5, n_jobs=-1, oob_score=True, random_state=99)
rf.fit(X_train, y_train)

print_score(rf)

fi = feature_importance(rf, X_train)
fi[-10:]

plot_fi(fi[-8:])

import lightgbm as lgb

lgbm = lgb.LGBMRegressor(objective='regression',num_leaves=8,
                              learning_rate=0.05, n_estimators=650,
                              max_bin=58, bagging_fraction=0.80,
                              bagging_freq=5, feature_fraction=0.2319,
                              feature_fraction_seed=9, bagging_seed=9,
                              min_data_in_leaf=7, min_sum_hessian_in_leaf=11)
                              
X_train['movie_date'] = X_train['movie_date'].astype('int')
X_test['movie_date'] = X_test['movie_date'].astype('int')
lgbm.fit(X_train, y_train, eval_set=[(X_test, y_test)],eval_metric='l1',early_stopping_rounds=10)
print_score(lgbm)

booster = lgbm.booster_
importance = booster.feature_importance(importance_type='split')
feature_name = booster.feature_name()
feature_importance = pd.DataFrame({'字段':feature_name,'重要性':importance} ).sort_values('重要性', ascending=True)
feature_importance[-15:]

plot_fi(feature_importance[-8:])