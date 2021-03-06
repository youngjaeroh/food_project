# -*- coding: utf-8 -*-
"""test.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/17iYBheKtTnvMcLtX9O8vqYS-6dC1J08S
"""

import subprocess
import os
import re
import pandas as pd
import numpy as np

#경로에 있는 파일 출력
path = "./myfood/"
file_list = os.listdir(path)

#ngrok url 입력받기
url = input('url을 입력하세요 : ')

#음식 배열에서 숫자코드만 가져오기
p = re.compile('\d+')

#py ipynb 파일은 빼고, 서버로 보내서 분석결과 리스트로 반환
food_list = []
for i in file_list:
    if not (i.endswith('py') or i.endswith('ipynb')):
        print(f"\n{i} 분석중")
        i = path + i
        result = subprocess.check_output(f"curl -X POST -F file=@{i} {url}" , shell=True)
        result = p.findall(str(result))
        food_list.append(result)

#2차원배열 1차원배열로
food_list = sum(food_list, [])



#성별 입력받기
sex = input('성별을 입력하세요 (m  or f) : ')

#칼로리 불러오기
data = pd.read_csv('/content/drive/MyDrive/final_project/calorie/calorie.csv', encoding='cp949')

def show1(food_list):
  food_names = []
  food_calories = []
  food_na_list = []
  for i in food_list:
    food_dict = {'01011001' : '쌀밥', '12011008' : '김치(배추김치)', '04016001': '부대찌개', '01015013' : '카레라이스', '01015010' : '제육(돼지고기)'}
    food_name=food_dict[i]
    food_calorie=data[data['음식명']==food_name]['1인분칼로리(kcal)']
    food_na=data[data['음식명']==food_name]['나트륨(g)']
    food_names.append(food_name)
    food_calories.append(food_calorie.values[0])
    food_na_list.append(food_na.values[0])
    
  return food_names, food_calories, food_na_list


def recommend_food(food_name,cal,na,sex):
    data = pd.read_csv('/content/drive/MyDrive/final_project/calorie/calorie.csv', encoding='cp949')
    data = data[['음식명','1인분칼로리(kcal)', '나트륨(g)']]

    data = data[data['음식명'].apply(lambda x: True if x not in food_name else False)]
    
    next_meal_na = 0 #성인 기준 매끼 나트륨 섭취량
    next_meal_cal = 0 # 성인 기준 매끼 식사 칼로리
    
    all_calorie=0
    all_na = 0

    all_caloriell = sum(cal)
    all_na = sum(na)

    #남자일 경우
    if sex == 'm':
        next_meal_cal = round(2500/3 - (all_calorie - 2500/3),1)
    #여자일 경우
    else:
        next_meal_cal = round(2000/3 - (all_calorie - 2000/3),1)

    next_meal_na = round(2000/3 - (all_na - 2000/3),1)

    #다음 식사 칼로리 허용량이 0이거나 0에 근접한 경우
    if next_meal_cal <= 150:
        result = f'다음식사 칼로리가 {next_meal_cal}남았습니다.\n 추천할 수 있는 음식이 제한됩니다.'        
    else:
        #다음 식사할 수 있는 칼로리와 가장 비슷한 칼로리 5개 뽑기
        data['dis_cal'] = data['1인분칼로리(kcal)'].apply(lambda x : np.sqrt((x-next_meal_cal)**2)) #유클리디안 거리기준
        data['dis_na'] = data['나트륨(g)'].apply(lambda x : np.sqrt((x-next_meal_na)**2))

    temp = data.sort_values(by = 'dis_cal')[:5]
    result = temp.sort_values(by = 'dis_na')[:2]['음식명'][:5].values
    return result

print ("음식리스트: {}".format(file_list))
print("\n")
result1, result2,result3 = show1(food_list)
print(f'먹은 음식 : {result1}')
print(f'해당 칼로리 : {result2}')
print(f'해당 나트륨 : {result3}\n')

result3 = recommend_food(result1, result2,result3, sex)
print(f"추천 음식 : {result3}")