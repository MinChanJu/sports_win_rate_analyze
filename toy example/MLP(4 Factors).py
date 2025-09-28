import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import pandas as pd

# 1. 가상 데이터 생성 (Synthetic Data Generation)
# ====================================================================
# [Home PTS, Home REB, Home AST, Home TO, Away PTS, Away REB, Away AST, Away TO]
# 100개의 가상 경기 데이터셋을 생성합니다.
np.random.seed(42)
num_samples = 100
X = np.random.randint(60, 120, size=(num_samples, 8)) # 60점에서 120점 사이의 가상 데이터

# 승패 결과 (0: 패배, 1: 승리). 홈 팀 득점이 어웨이 팀 득점보다 높으면 승리(1)로 설정합니다.
y_raw = (X[:, 0] > X[:, 4]).astype(int) 

# Softmax 출력을 위해 결과를 원-핫 인코딩(One-Hot Encoding) 합니다.
# (예: 패배 -> [1, 0], 승리 -> [0, 1]로 가정)
from tensorflow.keras.utils import to_categorical
y = to_categorical(y_raw, num_classes=2) 


# 2. 데이터 전처리 (Preprocessing)
# ====================================================================
# Min-Max 스케일링을 사용하여 데이터 범위를 0과 1 사이로 정규화합니다. (신경망 학습 안정화)
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

# 학습 데이터와 테스트 데이터 분리 (70:30)
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.3, random_state=42
)

print(f"총 데이터 샘플 수: {num_samples}")
print(f"입력 피처 수: {X_train.shape[1]}") # 8
print("-" * 30)


# 3. MLP 모델 정의 (Multi-Layer Perceptron Definition)
# ====================================================================
# Sequential 모델 정의 (레이어를 순차적으로 쌓는 방식)
model = Sequential()

# 입력층 및 첫 번째 은닉층 (Hidden Layer 1)
# 8개 입력 노드 (Input Dim) -> 16개 은닉 노드 (ReLU 활성화 함수 사용)
model.add(Dense(16, input_dim=X_train.shape[1], activation='relu'))

# 두 번째 은닉층 (Hidden Layer 2)
# 16개 은닉 노드 -> 8개 은닉 노드 (ReLU 활성화 함수 사용)
model.add(Dense(8, activation='relu'))

# 출력층 (Output Layer)
# 8개 은닉 노드 -> 2개 출력 노드 (Softmax 활성화 함수 사용: 승리/패배 확률)
model.add(Dense(2, activation='softmax'))

# 모델 구조 요약
model.summary()
print("-" * 30)


# 4. 모델 컴파일 및 학습 (Compile and Training)
# ====================================================================
# 모델 컴파일 (최적화 함수, 손실 함수, 평가 지표 설정)
# 이진 분류 문제이지만 Softmax와 원-핫 인코딩을 사용했으므로 'categorical_crossentropy' 사용
model.compile(optimizer='adam', 
              loss='categorical_crossentropy', 
              metrics=['accuracy'])

# 모델 학습 (Training)
# epochs: 전체 데이터셋을 반복 학습할 횟수
history = model.fit(X_train, y_train, 
                    epochs=20, 
                    batch_size=16, 
                    verbose=0, # 학습 과정을 출력하지 않음
                    validation_data=(X_test, y_test))

print("모델 학습 완료!")
print("-" * 30)


# 5. 모델 평가 및 예측 (Evaluation and Prediction)
# ====================================================================
loss, accuracy = model.evaluate(X_test, y_test, verbose=0)
print(f"테스트 데이터 정확도 (Accuracy): {accuracy:.4f}")

# 새로운 가상 데이터에 대한 예측 (예: 8개의 피처)
new_game_data = np.array([[115, 45, 25, 10, 90, 35, 18, 15]]) # Home Team이 유리한 가상 데이터
new_game_scaled = scaler.transform(new_game_data)

predictions = model.predict(new_game_scaled)
win_prob = predictions[0][1] * 100 

print(f"\n새로운 경기의 승리 예측 확률 (Softmax): {win_prob:.2f}%")