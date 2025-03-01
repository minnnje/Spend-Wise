#!/usr/bin/env python
# coding: utf-8

# # 가계부 웹 대시보드


import pandas as pd
import streamlit as st
import plotly.express as px

def load_dataset(path):
    return pd.read_csv(path, encoding='cp949')

path = 'transactions.csv'
df = load_dataset(path)
df['Date'] = pd.to_datetime(df['Date'])
df.info()


# ## 사이드바 생성

# 초기 설정
transaction_types = df['Transaction_Types'].unique().tolist()

# 사이드바 구성
with st.sidebar:
    # 거래 유형 선택
    classification = st.selectbox(
        label=':pushpin: The type of transaction',
        options=transaction_types
    )
    
    # 선택된 거래 유형에 따른 데이터 필터링
    filtered_df_by_type = df[df['Transaction_Types'] == classification]

    # 해당 거래 유형에 맞는 카테고리 리스트 생성
    category_options = filtered_df_by_type['Category'].unique().tolist()
    
    # 카테고리 선택
    selected_categories = st.multiselect(
        ':pushpin: The category:',
        category_options,
        default=category_options[0] if category_options else None,  # 기본값 설정
        key='option_filter'
    )
    
    # 해당 거래 유형의 금액 범위 가져오기
    min_price = filtered_df_by_type['Price'].min() if not filtered_df_by_type.empty else 0
    max_price = filtered_df_by_type['Price'].max() if not filtered_df_by_type.empty else 0

    # 슬라이더 설정
    st.slider(
        ':pushpin: Set up the price range you want to see:',
        min_value=min_price,
        max_value=max_price,
        value=(min_price, max_price),
        step=50000,
        key='price_filter'
    )

    # 이상치 포함 여부
    include_outliers = st.checkbox(":eyes: Include outliers", value=True)

# 원본 데이터 복사
original_df = df.copy()

# 이상치 처리
if not include_outliers:
    # 원본 데이터를 기준으로 다시 필터링
    df = original_df[
        (original_df['Price'] >= original_df['Price'].quantile(0.1)) &
        (original_df['Price'] <= original_df['Price'].quantile(0.95))
    ]
else:
    # 이상치를 포함하려면 원본 데이터를 그대로 사용
    df = original_df.copy()

# 사용자 지정 필터 적용
df = df.loc[
    (df['Transaction_Types'] == classification) &  # 선택된 거래 유형
    (df['Category'].isin(st.session_state.get('option_filter', category_options))) &  # 선택된 카테고리
    (df['Price'] <= st.session_state.get('price_filter', [0, float('inf')])[1]) &  # 선택된 가격 상한
    (df['Price']>= st.session_state.get('price_filter', [0, float('inf')])[0])  # 선택된 가격 하한
]

# 필터링된 데이터 표시
st.dataframe(df)


# ## 대제목 생성


# 제목에 HTML과 CSS 스타일을 추가하여 줄 바꿈 방지
st.markdown('<h1 style="white-space: nowrap;">Spend Wisely! - Your Financial Journey</h1>', unsafe_allow_html=True)

st.write(
    '''
    Hello, welcome to your personalized dashboard!
    Take a look at your past transactions and explore them in a way that fits your needs. You'll uncover insights along the way.
    Sometimes, you might feel a sense of reflection, guilt, or even discover hidden treasures — or simply feel proud of your progress.
    What’s certain is that through this journey, you’ll definitely be a step ahead of where you were.
    '''  
)
st.divider()


# ## part1_box graph


st.subheader(
    "Summary Statistics of Transaction Analysis Using Boxplot",
)

col1, col2 = st.columns(2)
with col1 :
    st.write(
        '''
        "The price distribution statistics analyzed by category. How much do you usually spend in each category?"
        '''
    )
with col2 :
    fig1 = px.box(
        data_frame=df, x='Category', y='Price', width=300, height=400, points='all'
    )
    st.plotly_chart(fig1)
st.divider()
