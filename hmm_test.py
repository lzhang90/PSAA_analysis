import numpy as np
from hmmlearn import hmm
states = ["box 1", "box 2", "box3"]
n_states = len(states)

observations = ["red", "white"]
n_observations = len(observations)
model2 = hmm.MultinomialHMM(n_components=n_states, n_iter=20, tol=0.01)
X2=np.array([[0,1,2,3,4,5,6,7,8,9]]).reshape(1,-1)
model2.fit(X2)

print(model2.startprob_)
print(model2.transmat_)
print(model2.emissionprob_)
print(model2.score(X2))
# X3=np.array([0,0,0,1]).reshape(1, -1)
# model2.fit(X3)
# print(model2.startprob_)
# print(model2.transmat_)
# print(model2.emissionprob_)
# print(model2.score(X3))
# X4=np.array([1,0,1]).reshape(1, -1)
# model2.fit(X4)
# print(model2.startprob_)
# print(model2.transmat_)
# print(model2.emissionprob_)
# print(model2.score(X4))
