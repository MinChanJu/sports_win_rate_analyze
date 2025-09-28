import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
from tensorflow.keras.utils import to_categorical

# ----------------------------------------------------------------------
# 1. 효율성(EFF) 계산 함수 정의
# ----------------------------------------------------------------------
def calculate_eff(pts, reb, ast, stl, blk, fga, fgm, fta, ftm, to):
    """EFF = (PTS + REB + AST + STL + BLK) - ((FGA - FGM) + (FTA - FTM) + TO)"""
    positive_stats = pts + reb + ast + stl + blk
    negative_stats = (fga - fgm) + (fta - ftm) + to
    return positive_stats - negative_stats

# ----------------------------------------------------------------------
# 2. 가상 데이터 생성 (총 400경기, 22개 피처)
# ----------------------------------------------------------------------
np.random.seed(42)
num_samples = 400 # 총 400경기 데이터 생성
# 20개의 Raw 지표 (Home 10개, Away 10개)
# PTS(0), REB(1), AST(2), TO(3), BLK(4), STL(5), FTA(6), FTM(7), FGA(8), FGM(9)
raw_features = np.random.randint(5, 50, size=(num_samples, 20)) 
raw_features[:, [0, 10]] = np.random.randint(60, 120, size=(num_samples, 2)) # PTS는 60~120점

# Home/Away EFF 계산
home_eff = calculate_eff(
    raw_features[:, 0], raw_features[:, 1], raw_features[:, 2], raw_features[:, 5], 
    raw_features[:, 4], raw_features[:, 8], raw_features[:, 9], raw_features[:, 6], 
    raw_features[:, 7], raw_features[:, 3]
).reshape(-1, 1)

away_eff = calculate_eff(
    raw_features[:, 10], raw_features[:, 11], raw_features[:, 12], raw_features[:, 15],
    raw_features[:, 14], raw_features[:, 18], raw_features[:, 19], raw_features[:, 16],
    raw_features[:, 17], raw_features[:, 13]
).reshape(-1, 1)

# 최종 입력 데이터 X (Raw 20개 + EFF 2개 = 총 22개 피처)
X = np.hstack((raw_features, home_eff, away_eff))

# 승패 결과 (Home PTS > Away PTS 이면 승리(1))
y_raw = (X[:, 0] > X[:, 10]).astype(int) 
y = to_categorical(y_raw, num_classes=2) 

# ----------------------------------------------------------------------
# 3. 데이터 전처리 및 모델 분할 (300 Train / 100 Test)
# ----------------------------------------------------------------------
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

# 400경기 중 25% (100경기)를 테스트 데이터로 사용
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.25, random_state=42
)

# ----------------------------------------------------------------------
# 4. MLP 모델 정의 (총 22개 입력 노드)
# ----------------------------------------------------------------------
input_dim = X_train.shape[1] # 22
model = Sequential()
model.add(Dense(32, input_dim=input_dim, activation='relu')) 
model.add(Dense(16, activation='relu')) 
model.add(Dense(2, activation='softmax')) 

model.compile(optimizer='adam', 
              loss='categorical_crossentropy', 
              metrics=['accuracy'])

# ----------------------------------------------------------------------
# 5. 모델 학습 및 시각화
# ----------------------------------------------------------------------
history = model.fit(X_train, y_train, 
                    epochs=50, 
                    batch_size=16, 
                    verbose=0,
                    validation_data=(X_test, y_test))

# ----------------------------------------------------------------------
# 6. 최종 평가 및 새로운 데이터 예측 (일반적인 경기 상황)
# ----------------------------------------------------------------------
loss, accuracy = model.evaluate(X_test, y_test, verbose=0)

# 새로운 데이터 예측: Home Team이 근소하게 유리한 일반적인 경기 상황 시뮬레이션
new_game_raw = np.array([[105, 40, 22, 12, 4, 6, 6, 6, 35, 18, # Home Raw (약간 우세)
                          100, 38, 20, 14, 3, 4, 4, 4, 33, 16]]) # Away Raw (약간 열세)

# EFF 계산 및 피처 벡터 완성
home_eff_val = calculate_eff(*new_game_raw[0, :10])
away_eff_val = calculate_eff(*new_game_raw[0, 10:])
new_game_eff = np.array([[home_eff_val, away_eff_val]])
new_game_data = np.hstack((new_game_raw, new_game_eff))

# 스케일링 후 예측
new_game_scaled = scaler.transform(new_game_data)
predictions = model.predict(new_game_scaled, verbose=0)
win_prob = predictions[0][1] * 100 

print(f"학습 데이터 수: {X_train.shape[0]}경기")
print(f"검증 데이터 수: {X_test.shape[0]}경기")
print(f"\n검증 데이터 정확도 (Accuracy): {accuracy:.4f}")
print(f"시뮬레이션 승리 예측 확률 (Softmax): {win_prob:.2f}%")