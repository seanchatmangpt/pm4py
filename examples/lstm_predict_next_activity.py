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
from pm4py.algo.transformation.log_to_target.variants import next_activity
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, TimeDistributed


def execute_script():
    log = pm4py.read_xes("../tests/input_data/running-example.xes", return_legacy_log_object=True)

    data, feature_names = event_based.apply(log)
    target, classes = next_activity.apply(log, parameters={"enable_padding": True})
    target = np.array(target)

    model = Sequential()
    model.add(LSTM(50, input_shape=(data.shape[1], data.shape[2]), return_sequences=True))
    model.add(TimeDistributed(Dense(len(classes), activation='softmax')))

    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    model.summary()

    # train the model
    model.fit(data, target, epochs=100)

    # test the model on an event log (in this case the same)

    # re-extract the features
    data, feature_names = event_based.apply(log, parameters={"feature_names": feature_names})

    # perform the prediction
    predictions = model.predict(data)
    predictions = [[classes[np.argmax(y)] for y in x] for x in predictions]

    print(predictions)


if __name__ == "__main__":
    execute_script()
