# MUSCLE ACTIVATION DATA ANALYSIS

Thorough data analysis for muscle activation using EMG recordings using an 8-channel Myo armband.
</br>

Each channel is responsible for recording the activation of different forearm muscles.
The recordings represent the following movements of the forearm:
- extension
- flexion
- pronation
- supination
- radial deviation
- ulnar deviation
- fist
- neutral position
</br>

Data was preprocessed by calculating **ARV (Average Rectified Value)** and **RMS (Root Mean Square) values, acting as features for further analysis**.
Afterwards, the data was subject to **dimension reduction using PCA (Principal Component Analysis)**, successfully minimizing data while still keeping the bulk of the information it originally contained.

### WORK IN PROGRESS...

Classification of forearm movements using a neural network in comparison with a selected classifier.
