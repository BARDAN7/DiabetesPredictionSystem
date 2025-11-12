import numpy as np

# ---------- Gradient & Hessian for Logistic Loss ----------
def logistic_grad_hess(y_true, y_pred):
    pred_prob = 1 / (1 + np.exp(-y_pred))  # sigmoid
    g = pred_prob - y_true                 # gradient
    h = pred_prob * (1 - pred_prob)        # hessian
    return g, h

# ---------- Tree Node ----------
class TreeNode:
    def __init__(self, depth=0):
        self.depth = depth
        self.feature_index = None
        self.threshold = None
        self.left = None
        self.right = None
        self.value = None
        self.is_leaf = False

    def predict_row(self, x_row):
        if self.is_leaf:
            return self.value
        if x_row[self.feature_index] <= self.threshold:
            return self.left.predict_row(x_row)
        else:
            return self.right.predict_row(x_row)

# ---------- Single Tree ----------
class XGTree:
    def __init__(self, max_depth=3, min_samples_split=10, lambda_reg=1.0, gamma=0.0, min_gain=1e-6):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.lambda_reg = lambda_reg
        self.gamma = gamma
        self.min_gain = min_gain

    def fit(self, X, g, h):
        idx_all = np.arange(X.shape[0])
        self.root = self._build(X, idx_all, g, h, 0)

    def _build(self, X, idx, g, h, depth):
        node = TreeNode(depth)
        G, H = g[idx].sum(), h[idx].sum()
        node.value = -G / (H + self.lambda_reg)
        if depth >= self.max_depth or len(idx) <= self.min_samples_split:
            node.is_leaf = True
            return node

        best_gain, best_feat, best_thr = -np.inf, None, None
        for f in range(X.shape[1]):
            order = np.argsort(X[idx, f])
            Xf, gf, hf = X[idx, f][order], g[idx][order], h[idx][order]
            G_L, H_L = 0, 0
            for i in range(1, len(idx)):
                G_L += gf[i - 1]
                H_L += hf[i - 1]
                if Xf[i] == Xf[i - 1]:
                    continue
                G_R, H_R = G - G_L, H - H_L
                gain = 0.5 * ((G_L**2 / (H_L + self.lambda_reg)) +
                              (G_R**2 / (H_R + self.lambda_reg)) -
                              (G**2 / (H + self.lambda_reg))) - self.gamma
                if gain > best_gain:
                    best_gain, best_feat, best_thr = gain, f, (Xf[i] + Xf[i - 1]) / 2

        if best_gain <= self.min_gain or best_feat is None:
            node.is_leaf = True
            return node

        # ✅ FIXED INDEXING
        mask_left = X[idx, best_feat] <= best_thr
        mask_right = X[idx, best_feat] > best_thr
        left_idx = idx[mask_left]
        right_idx = idx[mask_right]

        node.feature_index, node.threshold = best_feat, best_thr
        node.left = self._build(X, left_idx, g, h, depth + 1)
        node.right = self._build(X, right_idx, g, h, depth + 1)
        return node

    def predict(self, X):
        return np.array([self.root.predict_row(row) for row in X])

# ---------- XGBoost Classifier ----------
class XGBoostClassifierManual:
    def __init__(self, n_estimators=100, learning_rate=0.3, max_depth=3,
                 min_samples_split=10, lambda_reg=1.0, gamma=0.0):
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.lambda_reg = lambda_reg
        self.gamma = gamma
        self.trees = []

    def fit(self, X, y):
        X, y = np.asarray(X), np.asarray(y)
        y_pred = np.zeros_like(y, dtype=float)
        for _ in range(self.n_estimators):
            g, h = logistic_grad_hess(y, y_pred)
            tree = XGTree(self.max_depth, self.min_samples_split, self.lambda_reg, self.gamma)
            tree.fit(X, g, h)
            update = tree.predict(X)
            y_pred += self.learning_rate * update
            self.trees.append(tree)

    def predict_proba(self, X):
        X = np.asarray(X)
        y_pred = np.zeros(X.shape[0], dtype=float)
        for t in self.trees:
            y_pred += self.learning_rate * t.predict(X)
        return 1 / (1 + np.exp(-y_pred))  # sigmoid

    def predict(self, X):
        return (self.predict_proba(X) >= 0.5).astype(int)
