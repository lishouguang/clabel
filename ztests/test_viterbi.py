# coding: utf-8

import unittest


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_viterbi(self):
        self.assertTrue(True)

        pass


def viterbi(self, obs_seq):
    """
    Returns
    -------
    V : numpy.ndarray
        V [s][t] = Maximum probability of an observation sequence ending
                   at time 't' with final state 's'
    prev : numpy.ndarray
        Contains a pointer to the previous state at t-1 that maximizes
        V[state][t]
    """
    N = self.A.shape[0]
    T = len(obs_seq)
    prev = np.zeros((T - 1, N), dtype=int)

    # DP matrix containing max likelihood of state at a given time
    V = np.zeros((N, T))
    V[:, 0] = self.pi * self.B[:, obs_seq[0]]

    for t in range(1, T):
        for n in range(N):
            seq_probs = V[:, t - 1] * self.A[:, n] * self.B[n, obs_seq[t]]
            prev[t - 1, n] = np.argmax(seq_probs)
            V[n, t] = np.max(seq_probs)

    return V, prev


def viterbi_segment(text, P):
    """Find the best segmentation of the string of characters, given the UnigramTextModel P."""
    # best[i] = best probability for text[0:i]
    # words[i] = best word ending at position i
    n = len(text)
    words = [''] + list(text)
    best = [1.0] + [0.0] * n

    # Fill in the vectors best, words via dynamic programming
    for i in range(n + 1):
        for j in range(0, i):
            w = text[j:i]
            if P[w] * best[i - len(w)] >= best[i]:
                best[i] = P[w] * best[i - len(w)]
                words[i] = w

    # Now recover the sequence of best words
    sequence = [];
    i = len(words) - 1
    while i > 0:
        sequence[0:0] = [words[i]]
        i = i - len(words[i])

    # Return sequence of best words and overall probability
    return sequence, best[-1]


if __name__ == '__main__':
    unittest.main()
