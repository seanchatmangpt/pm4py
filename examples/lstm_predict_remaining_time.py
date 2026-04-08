"""
PM4Py – A Process Mining Library for Python
Copyright (C) 2024 Process Intelligence Solutions

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Website: https://processintelligence.solutions
Contact: info@processintelligence.solutions
"""

import numpy as np
import pm4py
from pm4py.algo.transformation.log_to_features.variants import event_based
from pm4py.algo.transformation.log_to_target.variants import remaining_time
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.optimizers import Adam



def execute_script():
    log = pm4py.read_xes("../tests/input_data/running-example.xes", return_legacy_log_object=True)
    max_len_log = max([len(x) for x in log])

    data, feature_names = event_based.apply(log)
    target, classes = remaining_time.apply(log, parameters={"enable_padding": True})
    target = np.array(target)
    scaler = MinMaxScaler(feature_range=(-1, 1))
    # Reshape for scaling
    target_reshaped = target.reshape(-1, 1)
    target_scaled = scaler.fit_transform(target_reshaped)
    # Reshape back to original shape
    target_scaled = target_scaled.reshape(-1, max_len_log)

    model = Sequential()
    model.add(LSTM(50, input_shape=(data.shape[1], data.shape[2]), return_sequences=True))  # Adjust the input shape as necessary
    model.add(Dense(1, activation='linear'))

    model.compile(optimizer=Adam(), loss='mean_squared_error', metrics=['mae'])

    model.summary()

    # train the model
    history = model.fit(data, target_scaled, batch_size=32, epochs=100, validation_split=0.2)

    # test the model on an event log (in this case the same)

    # re-extract the features
    test_log = log
    data, feature_names = event_based.apply(test_log, parameters={"feature_names": feature_names})

    # Make predictions
    predictions_scaled = model.predict(data)
    print(predictions_scaled)
    # Ensuring prediction values are within range
    predictions_clipped = np.clip(predictions_scaled, -1, 1)
    # Reshape predictions for inverse transformation
    predictions_scaled_reshaped = predictions_clipped.reshape(-1, 1)
    # Inverse transform to original scale
    predictions_original = scaler.inverse_transform(predictions_scaled_reshaped)
    # Reshape back to original predictions shape
    predictions_original = predictions_original.reshape(-1, max_len_log)

    # final output:
    print(predictions_original)


if __name__ == "__main__":
    execute_script()
